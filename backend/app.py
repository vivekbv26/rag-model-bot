from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import logging
import time
import numpy as np
import torch
import faiss
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
from datetime import datetime
from textblob import TextBlob

app = Flask(__name__)
CORS(app)  # Allow Cross-Origin Requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

KNOWLEDGE_BASE_PATH = r'kn3.json'
LOG_FILE_PATH = r'chatbot_logs.json'

# Load the knowledge base
def load_knowledge_base(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        logging.error(f"Error loading knowledge base: {e}")
        return {"questions": []}

# Save the knowledge base
def save_knowledge_base(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        logging.error(f"Error saving knowledge base: {e}")

# Retriever class for retrieving the most relevant answers
class Retriever:
    def __init__(self, model_name='distilbert-base-uncased'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.index = None  # For FAISS indexing
        self.knowledge_base = []

    def embed_text(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state[:, 0, :].detach().numpy()

    def build_index(self, knowledge_base):
        self.knowledge_base = knowledge_base
        embeddings = []
        for item in knowledge_base:
            embeddings.append(self.embed_text(item['question']))
        embeddings = np.vstack(embeddings)

        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def retrieve(self, question, top_k=1):  # Adjust top_k to limit to the most relevant
        question_embedding = self.embed_text(question)
        distances, indices = self.index.search(question_embedding, top_k)
        return indices[0]  # Return indices of the most similar question(s)

# Generator class for generating answers based on retrieved context
class Generator:
    def __init__(self, model_name='distilgpt2'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

    def generate(self, context, question):
        input_text = f"{context} {question}"
        inputs = self.tokenizer.encode(input_text, return_tensors='pt', truncation=True, max_length=256)  # Limit input length
        outputs = self.model.generate(inputs, max_new_tokens=100, repetition_penalty=2.0)  # Use repetition_penalty to reduce redundancy
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

# Function to detect abusive language using TextBlob sentiment analysis
def contains_abusive_language(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity < -0.5

# Function to log the conversation
def log_conversation(question, answer):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'question': question,
        'answer': answer
    }
   
    try:
        # Load existing logs
        try:
            with open(LOG_FILE_PATH, 'r') as log_file:
                logs = json.load(log_file)
        except FileNotFoundError:
            logs = []
       
        # Add new entry
        logs.append(log_entry)
       
        # Save updated logs
        with open(LOG_FILE_PATH, 'w') as log_file:
            json.dump(logs, log_file, indent=4)
       
        logging.info(f"Logged conversation: {log_entry}")
       
    except Exception as e:
        logging.error(f"Error logging conversation: {e}")

# Chatbot class integrating the Retriever and Generator
class Chatbot:
    def __init__(self, knowledge_base_path):
        # Load the knowledge base
        self.knowledge_base = load_knowledge_base(knowledge_base_path)

        # Initialize retriever and generator
        self.retriever = Retriever()
        self.retriever.build_index(self.knowledge_base["questions"])

        self.generator = Generator()

    def answer_question(self, question):
        # Retrieve relevant context from the knowledge base
        retrieved_indices = self.retriever.retrieve(question)
        context = " ".join([self.knowledge_base["questions"][idx]['answer'] for idx in retrieved_indices])

        # Generate the final answer
        return self.generator.generate(context, question)

# Initialize the chatbot
bot = Chatbot(KNOWLEDGE_BASE_PATH)

# Home route to serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# API route for chatbot response
@app.route('/get-response', methods=['POST'])
def get_flexhack_response():
    time.sleep(2)
    user_input = request.json.get('message')
   
    if not user_input:
        return jsonify({'response': "No input provided."})
   
    # Detect abusive language
    if contains_abusive_language(user_input):
        response = "Please refrain from using abusive language."
        log_conversation(user_input, response)
        return jsonify({'response': response})
   
    # Get response from the chatbot
    response = bot.answer_question(user_input)
   
    log_conversation(user_input, response)
    return jsonify({'response': response})

@app.route('/add-question', methods=['POST'])
def add_question():
    user_input = request.json.get('question')
    user_response = request.json.get('response')
   
    if not user_input or not user_response:
        return jsonify({'status': 'error', 'message': 'Question and response are required.'})

    try:
        # Load and update knowledge base
        knowledge_base = load_knowledge_base(KNOWLEDGE_BASE_PATH)
        new_entry = {"question": user_input, "answer": user_response}
        knowledge_base["questions"].append(new_entry)
       
        # Save updated knowledge base
        save_knowledge_base(KNOWLEDGE_BASE_PATH, knowledge_base)
        logging.info(f"Added new entry: {new_entry}")

        # Retrain retriever model with updated knowledge base
        bot.retriever.build_index(knowledge_base["questions"])
        logging.info("Model retrained successfully.")

        return jsonify({'status': 'success', 'message': 'Question added and model retrained.'})

    except Exception as e:
        logging.error(f"Error adding question: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to add question.'})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
