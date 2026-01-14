"""
Parse and extract CPU/GPU specs from text
"""

import re
from typing import Dict, Any
from .base import Tool


class SpecParserTool(Tool):
    """Extract CPU/GPU specs from text"""

    # Keywords for CPU specs
    CPU_KEYWORDS = [
        "cores", "threads", "ghz", "mhz", "cache", "tdp", "socket",
        "nm", "architecture", "base clock", "boost clock", "turbo",
        "l1", "l2", "l3", "pcie", "ddr", "ram"
    ]

    # Keywords for GPU specs
    GPU_KEYWORDS = [
        "cuda", "stream processors", "memory", "vram", "gb", "gddr",
        "bandwidth", "clock", "tdp", "watts", "nm", "cores",
        "ray tracing", "tensor", "pcie", "bit", "mhz", "ghz"
    ]

    @property
    def name(self) -> str:
        return "spec_parser"

    @property
    def description(self) -> str:
        return "Extract only CPU/GPU specs from text"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text containing specs"},
                "hardware_type": {"type": "string", "enum": ["cpu", "gpu"], "description": "Type of hardware"}
            },
            "required": ["text", "hardware_type"]
        }

    def execute(self, text: str, hardware_type: str) -> str:
        """
        Extract specs from text

        Args:
            text: Text to parse
            hardware_type: "cpu" or "gpu"

        Returns:
            Concise spec string
        """
        keywords = self.CPU_KEYWORDS if hardware_type.lower() == "cpu" else self.GPU_KEYWORDS

        # Split into sentences
        sentences = re.split(r'[.!?\n]+', text)

        # Find sentences with specs
        spec_lines = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check if sentence contains any spec keywords
            lower_sentence = sentence.lower()
            if any(kw in lower_sentence for kw in keywords):
                # Remove numbering (1., 2., etc.)
                cleaned = re.sub(r'^\d+\.\s*', '', sentence)
                spec_lines.append(cleaned)

        if not spec_lines:
            return "No specs found"

        return "\n".join(spec_lines[:8])  # Limit to 8 most relevant lines
