# TV Commercial Search Agent
# This application allows users to search for TV commercials using a conversational agent.
# It uses Gradio for the UI and integrates with Strands Agents, TwelveLabs, and OpenSearch.
# It also captures logs and outputs them in real-time to the UI.
# Opens on http://127.0.0.1:7860/ or http://127.0.0.1:7860/?__theme=light
# Author: Gary A. Stafford
# Date: 2025-08-03

import queue
import threading

import gradio as gr
from gradio.themes import Base, GoogleFont
from strands import Agent

from custom_logging import CustomLogging
from search_agent import SearchAgent

# Agent configuration
MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
MODEL_REGION = "us-east-1"
MODEL_TEMPERATURE = 0.2


# Set up custom logging
def setup_logging():
    custom_logging = CustomLogging()
    logger = custom_logging.setup_logging()
    log_queue = custom_logging.get_log_queue()
    return logger, log_queue


logger, log_queue = setup_logging()

search_agent = SearchAgent(logger=logger)

agent: Agent = search_agent.create_agent(MODEL_ID, MODEL_REGION, MODEL_TEMPERATURE)

# -------------------------------------------------
# GRADIO FRONTEND COMPONENTS
# -------------------------------------------------


def submit_query(user_query, logs_so_far):
    """
    Process the user query, interact with the agent, and update output and logs.
    """
    log_lines = logs_so_far.split("\n") if logs_so_far else []
    # Clear logs to avoid duplicate display
    # displayed_logs = []
    # Start a thread to relay live logs
    stop_event = threading.Event()
    logs_thread = threading.Thread(target=relay_live_logs, args=(log_lines, stop_event))
    logs_thread.start()

    try:
        logger.info("Processing started for user query.")
        # Visual feedback handled via gradio update below (progress bar)
        result = agent(user_query)
        if not result:
            output = "No results found. Try a different query."
        else:
            output = result
        logger.info("Processing complete.")
        logger.info(f"Total tokens: {result.metrics.accumulated_usage['totalTokens']}")
        logger.info(
            f"Execution time: {sum(result.metrics.cycle_durations):.2f} seconds"
        )
        logger.info(f"Tools used: {list(result.metrics.tool_metrics.keys())}")

    except Exception as e:
        output = f"❌ Error: {str(e)}"
        logger.error("Query processing failed: %s", str(e))
    finally:
        stop_event.set()
        logs_thread.join()

    final_logs = "\n".join(log_lines)
    return output, final_logs


def relay_live_logs(displayed_logs, stop_event):
    """Stream logs from the queue into the currently displayed logs list"""
    while not stop_event.is_set() or not log_queue.empty():
        try:
            msg = log_queue.get(timeout=0.1)
            displayed_logs.append(msg)
        except queue.Empty:
            continue


def get_initial_logs():
    """Return initial startup logs."""
    logger.info("Gradio UI initialized and ready.")
    return fetch_logs_from_queue()


def fetch_logs_from_queue():
    """Drains the logs from the queue for initial display."""
    lines = []
    while not log_queue.empty():
        lines.append(log_queue.get())
    return "\n".join(lines)


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
        with gr.Column(scale=2, min_width=400):
            user_input = gr.Textbox(
                label="User Input",
                placeholder="Enter your query...",
                lines=8,
                max_lines=10,
                interactive=True,
                show_copy_button=False,
                elem_id="input-query",
            )
            with gr.Row():
                submit_btn = gr.Button(
                    icon="./icons/search-engine_64px.png",
                    value="Search",
                    variant="primary",
                )
                reset_btn = gr.Button(
                    icon="./icons/broom_64px.png",
                    value="New Conversation",
                    variant="secondary",
                )
        with gr.Column(scale=3, min_width=450):
            output_text = gr.Textbox(
                label="Agent Response",
                value="",
                lines=12,
                max_lines=20,
                interactive=False,
                show_copy_button=True,
                elem_id="agent-output",
            )
    logs_box = gr.Textbox(
        label="Live System Logs",
        value=get_initial_logs(),
        lines=12,
        max_lines=20,
        interactive=False,
        elem_id="logs-box",
    )

    def on_submit(q, logs):
        return submit_query(q, logs)

    submit_btn.click(
        fn=on_submit, inputs=[user_input, logs_box], outputs=[output_text, logs_box]
    )

    user_input.submit(
        fn=on_submit, inputs=[user_input, logs_box], outputs=[output_text, logs_box]
    )

    def on_reset(q, logs):
        q = "Forget our previous conversation."
        return submit_query(q, logs)

    reset_btn.click(
        fn=on_reset, inputs=[user_input, logs_box], outputs=[output_text, logs_box]
    )

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
    logout_button.click(fn=lambda: "You have been logged out.", outputs=output_text)


demo.queue()  # Sequential processing
demo.launch(auth=simple_auth)  # auth=simple_auth
