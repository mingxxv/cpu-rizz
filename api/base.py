"""
Base API client interface following the Interface Segregation Principle
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class APIClient(ABC):
    """Abstract base class for AI API clients"""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Send a chat completion request

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional provider-specific parameters

        Returns:
            The generated response text
        """
        pass
