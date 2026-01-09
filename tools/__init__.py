"""
Tools module for agent capabilities
"""

from .base import Tool
from .web_search import WebSearchTool

__all__ = ["Tool", "WebSearchTool"]
