"""
Sambanova API client implementation
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
import requests

from .base import APIClient
from utils import TokenCounter


class SambanovaClient(APIClient):
    """Sambanova API client following Single Responsibility Principle"""

    def __init__(self, api_key: str = None, model: str = "Meta-Llama-3.1-8B-Instruct", max_retries: int = 5, initial_retry_delay: float = 1.0):
        """
        Initialize Sambanova client

        Args:
            api_key: Sambanova API key (defaults to SAMBANOVA_API_KEY env var)
            model: Model to use for completions
            max_retries: Maximum number of retries for rate limit errors (default: 5)
            initial_retry_delay: Initial delay in seconds before first retry (default: 1.0)
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

        # Retry configuration
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay

        # Track cumulative usage
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.request_count = 0

        # Token counter
        self.token_counter = TokenCounter()

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, Any]:
        """
        Send a chat completion request to Sambanova with retry logic for rate limits

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

        # Count tokens before sending
        token_count = self.token_counter.count(messages, tools)

        self.logger.info(f"Sending chat request to {self.base_url}/chat/completions")
        self.logger.info(f"Model: {self.model}, Messages: {len(messages)}, Tools: {len(tools) if tools else 0}")
        if token_count > 0:
            self.logger.info(f"Estimated input tokens: {token_count}")

        # Log the full request payload for rate limit debugging
        self.logger.debug("=" * 80)
        self.logger.debug("LLM REQUEST PAYLOAD:")
        self.logger.debug("=" * 80)
        self.logger.debug(json.dumps(payload, indent=2))
        self.logger.debug("=" * 80)

        # Retry loop with exponential backoff
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )

                # Log response status
                self.logger.info(f"Response status: {response.status_code}")

                # Check for rate limit error
                if response.status_code == 429:
                    if attempt < self.max_retries:
                        # Calculate exponential backoff delay
                        delay = self.initial_retry_delay * (2 ** attempt)
                        self.logger.warning(f"Rate limit exceeded (429). Retry {attempt + 1}/{self.max_retries} after {delay:.1f}s...")
                        print(f"\n\033[1;33m⚠ Rate limit exceeded. Retrying in {delay:.1f}s... (attempt {attempt + 1}/{self.max_retries})\033[0m")
                        time.sleep(delay)
                        continue
                    else:
                        self.logger.error(f"Rate limit exceeded after {self.max_retries} retries")
                        self.logger.error(f"Error response body: {response.text}")
                        response.raise_for_status()

                # Log the full response for debugging
                self.logger.debug("=" * 80)
                self.logger.debug("LLM RESPONSE:")
                self.logger.debug("=" * 80)
                self.logger.debug(response.text)
                self.logger.debug("=" * 80)

                if response.status_code != 200:
                    self.logger.error(f"Error response body: {response.text}")

                response.raise_for_status()

                # Success - break out of retry loop
                break

            except requests.exceptions.Timeout:
                self.logger.error("Request timeout after 60 seconds")
                raise
            except requests.exceptions.RequestException as e:
                # If it's not a rate limit error, re-raise immediately
                if "429" not in str(e):
                    self.logger.error(f"Request failed: {str(e)}")
                    raise
                # If it is a 429 and we're out of retries, re-raise
                if attempt >= self.max_retries:
                    self.logger.error(f"Request failed after {self.max_retries} retries: {str(e)}")
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
