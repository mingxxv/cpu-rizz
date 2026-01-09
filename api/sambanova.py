"""
Sambanova API client implementation
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import requests

from .base import APIClient


class SambanovaClient(APIClient):
    """Sambanova API client following Single Responsibility Principle"""

    def __init__(self, api_key: str = None, model: str = "Meta-Llama-3.1-8B-Instruct"):
        """
        Initialize Sambanova client

        Args:
            api_key: Sambanova API key (defaults to SAMBANOVA_API_KEY env var)
            model: Model to use for completions
        """
        self.api_key = api_key or os.getenv("SAMBANOVA_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in SAMBANOVA_API_KEY env var")

        self.model = model
        self.base_url = "https://api.sambanova.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(self.__class__.__name__)

        # Track cumulative usage
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.request_count = 0

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, Any]:
        """
        Send a chat completion request to Sambanova

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions for function calling
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            The complete response data including message and tool calls
        """
        payload = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }

        if tools:
            payload["tools"] = tools

        self.logger.debug(f"Sending chat request to {self.base_url}/chat/completions")
        self.logger.debug(f"Model: {self.model}, Messages: {len(messages)}, Tools: {len(tools) if tools else 0}")

        # Log the full payload for debugging
        self.logger.debug(f"Full payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )

            # Log response status and body for debugging
            self.logger.debug(f"Response status: {response.status_code}")
            if response.status_code != 200:
                self.logger.error(f"Error response body: {response.text}")

            response.raise_for_status()
        except requests.exceptions.Timeout:
            self.logger.error("Request timeout after 60 seconds")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise

        data = response.json()

        # Log usage statistics if available
        if "usage" in data:
            usage = data["usage"]
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)

            # Update cumulative stats
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            self.total_tokens += total_tokens
            self.request_count += 1

            self.logger.info(f"API Request #{self.request_count} - Tokens: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total")
            self.logger.info(f"Cumulative usage - Total requests: {self.request_count}, Total tokens: {self.total_tokens} ({self.total_prompt_tokens} prompt + {self.total_completion_tokens} completion)")

        return data["choices"][0]["message"]

    def get_usage_stats(self) -> Dict[str, int]:
        """
        Get cumulative usage statistics

        Returns:
            Dictionary with usage statistics
        """
        return {
            "total_requests": self.request_count,
            "total_tokens": self.total_tokens,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens
        }
