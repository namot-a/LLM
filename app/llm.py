"""LLM service with improved prompt engineering and error handling."""
import time
from typing import List, Dict, Optional
from openai import AsyncOpenAI, RateLimitError, APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import os
from .config import settings
from .logger import get_logger
from .exceptions import OpenAIError

logger = get_logger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)

# Enhanced system prompt for better responses
SYSTEM_PROMPT = """Ты корпоративный ассистент, который отвечает на вопросы сотрудников на основе регламентов и документации компании.

ПРАВИЛА ОТВЕТА:
1. Отвечай ТОЛЬКО на основе предоставленного контекста из регламентов
2. Если ответа в контексте нет, честно скажи: "Я не нашел этого в регламентах. Попробуйте уточнить формулировку вопроса или обратитесь к @anton_huntit."
3. Пиши кратко, структурированно и по делу
4. Если есть различия по ролям/исключения — обязательно укажи
5. Используй форматирование Markdown для структурирования ответа
6. Если в контексте есть несколько вариантов ответа — перечисли их все
7. Всегда указывай на источники информации

СТИЛЬ ОТВЕТА:
- Используй профессиональный, но дружелюбный тон
- Структурируй ответ с помощью заголовков и списков
- Выделяй важную информацию жирным шрифтом
- Если нужно, используй эмодзи для лучшего восприятия (но умеренно)"""


def build_context_snippets(chunks: List[Dict]) -> str:
    """
    Build context snippets from retrieved chunks.
    
    Args:
        chunks: List of chunk dictionaries
        
    Returns:
        Formatted context string
    """
    if not chunks:
        return "Контекст не найден."
    
    pieces = []
    total_chars = 0
    
    for i, chunk in enumerate(chunks, 1):
        # Build header with source information
        header = f"## Источник {i}: {chunk['title']}"
        if chunk.get('heading_path'):
            header += f" — {chunk['heading_path']}"
        
        header += f"\n**Ссылка:** {chunk['url']}\n"
        
        # Add content
        content = chunk['content'].strip()
        
        # Add similarity score for debugging (in development)
        if settings.log_level == "DEBUG":
            similarity = chunk.get('cosine_similarity', 0)
            header += f"**Релевантность:** {similarity:.2f}\n"
        
        block = f"{header}\n{content}\n\n---\n"
        
        # Check if adding this block would exceed the limit
        if total_chars + len(block) > settings.max_context_chars:
            logger.warning("Context truncated due to size limit", 
                         current_size=total_chars, 
                         max_size=settings.max_context_chars)
            break
        
        pieces.append(block)
        total_chars += len(block)
    
    context = "\n".join(pieces)
    logger.info("Context built", chunks_used=len(pieces), total_chars=total_chars)
    return context


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitError, APIError)),
    reraise=True
)
async def answer_with_context(question: str, chunks: List[Dict]) -> Dict:
    """
    Generate answer using LLM with context from retrieved chunks.
    
    Args:
        question: User question
        chunks: Retrieved document chunks
        
    Returns:
        Dictionary with answer and metadata
        
    Raises:
        OpenAIError: If LLM generation fails
    """
    start_time = time.time()
    
    try:
        logger.info("Generating answer", question=question[:100], chunks_count=len(chunks))
        
        # Build context from chunks
        context = build_context_snippets(chunks)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user", 
                "content": f"""Вопрос: {question}

Контекст из регламентов:
{context}

Ответ:"""
            }
        ]
        
        # Generate response
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=messages,
            temperature=0.1,  # Low temperature for consistent, factual responses
            max_tokens=1000,  # Reasonable limit for responses
            top_p=0.9
        )
        
        choice = response.choices[0].message
        usage = response.usage
        
        processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        result = {
            "answer": choice.content.strip(),
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
            "model": settings.openai_chat_model,
            "processing_time_ms": processing_time
        }
        
        logger.info("Answer generated", 
                   tokens_used=usage.total_tokens, 
                   processing_time_ms=processing_time)
        
        return result
        
    except RateLimitError as e:
        logger.error("Rate limit exceeded for LLM", error=str(e))
        raise OpenAIError(f"Rate limit exceeded: {e}", "rate_limit")
    except APIError as e:
        logger.error("OpenAI API error for LLM", error=str(e), status_code=getattr(e, 'status_code', None))
        raise OpenAIError(f"OpenAI API error: {e}", "api_error")
    except Exception as e:
        logger.error("Unexpected error generating answer", error=str(e))
        raise OpenAIError(f"Unexpected error: {e}", "unknown")


def calculate_cost(prompt_tokens: int, completion_tokens: int) -> Optional[float]:
    """
    Calculate cost based on token usage.
    
    Args:
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        
    Returns:
        Cost in USD or None if pricing not configured
    """
    if not settings.price_prompt_per_1k and not settings.price_completion_per_1k:
        return None
    
    prompt_cost = (prompt_tokens / 1000.0) * settings.price_prompt_per_1k
    completion_cost = (completion_tokens / 1000.0) * settings.price_completion_per_1k
    
    return round(prompt_cost + completion_cost, 4)


async def generate_summary(text: str, max_length: int = 200) -> str:
    """
    Generate a summary of text using LLM.
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary
        
    Returns:
        Generated summary
    """
    try:
        messages = [
            {
                "role": "system", 
                "content": f"Создай краткое резюме текста на русском языке (максимум {max_length} символов)."
            },
            {"role": "user", "content": text}
        ]
        
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=messages,
            temperature=0.3,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error("Error generating summary", error=str(e))
        return text[:max_length] + "..." if len(text) > max_length else text
