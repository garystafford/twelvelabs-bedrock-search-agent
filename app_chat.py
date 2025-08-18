# TV Commercial Search Agent
# This application allows users to search for TV commercials using a conversational agent.
# It uses Gradio for the UI and integrates with Strands Agents, TwelveLabs, and OpenSearch.
# It also captures logs and outputs them in real-time to the UI.
# Opens on http://127.0.0.1:7860/ or http://127.0.0.1:7860/?__theme=light
# Author: Gary A. Stafford
# Date: 2025-08-16

import gradio as gr
from gradio.themes import Base, GoogleFont
from gradio_log import Log
from strands import Agent

from gradio_logger import GradioLogger
from search_agent import SearchAgent

# Agent configuration
MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
MODEL_REGION = "us-east-1"
MODEL_TEMPERATURE = 0.2

# Log file
log_file = "./log_file.txt"
with open(log_file, "w") as f:
    pass  # The 'pass' statement does nothing, but the 'w' mode clears the file


# Set up custom logging
gradio_logger = GradioLogger()
logger = gradio_logger.setup_logging()

search_agent = SearchAgent(logger=logger)

agent: Agent = search_agent.create_agent(MODEL_ID, MODEL_REGION, MODEL_TEMPERATURE)

# -------------------------------------------------
# GRADIO FRONTEND COMPONENTS
# -------------------------------------------------


# ---- GRADIO APP LAYOUT ----

custom_css = """
#logs-box textarea {
    font-family: "Courier New", Courier, monospace; font-size: 12px;
}
#config-info p {
    font-size: 14px;
    color: lightgray;
}
footer {
    display: none !important;
}
#input-query {
        font-size: 12px;
}
#chatbot span p {
    font-size: 14px;
}
"""

with gr.Blocks(
    title="Video Search Agent",
    css=custom_css,
    theme=Base(font=[GoogleFont("Inter"), "Arial", "sans-serif"]),
) as demo:
    gr.Markdown(
        """
        # 📺 Video Search Agent powered by TwelveLabs
        Enter your search query below to find relevant videos.
        """,
        elem_id="title-header",
    )

    with gr.Row():
        with gr.Column(scale=2, min_width=800):
            chatbot = gr.Chatbot(
                type="messages", min_height=300, max_height=600, elem_id="chatbot"
            )
            with gr.Column(scale=2, min_width=600):
                with gr.Row():
                    msg = gr.Textbox(
                        label="User Input",
                        placeholder="Enter your query...",
                        lines=1,
                        max_lines=2,
                        interactive=True,
                        show_copy_button=False,
                        autoscroll=True,
                        elem_id="input-query",
                    )
            with gr.Column(scale=2, min_width=600):
                Log(log_file, dark=True, xterm_font_size=12)

        def user(user_message, history: list):
            return "", history + [{"role": "user", "content": user_message}]

        def bot(history: list):
            history.append(
                {
                    "role": "assistant",
                    "content": str(agent(history[-1]["content"])),
                }
            )
            return history

        msg.submit(
            fn=user, inputs=[msg, chatbot], outputs=[msg, chatbot], queue=False
        ).then(fn=bot, inputs=[chatbot], outputs=chatbot)

    def simple_auth(username, password):
        # check if username is demo and password is demo123
        return username == "demo" and password == "demo123"

    # Configuration information and logout button
    config_info = f"Provider: Amazon Bedrock | Model: {MODEL_ID} | Temperature: {MODEL_TEMPERATURE}"  # type: ignore
    # config_info = f"Provider: Ollama | Model: {model.get_config()['model_id']} | Temperature: {model.get_config()['temperature']}"  # type: ignore
    with gr.Row():
        with gr.Column(scale=4, min_width=800):
            gr.Markdown(
                value=config_info,
                elem_id="config-info",
            )
        with gr.Column(scale=1, min_width=50):
            logout_button = gr.Button(
                icon="./icons/logout_64px.png",
                value=" Logout",
                link="/logout",
                variant="secondary",
                scale=1,
            )
    logout_button.click(fn=lambda: "You have been logged out.", outputs=None)


demo.queue()  # Sequential processing
demo.launch()  # auth=simple_auth
