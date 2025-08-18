# This terminal-based application uses the Strands framework to create an intelligent agent
# that can search for TV commercials using various tools and a conversational interface.
# It integrates with AWS Bedrock for AI capabilities and includes custom tools for searching.
# It also includes basic logging to the terminal.
# Author: Gary A. Stafford
# Date: 2025-08-03

from strands import Agent

from basic_logging import BasicLogging
from search_agent import SearchAgent

# Agent configuration
MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
MODEL_REGION = "us-east-1"
MODEL_TEMPERATURE = 0.2

# Sets the logging format and streams logs to stderr
basic_logger = BasicLogging()
logger = basic_logger.setup_logging()

search_agent = SearchAgent(logger=logger)

agent: Agent = search_agent.create_agent(MODEL_ID, MODEL_REGION, MODEL_TEMPERATURE)

RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
RESET = "\033[0m"

# Interactive loop
print(f"{BLUE}Welcome to the TwelveLabs Video Search Agent!{RESET}")
while True:
    try:
        user_input = input(f"\n{BLUE}> {RESET}")

        if user_input.lower() == "exit" or user_input.lower() == "quit":
            print(f"\n{BLUE}Goodbye! 👋{RESET}")
            break

        # Call the video search agent
        response = agent(user_input)
    except KeyboardInterrupt:
        print(f"\n\n{RED}Execution interrupted. Exiting...{RESET}")
        break
    except Exception as e:
        print(f"\n{RED}An error occurred: {str(e)}{RESET}")
        print(f"{RED}Please try a different request.{RESET}")
