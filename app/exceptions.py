"""Custom exceptions for the application."""
from typing import Optional
class NotionRAGError(Exception):
    """Base exception for Notion RAG bot."""
    pass
class ConfigurationError(NotionRAGError):
    """Configuration-related errors."""
    pass
class NotionAPIError(NotionRAGError):
    """Notion API related errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code
class OpenAIError(NotionRAGError):
    """OpenAI API related errors."""
    def __init__(self, message: str, error_type: Optional[str] = None):
        super().__init__(message)
        self.error_type = error_type
class DatabaseError(NotionRAGError):
    """Database related errors."""
    pass
class RetrievalError(NotionRAGError):
    """Document retrieval related errors."""
    pass
class TelegramError(NotionRAGError):
    """Telegram bot related errors."""
    pass
