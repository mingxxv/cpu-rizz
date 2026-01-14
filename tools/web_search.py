"""
Web search tool using Google Custom Search API
"""

from typing import Dict, Any, List
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .base import Tool


class WebSearchTool(Tool):
    """Web search tool for finding CPU/GPU information"""

    def __init__(self, api_key: str = None, cse_id: str = None):
        """
        Initialize the Google Custom Search tool

        Args:
            api_key: Google API key
            cse_id: Custom Search Engine ID
        """
        self.api_key = api_key
        self.cse_id = cse_id
        self._service = None

    def _get_service(self):
        """Lazy initialization of Google Custom Search service"""
        if self._service is None:
            if not self.api_key or not self.cse_id:
                raise ValueError("Google API key and CSE ID must be provided")
            self._service = build("customsearch", "v1", developerKey=self.api_key)
        return self._service

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search web for CPU/GPU specs"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 5}
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
            if not self.api_key or not self.cse_id:
                return "Error: Google API credentials not configured. Please set GOOGLE_API_KEY and GOOGLE_CSE_ID."

            service = self._get_service()

            # Handle None value for max_results (can happen when LLM passes null)
            if max_results is None:
                max_results = 5

            # Google Custom Search API returns max 10 results per request
            num_results = min(max_results, 10)

            result = service.cse().list(
                q=query,
                cx=self.cse_id,
                num=num_results
            ).execute()

            items = result.get('items', [])

            if not items:
                return f"No results found for query: {query}"

            formatted_results = []
            for i, result in enumerate(items, 1):
                snippet = result.get('snippet', '')
                # Only extract specification data from snippet
                if snippet:
                    formatted_results.append(f"{i}. {snippet}")

            return "\n".join(formatted_results)

        except HttpError as e:
            return f"Error performing search: {str(e)}"
        except Exception as e:
            return f"Error performing search: {str(e)}"
