import os
import re
import requests
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get('API_KEY')
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

# --- Gemini API Call ---
def call_gemini_api(prompt, conversation_history=None):
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY environment variable is not set."

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
        
        return "Sorry, the API response was not in the expected format."
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
        return f"The result of `{expression}` is **{result}**."
    except Exception as e:
        return f"I encountered an error trying to calculate that: {e}."

def physics_constants_tool(constant_name: str) -> str | None:
    constants = {
        "speed of light": "299,792,458 m/s",
        "gravitational constant": "6.67430 x 10^-11 N(m/kg)^2",
        "planck's constant": "6.62607015 x 10^-34 J*s",
        "gravity": "9.8 m/s^2 (on Earth)"
    }
    for key in constants:
        if key in constant_name.lower():
            return f"The value of **{key}** is `{constants[key]}`."
    return None

def code_generator_tool(task_description: str) -> str:
    print(f"Code Generator Tool activated for: {task_description}")
    code_prompt = f"""
    You are a helpful code assistant.
    Generate a clean, well-commented Python code snippet for the following task.
    Do not include any explanation outside of the code block.
    Task: "{task_description}"
    """
    generated_code = call_gemini_api(code_prompt)
    return f"Certainly! Here is a Python script for '{task_description}':\n\n{generated_code}"

# --- AGENT DEFINITIONS ---

def math_agent(query: str, history: list) -> str:
    print("Delegating to Math Agent...")
    tool_prompt = f"""Based on the user's latest query, do they need to perform a calculation?
    Query: "{query}"
    Respond with a JSON object: {{"use_tool": boolean, "expression": "the calculation or empty string"}}
    """
    try:
        decision_str = call_gemini_api(tool_prompt)
        decision = json.loads(decision_str)
        if decision.get("use_tool"):
            return calculator_tool(decision.get("expression"))
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Math Agent could not parse tool decision: {e}.")
    
    concept_prompt = f"You are a friendly math tutor. Answer the user's question clearly. Use Markdown for formatting (e.g., lists, bold text)."
    return call_gemini_api(concept_prompt, history + [{"sender": "user", "text": query}])


def physics_agent(query: str, history: list) -> str:
    print("Delegating to Physics Agent...")
    tool_prompt = f"""Based on the query, do they need a physical constant?
    Query: "{query}"
    Respond with a JSON object: {{"use_tool": boolean, "constant_name": "the constant or empty string"}}
    """
    try:
        decision_str = call_gemini_api(tool_prompt)
        decision = json.loads(decision_str)
        if decision.get("use_tool"):
            result = physics_constants_tool(decision.get("constant_name"))
            if result: return result
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Physics Agent could not parse tool decision: {e}.")

    concept_prompt = "You are a helpful physics tutor. Answer clearly. Use Markdown for formatting."
    return call_gemini_api(concept_prompt, history + [{"sender": "user", "text": query}])


def general_knowledge_agent(query: str, history: list) -> str:
    print("Delegating to General Knowledge Agent...")
    tool_prompt = f"""Analyze the user's query. Does it ask for a Python script or code?
    Query: "{query}"
    Respond with JSON: {{"use_tool": boolean, "task_description": "the task or empty string"}}
    """
    try:
        decision_str = call_gemini_api(tool_prompt)
        decision = json.loads(decision_str)
        if decision.get("use_tool"):
            return code_generator_tool(decision.get("task_description"))
    except (json.JSONDecodeError, KeyError) as e:
        print(f"General Agent could not parse tool decision: {e}.")

    concept_prompt = "You are a helpful general assistant. Answer the user's question. Use Markdown for formatting."
    return call_gemini_api(concept_prompt, history + [{"sender": "user", "text": query}])


def tutor_agent(query: str, history: list) -> str:
    print("Tutor Agent received query...")
    intent_prompt = f"""
    Analyze the user's query and classify its primary subject based on the conversation.
    
    Conversation History:
    {json.dumps(history, indent=2)}
    
    User's latest query: "{query}"

    Respond with a single word: 'math', 'physics', or 'general'.
    Classification:"""
    
    intent = call_gemini_api(intent_prompt).lower().strip().replace("'", "").replace(".", "")
    print(f"Tutor Agent classified intent as: '{intent}'")

    if 'math' in intent:
        return math_agent(query, history)
    elif 'physics' in intent:
        return physics_agent(query, history)
    else:
        return general_knowledge_agent(query, history)

# --- FLASK ROUTE ---

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided.'}), 400
    
    query = data['query']
    history = data.get('history', [])
    
    response_text = tutor_agent(query, history)
    
    updated_history = history + [
        {"sender": "user", "text": query},
        {"sender": "agent", "text": response_text}
    ]
    
    return jsonify({'response': response_text, 'history': updated_history})

@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000)) 
    app.run(host='0.0.0.0', port=port)
