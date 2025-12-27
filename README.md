# 🗓️ AI Calendar Assistant

A premium, agentic AI assistant designed to manage your Google Calendar with natural language. This assistant understands context, avoids duplicates, handles timezones gracefully, and provides a sleek, modern interface.

---

## ✨ Key Features

### 🎨 Modern "Glassmorphism" UI
- **Responsive Design**: Mobile-first layout that prioritizes the chat window on small screens.
- **Micro-animations**: Smooth transitions, hover effects, and interactive components.
- **organized structure**: Quick access to capabilities and privacy settings via elegant accordions.

### 🧠 Advanced Agent Logic
- **Full CRUD Support**: List, Create, Update, and Delete events intuitively.
- **Action Redundancy Blockers**: Strict "No Re-creation" rules and "History Over Tools" priority to prevent duplicate events.
- **Timezone Aware**: Fully localized to `Asia/Beirut` (configurable) for accurate scheduling.
- **Grounding & Verification**: Mandated link inclusion and a **"STRICT ACTION CLAUSE"** ensure the AI never hallucinations success or claims a task is done without real API confirmation.

---

## 🛠️ Tech Stack

- **Core**: Python 3.12+
- **LLM**: **Ollama** running **gpt-oss:120B** (powered by **Claude API**)
- **Orchestration**: LangChain (ReAct Pattern)
- **Interface**: Gradio (Custom CSS / Premium Design)
- **API**: Google Calendar API v3

---

## 🚀 Getting Started

### 1. Prerequisites
- **Ollama**: Installed and running with the `gpt-oss` model.
- **Google Cloud Project**: Enabled Google Calendar API with appropriate credentials.

### 2. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd Calendar_Assistant

# Create and activate virtual environment
python -m venv myvenv
source myvenv/Scripts/activate  # Windows: .\myvenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Credentials
1. Place your `credentials.json` from Google Cloud in the root directory.
2. Run the application once to authenticate and generate `token.json`.

---

## 🖥️ Usage

Launch the modern web interface:
```bash
python app.py
```
Open your browser at `http://localhost:7860`.


### 🪄  Running with: Docker Compose

If you have Docker Compose installed, you can launch everything with one command:

```bash
docker-compose up --build
```
This automatically handles the volume mounts for your `credentials.json` and `token.json`.

### Example Queries
- *"What's on my calendar for today?"*
- *"Am I free tomorrow at 3 PM?"*
- *"Add 'Project Sync' at 10 AM on Monday for 1 hour."*
- *"Move my 2 PM meeting to 4 PM tomorrow."*

---

## 🔒 Privacy & Security
Your calendar data is processed via secure Google API calls. All reasoning is performed via your Ollama instance, ensuring your schedule data is handled according to your configuration.
