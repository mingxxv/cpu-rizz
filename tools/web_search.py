"""
Web search tool using DuckDuckGo
"""

from typing import Dict, Any
from duckduckgo_search import DDGS

from .base import Tool


class WebSearchTool(Tool):
    """Web search tool for finding information online"""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for information. Use this to find CPU/GPU specifications, benchmarks, and performance data."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query (e.g., 'AMD Ryzen 9 7950X specifications', 'RTX 4090 benchmarks')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }

    def execute(self, query: str, max_results: int = 5) -> str:
        """
        Execute web search

        Args:
            query: Search query string
            max_results: Maximum number of results

        Returns:
            Formatted search results
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return "No results found."

            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. {result['title']}\n"
                    f"   URL: {result['href']}\n"
                    f"   {result['body']}\n"
                )

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error performing search: {str(e)}"
