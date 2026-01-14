"""
Token counting utility
"""

import json
import logging
from typing import Dict, List, Any, Optional


class TokenCounter:
    """Counts tokens using the model's tokenizer"""

    def __init__(self, model_name: str = "gpt2"):
        """
        Initialize token counter

        Args:
            model_name: HuggingFace model name to use for tokenization.
                       Defaults to 'gpt2' which is publicly available and doesn't require authentication.
                       This provides approximate token counts that are useful for monitoring.
        """
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)
        self._tokenizer = None

    def _get_tokenizer(self):
        """Lazy initialization of tokenizer"""
        if self._tokenizer is None:
            try:
                from transformers import AutoTokenizer
                self.logger.info("Loading tokenizer for token counting...")
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.logger.info("Tokenizer loaded successfully")
            except Exception as e:
                self.logger.warning(f"Failed to load tokenizer: {e}. Token counting disabled.")
                self._tokenizer = False
        return self._tokenizer if self._tokenizer is not False else None

    def count(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> int:
        """
        Count tokens in messages

        Args:
            messages: List of message dicts
            tools: Optional tool definitions

        Returns:
            Token count, or 0 if unavailable
        """
        tokenizer = self._get_tokenizer()
        if not tokenizer:
            return 0

        try:
            # Combine messages
            text = "\n".join(f"{msg.get('role', '')}: {msg.get('content', '')}" for msg in messages)

            # Add tools if present
            if tools:
                text += "\nTools:\n" + json.dumps(tools, indent=2)

            return len(tokenizer.encode(text))
        except Exception as e:
            self.logger.warning(f"Failed to count tokens: {e}")
            return 0
