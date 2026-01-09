"""
Simple agent with tool calling capabilities
"""

import json
import logging
from typing import List, Dict, Any

from api import SambanovaClient
from tools import Tool


class Agent:
    """Agent that can use tools to answer questions"""

    def __init__(self, client: SambanovaClient, tools: List[Tool], system_prompt: str = None):
        """
        Initialize agent

        Args:
            client: API client for LLM communication
            tools: List of available tools
            system_prompt: Optional system prompt
        """
        self.client = client
        self.tools = {tool.name: tool for tool in tools}
        self.system_prompt = system_prompt or "You are a helpful AI assistant that can search the web for information."
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Run the agent with tool calling loop

        Args:
            user_message: User's question or request
            max_iterations: Maximum number of tool calling iterations

        Returns:
            Final response text
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        tool_definitions = [tool.to_dict() for tool in self.tools.values()]
        self.logger.info(f"Starting agent run with {len(tool_definitions)} available tools")

        total_tool_calls = 0

        for iteration in range(max_iterations):
            self.logger.debug(f"Iteration {iteration + 1}/{max_iterations}")

            # Get response from LLM
            try:
                response = self.client.chat(messages=messages, tools=tool_definitions)
                self.logger.debug(f"Received response from LLM")
            except Exception as e:
                self.logger.error(f"Error calling LLM API: {str(e)}", exc_info=True)
                raise

            # Check if model wants to call a tool
            tool_calls = response.get("tool_calls")

            if not tool_calls:
                # No tool calls, return the final response
                final_response = response.get("content", "")
                self.logger.info(f"Agent completed in {iteration + 1} iteration(s)")
                self.logger.info(f"Total tool calls made: {total_tool_calls}")
                self.logger.debug(f"Final response length: {len(final_response)} chars")
                return final_response

            # IMPORTANT: SambaNova API doesn't support multiple tool calls in one message
            # Only process the first tool call to avoid 500 errors
            if len(tool_calls) > 1:
                self.logger.warning(f"Model requested {len(tool_calls)} tool calls, but SambaNova only supports 1 at a time. Processing only the first one.")
                tool_calls = [tool_calls[0]]

            # Add assistant message with tool calls to conversation
            messages.append({
                "role": "assistant",
                "content": response.get("content"),
                "tool_calls": tool_calls
            })

            self.logger.info(f"Processing {len(tool_calls)} tool call(s)")

            # Execute each tool call
            for idx, tool_call in enumerate(tool_calls, 1):
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])

                total_tool_calls += 1

                # Log tool call details
                self.logger.info(f"Tool call {idx}/{len(tool_calls)}: {function_name}")
                self.logger.debug(f"Tool arguments: {json.dumps(function_args, indent=2)}")

                # Print to console with color
                print(f"\n\033[1;34m[Tool Call]\033[0m {function_name}")
                print(f"\033[2mArguments: {json.dumps(function_args, indent=2)}\033[0m")

                # Execute the tool
                try:
                    if function_name in self.tools:
                        result = self.tools[function_name].execute(**function_args)
                        result_preview = result[:200] + "..." if len(result) > 200 else result
                        self.logger.info(f"Tool '{function_name}' executed successfully")
                        self.logger.debug(f"Tool result length: {len(result)} chars")
                        print(f"\033[2mResult: {result_preview}\033[0m\n")
                    else:
                        result = f"Error: Tool '{function_name}' not found"
                        self.logger.error(f"Tool '{function_name}' not found in available tools")
                        print(f"\033[1;31m{result}\033[0m\n")
                except Exception as e:
                    result = f"Error executing tool: {str(e)}"
                    self.logger.error(f"Error executing tool '{function_name}': {str(e)}", exc_info=True)
                    print(f"\033[1;31m{result}\033[0m\n")

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": function_name,
                    "content": result
                })

        self.logger.warning(f"Max iterations ({max_iterations}) reached")
        self.logger.info(f"Total tool calls made: {total_tool_calls}")
        return "Max iterations reached. Please try again with a simpler question."
