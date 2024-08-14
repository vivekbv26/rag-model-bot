from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import logging
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
CORS(app)  # Allow Cross-Origin Requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the knowledge base file
KNOWLEDGE_BASE_PATH = r'C:\Users\AShetty\Chatbot-flexera\backend\kn.json'  # Adjust the path as needed

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

# Train the intent classifier
def train_intent_classifier(knowledge_base):
    try:
        questions = [q["question"] for q in knowledge_base["questions"]]
        answers = [q["answer"] for q in knowledge_base["questions"]]
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(questions)
        clf = MultinomialNB()
        clf.fit(X, answers)
        return vectorizer, clf
    except Exception as e:
        logging.error(f"Error training classifier: {e}")
        return None, None

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to detect abusive language using VADER
def contains_abusive_language(text):
    sentiment = analyzer.polarity_scores(text)
    return sentiment['compound'] < -0.5

# Load and train initial models
knowledge_base = load_knowledge_base(KNOWLEDGE_BASE_PATH)
vectorizer, clf = train_intent_classifier(knowledge_base)

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
        return jsonify({'response': "Please refrain from using abusive language."})
    
    # Generate response from chatbot
    if vectorizer and clf:
        X_user = vectorizer.transform([user_input])
        predicted_answer = clf.predict(X_user)[0]
        return jsonify({'response': predicted_answer})
    else:
        return jsonify({'response': "Sorry, the chatbot is not functioning properly."})

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

        # Retrain model with updated knowledge base
        global vectorizer, clf
        vectorizer, clf = train_intent_classifier(knowledge_base)
        logging.info("Model retrained successfully.")

        return jsonify({'status': 'success', 'message': 'Question added and model retrained.'})

    except Exception as e:
        logging.error(f"Error adding question: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to add question.'})

# Placeholder functions for Flexera and Gemini responses
def get_flexera_response(query):
    # Placeholder function to call Flexera API
    return "Flexera API response"

def get_gemini_llm_response(query):
    # Placeholder function to call Gemini LLM
    return "Gemini LLM response"

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)