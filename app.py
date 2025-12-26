"""
Calendar Assistant - Gradio Web Interface
AI-powered calendar management with Google Calendar integration
"""

# -*- coding: utf-8 -*-
import sys
import io

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import gradio as gr
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.agent import CalendarAssistantChat


# Initialize the agent
print("🚀 Initializing Calendar Assistant for Gradio...")
chat_assistant = CalendarAssistantChat(verbose=False)
print("✅ Calendar Assistant ready for web interface!\n")


def chat_interface(message, history):
    """
    Process chat messages and return responses
    
    Args:
        message (str): User's message
        history (list): Chat history (not used but required by Gradio)
    
    Returns:
        str: Assistant's response
    """
    if not message or message.strip() == "":
        return "Please enter a message."
    
    try:
        response = chat_assistant.chat(message)
        return response
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease try again or rephrase your question."


def reset_conversation():
    """Reset the chat history"""
    chat_assistant.reset()
    return None

# Calendar Information Panel (Streamlined)
calendar_info_lean = """
### 🗓️ Quick Actions
- **List**: "What's coming up?"
- **Check**: "Am I free at 2pm?"
- **Create**: "Add meeting at 10am tomorrow for 2hours"
- **Update**: "Move my 2pm to 3pm {event name}"
- **Delete**: "Remove my meeting at 2pm tomorrow"

### 💡 Pro Tip
Specific dates (Dec 27th) and times work best!
"""

# Custom Premium CSS
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
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

#chatbot {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

.message-wrap .message.user {
    background: var(--primary-gradient) !important;
    border: none !important;
    color: white !important;
    border-radius: 15px 15px 0 15px !important;
}

.message-wrap .message.bot {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid var(--glass-border) !important;
    color: #f1f5f9 !important;
    border-radius: 15px 15px 15px 0 !important;
}

.sidebar-panel {
    background: var(--glass-bg);
    backdrop-filter: blur(8px);
    border: 1px solid var(--glass-border);
    border-radius: 15px;
    padding: 20px;
    height: 100%;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 8px;
    background: rgba(34, 197, 94, 0.1);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.2);
}

.footer {
    opacity: 0.6;
    font-size: 0.8rem;
    padding: 20px;
}

button.primary {
    background: var(--primary-gradient) !important;
    border: none !important;
    transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}

button.primary:hover {
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
    #main-layout-row {
        flex-direction: column-reverse !important;
    }
    .sidebar-panel {
        margin-top: 20px;
    }
}
"""

# Build Gradio Interface
with gr.Blocks(css=custom_css, title="Calendar Assistant", theme=gr.themes.Default()) as demo:
    
    with gr.Row(elem_id="main-layout-row"):
        # Left sidebar for info and status
        with gr.Column(scale=1, elem_classes="sidebar-panel"):
            gr.Markdown("# 🗓️ Calendar Assistant")
            with gr.Accordion("✨ Quick Actions", open=True):
                gr.Markdown(calendar_info_lean)
            
            with gr.Accordion("🔒 Privacy & Security", open=False):
                gr.Markdown("Your data is processed locally and via secure Google API calls.")
                
        # Main Chat Area
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(
                elem_id="chatbot",
                show_label=False,
                height=500,
                show_copy_button=True,
                avatar_images=(None, "https://api.iconify.design/noto:calendar.svg")
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    show_label=False,
                    placeholder="Ask me something...",
                    container=False,
                    scale=7,
                    autofocus=True
                )
                submit = gr.Button("Send", variant="primary", scale=1)
            
            # Quick suggestions as pills
            with gr.Row():
                gr.Examples(
                    examples=[
                        "What's on my calendar for today?",
                        "Am I free tomorrow at 10am?",
                        "Add 'Team Sync' tomorrow at 2pm",
                        "Show my upcoming 5 events"
                    ],
                    inputs=msg,
                    label="Quick Actions"
                )

            with gr.Row():
                clear = gr.Button("Clear Chat", variant="secondary", size="sm")
                reset = gr.Button("Reset Agent", variant="secondary", size="sm")
            
    # Inline footer
    gr.HTML("<div class='footer'>© 2025 Calendar Assistant | Powered by Ollama & Google Calendar API</div>")
    
    # Event Handlers
    def user_message(message, history):
        """Handle user message submission"""
        if history is None:
            history = []
        return "", history + [[message, None]]
    
    def bot_response(history):
        """Get bot response"""
        if history and history[-1][1] is None:
            user_msg = history[-1][0]
            bot_msg = chat_interface(user_msg, history)
            history[-1][1] = bot_msg
        return history
    
    # Connect events
    msg.submit(user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_response, chatbot, chatbot
    )
    
    submit.click(user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_response, chatbot, chatbot
    )
    
    clear.click(lambda: None, None, chatbot, queue=False)
    
    reset.click(
        reset_conversation,
        None,
        chatbot,
        queue=False
    )

# Launch the app
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 Starting Calendar Assistant Gradio Interface")
    print("="*70 + "\n")
    
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,  # Set to True to create public link
        show_error=True
    )