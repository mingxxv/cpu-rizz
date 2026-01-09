"""
Web search tool using DuckDuckGo with site restrictions for hardware specs
"""

from typing import Dict, Any, List
from duckduckgo_search import DDGS

from .base import Tool


class WebSearchTool(Tool):
    """Web search tool for finding CPU/GPU information from trusted sources"""

    # Trusted sites for hardware specifications
    TRUSTED_SITES = [
        "techpowerup.com",
        "ark.intel.com",
        "amd.com",
    ]

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web for CPU/GPU information from trusted sources only. "
            "Automatically restricts searches to TechPowerUp, Intel ARK, and AMD official sites. "
            "Use this to find specifications, benchmarks, and performance data."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query (e.g., 'Intel Core i9-13900K specifications')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5
                },
                "specific_site": {
                    "type": "string",
                    "description": "Optional: search only a specific site (techpowerup, intel, or amd)",
                    "enum": ["techpowerup", "intel", "amd"]
                }
            },
            "required": ["query"]
        }

    def _build_site_restricted_query(self, query: str, specific_site: str = None) -> List[str]:
        """
        Build queries with site restrictions

        Args:
            query: Original search query
            specific_site: Optional specific site to search

        Returns:
            List of queries to try
        """
        queries = []

        if specific_site:
            # Search specific site only
            site_map = {
                "techpowerup": "site:techpowerup.com",
                "intel": "site:ark.intel.com",
                "amd": "site:amd.com"
            }
            if specific_site in site_map:
                queries.append(f"{query} {site_map[specific_site]}")
        else:
            # Try TechPowerUp first (best for specs), then Intel ARK, then AMD
            queries.append(f"{query} site:techpowerup.com")
            queries.append(f"{query} site:ark.intel.com")
            queries.append(f"{query} site:amd.com")

        return queries

    def execute(self, query: str, max_results: int = 5, specific_site: str = None) -> str:
        """
        Execute web search restricted to trusted hardware sites

        Args:
            query: Search query string
            max_results: Maximum number of results
            specific_site: Optional specific site to search (techpowerup, intel, amd)

        Returns:
            Formatted search results
        """
        try:
            all_results = []
            queries_to_try = self._build_site_restricted_query(query, specific_site)

            # Try each query until we get results
            for search_query in queries_to_try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(search_query, max_results=max_results))

                if results:
                    all_results.extend(results)
                    # If we found results, stop trying other sites
                    break

            # Remove duplicates by URL
            seen_urls = set()
            unique_results = []
            for result in all_results:
                if result['href'] not in seen_urls:
                    seen_urls.add(result['href'])
                    unique_results.append(result)

            if not unique_results:
                return (
                    f"No results found on trusted sites (TechPowerUp, Intel ARK, AMD) for query: {query}\n"
                    f"Try rephrasing your query or check the exact product name."
                )

            formatted_results = []
            for i, result in enumerate(unique_results[:max_results], 1):
                formatted_results.append(
                    f"{i}. {result['title']}\n"
                    f"   URL: {result['href']}\n"
                    f"   {result['body']}\n"
                )

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error performing search: {str(e)}"
