AI Tutor Pro - Multi-Agent SystemThis project is a sophisticated, conversational AI tutoring assistant built using Python, Flask, and the Gemini API. It features a multi-agent architecture where a primary "Tutor Agent" delegates user queries to specialized sub-agents for mathematics, physics, and general knowledge/coding tasks.FeaturesMulti-Agent Architecture: A central Tutor Agent intelligently routes tasks to the appropriate specialist.Specialist Agents:Math Agent: Solves mathematical problems and explains concepts. Utilizes a Calculator Tool for precise calculations.Physics Agent: Answers physics questions and provides definitions. Uses a Constants Lookup Tool for physical values.General Agent: Handles other queries and features a Python Code Generation Tool.Conversational Memory: The agent remembers the context of the conversation for a more natural and continuous interaction.Dynamic Tool Use: Agents intelligently decide when to use their tools by consulting the Gemini API.Markdown & Code Rendering: The agent can format its responses with Markdown, including lists, bold text, and code blocks with syntax highlighting and a "copy" button.Sleek, Responsive Frontend: A clean user interface built with HTML and Tailwind CSS that works on all devices.Tech StackBackend: Python, FlaskAI Model: Google Gemini APIFrontend: HTML, Tailwind CSS, JavaScriptLibraries: requests (for API calls), marked.js (for Markdown), highlight.js (for syntax highlighting)Setup and InstallationFollow these steps to run the project on your local machine.PrerequisitesPython 3.7+pip (Python package installer)A Google Gemini API Key. You can get one from Google AI Studio.1. Backend SetupFirst, set up and run the Flask server.# 1. Clone the repository (or download the files)
git clone <your-repository-url>
cd <your-repository-directory>

# 2. Install the required Python packages
pip install -r requirements.txt

# 3. Set your Gemini API key as an environment variable
# On macOS/Linux:
export GEMINI_API_KEY="YOUR_API_KEY_HERE"

# On Windows (Command Prompt):
set GEMINI_API_KEY="YOUR_API_KEY_HERE"

# 4. Run the Flask server
flask run --port 5001
Your backend should now be running at http://127.0.0.1:5001.2. Frontend SetupThe frontend is a single HTML file and requires no build steps.Navigate to your project directory.Open the index.html file in your favorite web browser (e.g., Google Chrome, Firefox).How to UseOnce the frontend is open in your browser, you can start a conversation:Ask a math question: "What is 144 * 12?" or "Explain the Pythagorean theorem."Ask a physics question: "What is the value for the speed of light?" or "What is Newton's second law?"Request a code snippet: "Write me a python function to check if a number is prime."Have a continuous conversation: Ask follow-up questions. The agent will remember what you were talking about.Clear the chat: Click the "Clear" button in the header to start a new conversation.Project Structure.
├── app.py              # The Flask backend server, agents, and tools logic
├── index.html          # The HTML frontend for the user interface
└── requirements.txt    # Python dependencies for the backend