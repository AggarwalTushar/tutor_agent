import os
import re
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app) 

GEMINI_API_KEY = os.getenv("API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

# --- Gemini API Call ---
def call_gemini_api(prompt, conversation_history=None):
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is not set. Please set the environment variable."

    contents = []
    if conversation_history:
        for entry in conversation_history:
            role = "user" if entry["sender"] == "user" else "model"
            contents.append({'role': role, 'parts': [{'text': entry["text"]}]})
    
    contents.append({'role': 'user', 'parts': [{'text': prompt}]})
    
    headers = {'Content-Type': 'application/json'}
    payload = {'contents': contents}
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        candidates = response.json().get('candidates', [])
        if candidates and 'content' in candidates[0] and 'parts' in candidates[0]['content']:
            return candidates[0]['content']['parts'][0].get('text', "Sorry, I couldn't generate a response.").strip()
        
        return "Sorry, the response from the API was not in the expected format."
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return "Error: Could not connect to the Gemini API."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}"

# --- TOOLS ---

def calculator_tool(expression: str) -> str:
    expression = "".join(filter(lambda char: char in "0123456789.+-*/() ", expression))
    try:
        result = eval(expression, {"__builtins__": None}, {})
        return f"The result of the calculation `{expression}` is {result}."
    except Exception as e:
        return f"I encountered an error trying to calculate that: {e}. Please ensure it's a valid mathematical expression."

def physics_constants_tool(constant_name: str) -> str | None:
    constants = {
        "speed of light": "299,792,458 m/s",
        "gravitational constant": "6.67430 x 10^-11 N(m/kg)^2",
        "planck's constant": "6.62607015 x 10^-34 J*s",
        "gravity": "9.8 m/s^2 (on Earth)"
    }
    for key in constants:
        if key in constant_name.lower():
            return f"The value of {key} is {constants[key]}."
    return None

# --- AGENT DEFINITIONS ---

def math_agent(query: str, history: list) -> str:
    """Specializes in math questions, deciding when to use its calculator tool."""
    print("Delegating to Math Agent...")
    
    # Ask the LLM if the calculator tool is needed for the latest query
    tool_prompt = f"""
    Conversation History:
    {json.dumps(history, indent=2)}

    User's latest query: "{query}"

    Based on the user's latest query, do you need to use the calculator tool? 
    The calculator can evaluate mathematical expressions (e.g., "5*10", "100 / 4").
    Respond with a JSON object containing two keys:
    1. "use_tool": boolean (true if the calculator is needed, otherwise false)
    2. "expression": string (the mathematical expression to calculate, or an empty string if not using the tool)
    
    Example for 'what is 25 * 4?': {{"use_tool": true, "expression": "25 * 4"}}
    Example for 'what is a prime number?': {{"use_tool": false, "expression": ""}}
    """
    
    try:
        tool_decision_str = call_gemini_api(tool_prompt)
        tool_decision = json.loads(tool_decision_str)
        
        if tool_decision.get("use_tool"):
            print(f"Math Agent decided to use the calculator for: {tool_decision.get('expression')}")
            return calculator_tool(tool_decision.get("expression"))
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Math Agent could not parse tool decision: {e}. Proceeding without tool.")

    print("Math Agent is generating a conversational response.")
    concept_prompt = f"You are a friendly and helpful math tutor. Answer the user's question clearly and concisely."
    return call_gemini_api(concept_prompt, history + [{"sender": "user", "text": query}])

def physics_agent(query: str, history: list) -> str:
    """Specializes in physics questions, deciding when to look up a constant."""
    print("Delegating to Physics Agent...")

    # Ask the LLM if the constants tool is needed
    tool_prompt = f"""
    Conversation History:
    {json.dumps(history, indent=2)}

    User's latest query: "{query}"
    
    Based on the query, do you need to look up a physical constant (e.g., speed of light, gravity)?
    Respond with a JSON object containing two keys:
    1. "use_tool": boolean (true if a constant lookup is needed, otherwise false)
    2. "constant_name": string (the name of the constant, or an empty string if not using the tool)
    """

    try:
        tool_decision_str = call_gemini_api(tool_prompt)
        tool_decision = json.loads(tool_decision_str)

        if tool_decision.get("use_tool"):
            constant_name = tool_decision.get("constant_name")
            print(f"Physics Agent decided to look up constant: {constant_name}")
            result = physics_constants_tool(constant_name)
            if result:
                return result
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Physics Agent could not parse tool decision: {e}. Proceeding without tool.")
    
    print("Physics Agent is generating a conversational response.")
    concept_prompt = "You are a friendly and helpful physics tutor. Answer the user's question clearly and concisely."
    return call_gemini_api(concept_prompt, history + [{"sender": "user", "text": query}])

def tutor_agent(query: str, history: list) -> str:
    """The main agent that determines intent and delegates to the specialist agents."""
    print("Tutor Agent received query...")
    
    intent_prompt = f"""
    You are an AI Tutor orchestrator. Your job is to classify the user's query and route it to the correct specialist.
    Based on the conversation so far and the latest query, classify the subject.
    
    Conversation History:
    {json.dumps(history, indent=2)}
    
    User's latest query: "{query}"

    Respond with a single word: 'math', 'physics', or 'general'.
    Classification:"""
    
    intent = call_gemini_api(intent_prompt).lower().strip().replace("'", "")
    print(f"Tutor Agent classified intent as: '{intent}'")

    if 'math' in intent:
        return math_agent(query, history)
    elif 'physics' in intent:
        return physics_agent(query, history)
    else:
        return "I'm sorry, I specialize in math and physics. Could you ask a question on one of those subjects?"

# --- FLASK ROUTE ---

@app.route('/query', methods=['POST'])
def handle_query():
    """Endpoint to receive user queries and conversation history."""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided.'}), 400
    
    query = data['query']
    history = data.get('history', [])
    
    response_text = tutor_agent(query, history)
    
    history.append({"sender": "user", "text": query})
    history.append({"sender": "agent", "text": response_text})
    
    return jsonify({'response': response_text, 'history': history})

@app.route('/')
def index():
    return "AI Tutor Agent (Enhanced) is running. Use the /query endpoint."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) 
    app.run(debug=True, port=port)
