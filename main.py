"""
Interactive terminal interface for AI agent with CPU/GPU information
"""

import logging
import sys
from datetime import datetime
from dotenv import load_dotenv

from api import SambanovaClient
from config import Settings
from tools import WebSearchTool
from agent import Agent


# Configure logging
def setup_logging():
    """Setup logging configuration with file and console handlers"""
    # Create logs directory if it doesn't exist
    import os
    os.makedirs('logs', exist_ok=True)

    # Create log filename with timestamp
    log_filename = f"logs/agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Setup file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Setup console handler (only warnings and errors)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return log_filename


def print_welcome():
    """Print welcome message"""
    print("\n" + "=" * 80)
    print("CPU/GPU Information Agent - Interactive Terminal".center(80))
    print("=" * 80)
    print("\nCommands:")
    print("  - Type your question to get CPU/GPU information")
    print("  - Type 'exit' or 'quit' to end the session")
    print("  - Press Ctrl+C to interrupt")
    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point with interactive terminal interface"""
    # Load environment variables
    load_dotenv()

    # Setup logging
    log_file = setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting CPU-Rizz Agent")
    logger.info(f"Log file: {log_file}")

    print(f"\nLogging to: {log_file}")

    try:
        # Initialize settings and client
        settings = Settings.from_env()
        logger.info(f"Using model: {settings.model}")
        logger.info(f"Temperature: {settings.temperature}, Max tokens: {settings.max_tokens}")

        client = SambanovaClient(api_key=settings.api_key, model=settings.model)

        # Initialize tools
        tools = [WebSearchTool()]
        logger.info(f"Initialized {len(tools)} tool(s): {[tool.name for tool in tools]}")

        # Create agent with system prompt
        system_prompt = """You are an extremely experienced hardware computer engineer specialized in finding CPU and GPU information.
When users ask about processors or graphics cards, use the web_search tool to find:
- Detailed specifications (cores, clock speeds, TDP, etc.)
- Performance benchmarks and comparisons
- Release dates and pricing

Always provide comprehensive, well-organized information.
The information should always be in the form of a table properly formatted with ASCII characters to display cleanly in a terminal shell.
For example:
+-------------+--------+--------+
|             | CPU1   | CPU2   |
+-------------+--------+--------+
| Name        |        |        |
| Cores       |        |        |
| Threads     |        |        |
| Base Clock  |        |        |
| Boost Clock |        |        |
| Socket      |        |        |
+-------------+--------+--------+

Depending on the type of CPU or GPU found, modify the rows and row naming accordingly. If there are specific or unusual characteristics, highlight that as well.
It is recommended to search on TechPowerUp for the specifications; if it does not exist there, look at either Intel ARK or AMD's website database.
If there is still nothing, search the general internet for any information.
"""

        agent = Agent(client=client, tools=tools, system_prompt=system_prompt)
        logger.info("Agent initialized successfully")

        # Print welcome message
        print_welcome()

        # Main conversation loop
        conversation_count = 0
        while True:
            try:
                # Get user input
                user_input = input("\n\033[1;36mYou:\033[0m ").strip()

                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n\033[1;33mGoodbye!\033[0m\n")
                    logger.info("User requested exit")
                    break

                # Skip empty inputs
                if not user_input:
                    continue

                conversation_count += 1
                logger.info(f"[Conversation #{conversation_count}] User: {user_input}")

                # Print separator
                print("\n" + "-" * 80)
                print("\033[1;35mAgent is thinking...\033[0m")
                print("-" * 80 + "\n")

                # Get agent response
                start_time = datetime.now()
                response = agent.run(user_message=user_input)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                # Log response
                logger.info(f"[Conversation #{conversation_count}] Response time: {duration:.2f}s")
                logger.info(f"[Conversation #{conversation_count}] Agent response length: {len(response)} chars")

                # Print response
                print("\033[1;32mAgent:\033[0m")
                print(response)
                print("\n" + "=" * 80)
                print(f"\033[2mResponse time: {duration:.2f}s\033[0m")

            except KeyboardInterrupt:
                print("\n\n\033[1;33mInterrupted. Type 'exit' to quit or continue chatting.\033[0m")
                logger.warning("Keyboard interrupt received")
                continue
            except Exception as e:
                print(f"\n\033[1;31mError: {str(e)}\033[0m\n")
                logger.error(f"Error during conversation: {str(e)}", exc_info=True)
                continue

        # Print session summary
        usage_stats = client.get_usage_stats()
        print(f"\nSession summary:")
        print(f"  - Total conversations: {conversation_count}")
        print(f"  - Total API requests: {usage_stats['total_requests']}")
        print(f"  - Total tokens used: {usage_stats['total_tokens']:,}")
        print(f"    - Prompt tokens: {usage_stats['total_prompt_tokens']:,}")
        print(f"    - Completion tokens: {usage_stats['total_completion_tokens']:,}")
        print(f"  - Logs saved to: {log_file}\n")
        logger.info(f"Session ended. Total conversations: {conversation_count}")
        logger.info(f"Final usage stats: {usage_stats}")

    except ValueError as e:
        print(f"\n\033[1;31mConfiguration Error: {str(e)}\033[0m")
        print("Please ensure your .env file is properly configured.\n")
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\033[1;31mFatal Error: {str(e)}\033[0m\n")
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
