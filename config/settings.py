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

        return cls(
            api_key=api_key,
            model=os.getenv("MODEL", "Meta-Llama-3.1-8B-Instruct"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS", "1000"))
        )
