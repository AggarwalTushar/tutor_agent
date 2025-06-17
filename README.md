# AI Tutor Pro - Multi-Agent System

This project is a sophisticated, conversational AI tutoring assistant built using Python, Flask, and the Gemini API. It features a multi-agent architecture where a primary "Tutor Agent" delegates user queries to specialized sub-agents for mathematics, physics, and general knowledge/coding tasks.

![AI Tutor Pro Screenshot](https://placehold.co/800x500/14b8a6/ffffff?text=AI%20Tutor%20Pro%20UI)

---

## Features

* **Multi-Agent Architecture**: A central Tutor Agent intelligently routes tasks to the appropriate specialist.
* **Specialist Agents**:
    * **Math Agent**: Solves mathematical problems and explains concepts. Utilizes a **Calculator Tool** for precise calculations.
    * **Physics Agent**: Answers physics questions and provides definitions. Uses a **Constants Lookup Tool** for physical values.
    * **General Agent**: Handles other queries and features a **Python Code Generation Tool**.
* **Conversational Memory**: The agent remembers the context of the conversation for a more natural and continuous interaction.
* **Dynamic Tool Use**: Agents intelligently decide when to use their tools by consulting the Gemini API.
* **Markdown & Code Rendering**: The agent can format its responses with Markdown, including lists, bold text, and code blocks with syntax highlighting and a "copy" button.
* **Sleek, Responsive Frontend**: A clean user interface built with HTML and Tailwind CSS that works on all devices.

---

## Tech Stack

* **Backend**: Python, Flask
* **AI Model**: Google Gemini API
* **Frontend**: HTML, Tailwind CSS, JavaScript
* **Libraries**: `requests` (for API calls), `marked.js` (for Markdown), `highlight.js` (for syntax highlighting)

---

## Setup and Installation

Follow these steps to run the project on your local machine.

### Prerequisites

* Python 3.7+
* `pip` (Python package installer)
* A Google Gemini API Key. You can get one from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 1. Backend Setup

First, set up and run the Flask server.

```bash
# 1. Clone the repository (or download the files)
git clone https://github.com/AggarwalTushar/tutor_agent.git
cd tutor_agent

# 2. Install the required Python packages
pip install -r requirements.txt

# 3. Set your Gemini API key as an environment variable
# On macOS/Linux:
export API_KEY="YOUR_API_KEY_HERE"

# On Windows (Command Prompt):
set API_KEY="YOUR_API_KEY_HERE"

# 4. Run the Flask server
python run.py