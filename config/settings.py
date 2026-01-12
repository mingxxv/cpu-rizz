"""
Simple configuration management following Single Responsibility Principle
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    """Application settings"""

    api_key: str
    model: str = "Meta-Llama-3.1-8B-Instruct"
    temperature: float = 0.7
    max_tokens: int = 1000
    google_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None
    max_retries: int = 5
    initial_retry_delay: float = 1.0
    inter_call_delay: float = 0.5

    @classmethod
    def from_env(cls) -> "Settings":
        """
        Load settings from environment variables

        Returns:
            Settings instance with values from environment
        """
        api_key = os.getenv("SAMBANOVA_API_KEY")
        if not api_key:
            raise ValueError("SAMBANOVA_API_KEY environment variable must be set")

        google_api_key = os.getenv("GOOGLE_API_KEY")
        google_cse_id = os.getenv("GOOGLE_CSE_ID")

        if not google_api_key or not google_cse_id:
            raise ValueError("GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables must be set")

        return cls(
            api_key=api_key,
            model=os.getenv("MODEL", "Meta-Llama-3.1-8B-Instruct"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS", "1000")),
            google_api_key=google_api_key,
            google_cse_id=google_cse_id,
            max_retries=int(os.getenv("MAX_RETRIES", "5")),
            initial_retry_delay=float(os.getenv("INITIAL_RETRY_DELAY", "1.0")),
            inter_call_delay=float(os.getenv("INTER_CALL_DELAY", "0.5"))
        )
