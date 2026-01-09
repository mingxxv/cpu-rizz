"""
Base tool interface following Interface Segregation Principle
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class Tool(ABC):
    """Abstract base class for agent tools"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for identification"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for the LLM"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema for tool parameters"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        Execute the tool with given parameters

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Execution result as string
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
