"""
Calendar Assistant - Gradio Web Interface
AI-powered calendar management with Google Calendar integration
"""

# -*- coding: utf-8 -*-
import sys
import io
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import gradio as gr

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.agent import CalendarAssistantChat


# =========================
# Initialize Assistant
# =========================
print("🚀 Initializing Calendar Assistant for Gradio...")
chat_assistant = CalendarAssistantChat(verbose=False)
print("✅ Calendar Assistant ready!\n")


# =========================
# Helper Functions
# =========================
def reset_conversation():
    chat_assistant.reset()
    return []


# =========================
# UI Text
# =========================
calendar_info_lean = """
### 🗓️ Quick Actions
- **List**: "What's coming up?"
- **Check**: "Am I free at 2pm?"
- **Create**: "Add meeting at 10am tomorrow for 2 hours"
- **Update**: "Move my 2pm to 3pm {event name}"
- **Delete**: "Remove my meeting at 2pm tomorrow"

### 💡 Pro Tip
Specific dates and times work best!
"""

custom_css = """
:root {
    --primary-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    --bg-gradient: radial-gradient(circle at top left, #1e1b4b 0%, #0f172a 100%);
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
}

.gradio-container {
    background: var(--bg-gradient) !important;
    color: #e2e8f0 !important;
}

#chatbot {
    background: var(--glass-bg) !important;
    border-radius: 20px !important;
}
"""


# =========================
# Gradio App
# =========================
with gr.Blocks(title="Calendar Assistant") as demo:

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("# 🗓️ Calendar Assistant")
            

    chatbot = gr.Chatbot(
        elem_id="chatbot",
        height=500,
    )

    msg = gr.Textbox(
        placeholder="Ask me about your calendar...",
        show_label=False,
    )

    submit = gr.Button("Send", variant="primary")
    clear = gr.Button("Clear Chat")

    gr.Markdown(calendar_info_lean)


    # =========================
    # Event Handlers (Gradio 6)
    # =========================
    def user_message(message, history):
        if history is None:
            history = []
        history.append({"role": "user", "content": message})
        return "", history

    def bot_response(history):
        if history and history[-1]["role"] == "user":
            user_msg = history[-1]["content"]
            bot_msg = chat_assistant.chat(user_msg)
            history.append({"role": "assistant", "content": bot_msg})
        return history


    msg.submit(
        user_message,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot],
        queue=False,
    ).then(
        bot_response,
        inputs=chatbot,
        outputs=chatbot,
    )

    submit.click(
        user_message,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot],
        queue=False,
    ).then(
        bot_response,
        inputs=chatbot,
        outputs=chatbot,
    )

    clear.click(lambda: [], None, chatbot)


# =========================
# Launch
# =========================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 Starting Calendar Assistant Gradio Interface")
    print("=" * 70 + "\n")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=custom_css,
        theme=gr.themes.Default(),
        show_error=True,
        share=False,
    )
