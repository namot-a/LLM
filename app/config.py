"""Configuration management with Pydantic settings."""
import os
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Telegram
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    allowed_telegram_user_ids: str = Field(default="", env="ALLOWED_TELEGRAM_USER_IDS")
    webhook_secret_path: str = Field(..., env="WEBHOOK_SECRET_PATH")
    
    # Notion
    notion_token: str = Field(..., env="NOTION_TOKEN")
    notion_database_ids: str = Field(..., env="NOTION_DATABASE_IDS")
    
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_chat_model: str = Field(default="gpt-4o-mini", env="OPENAI_CHAT_MODEL")
    openai_embed_model: str = Field(default="text-embedding-3-small", env="OPENAI_EMBED_MODEL")
    embedding_dim: int = Field(default=1536, env="EMBEDDING_DIM")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Retrieval settings
    top_k: int = Field(default=6, env="TOP_K", ge=1, le=20)
    similarity_threshold: float = Field(default=0.25, env="SIMILARITY_THRESHOLD", ge=0.0, le=1.0)
    max_context_chars: int = Field(default=12000, env="MAX_CONTEXT_CHARS", ge=1000, le=50000)
    
    # Cost tracking
    price_prompt_per_1k: float = Field(default=0.005, env="PRICE_PROMPT_PER_1K", ge=0)
    price_completion_per_1k: float = Field(default=0.015, env="PRICE_COMPLETION_PER_1K", ge=0)
    
    # API settings
    api_url: str = Field(default="http://localhost:8000", env="API_URL")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT", ge=1, le=65535)
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    def get_allowed_user_ids(self) -> List[int]:
        """Get allowed user IDs as a list (fallback if database is unavailable)."""
        if not self.allowed_telegram_user_ids:
            return []
        return [int(x.strip()) for x in self.allowed_telegram_user_ids.split(",") if x.strip()]
    
    def get_database_ids(self) -> List[str]:
        """Get database IDs as a list."""
        return [x.strip() for x in self.notion_database_ids.split(",") if x.strip()]
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
