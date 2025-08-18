from logging import Logger

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import BedrockModel
from strands_tools import calculator, current_time, shell

from custom_tools import CustomTools


class SearchAgent:
    def __init__(self, logger: Logger):
        # Set up custom logging
        self.logger = logger
        self.custom_tools = CustomTools(logger=logger)

    def create_agent(
        self, model_id: str, region_name: str, temperature: float
    ) -> Agent:
        # Create a BedrockModel instance

        model = BedrockModel(
            model_id=model_id,
            region_name=region_name,
            temperature=temperature,
        )

        # Create an Ollama model instance
        # model = OllamaModel(
        #     host="http://localhost:11434",
        #     model_id=model_id,
        #     temperature=0.2,
        # )

        # Create a conversation manager
        conversation_manager = SlidingWindowConversationManager(
            window_size=20,
        )

        # Define a system prompt for the agent
        main_system_prompt = """You are a helpful search assistant that can use various tools to search OpenSearch for TV commercials 
        (aka videos) or segments of commercials (aka video segments) based on user queries.
        You can use the following tools:
        1. **Text Embedding**: Create a dense vector embedding from the user's text query.
        2. **Semantic Search for Videos**: Perform a semantic search for videos using the generated text embedding.
        3. **Semantic Search for Video Segments**: Perform a semantic search for video segments using the generated text embedding.
        4. **Keyword Search for Videos**: Perform a keyword search for videos using a list of keywords.

        The user will either provide a text-based search query that which you will use to create a dense vector embedding from. 
        Or, the user will explicitly provide a list of keywords. 
        You will either perform a semantic search in OpenSearch using the embedding you created for either videos or video segments,
        or perform a keyword search for videos using the provided keywords.
        Only perform **one** search at a time.
        If you cannot find any results, return a message indicating that no results were found. 
        If you encounter an error, return a message indicating that an error occurred.
        """

        # Create an agent with these tools
        search_agent = Agent(
            system_prompt=main_system_prompt,
            model=model,
            tools=[
                calculator,
                current_time,
                shell,
                self.custom_tools.create_text_embedding,
                self.custom_tools.keyword_search_for_videos,
                self.custom_tools.semantic_search_for_videos,
                self.custom_tools.semantic_search_for_video_segments,
            ],
            conversation_manager=conversation_manager,
        )
        return search_agent
