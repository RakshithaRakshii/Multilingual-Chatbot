from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from deep_translator import GoogleTranslator
import os
import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Embedding, Bidirectional, GRU, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
import numpy as np
import re
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# API configuration - use your existing API key
API_KEY = "AIzaSyDFOnr2M_F8OLogjqxjl31wsriyA7IJ-g0"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
HEADERS = {"Content-Type": "application/json"}

# Dictionary of supported languages with their codes
LANGUAGE_CODES = {
    'english': 'en',
    'tamil': 'ta',
    'hindi': 'hi',
    'telugu': 'te',
    'malayalam': 'ml'
}

# Store conversation history
conversation_history = {}

# Parameters for the text generation model
VOCAB_SIZE = 10000
EMBEDDING_DIM = 128
GRU_UNITS = 256
SEQ_LENGTH = 20
NUM_COMPLETIONS = 5  # Number of different completions to generate

# Load and preprocess data
def load_and_preprocess_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text

# Initialize and train model
def initialize_model():
    global tokenizer, model, total_words
    
    # Load dataset
    text = load_and_preprocess_data(r"Conversation.csv")
    
    # Initialize tokenizer
    tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token='<OOV>')
    tokenizer.fit_on_texts([text])
    word_index = tokenizer.word_index
    total_words = len(word_index) + 1
    
    # Create training sequences
    input_sequences = []
    for line in text.split('\n'):
        if not line.strip():
            continue
        token_list = tokenizer.texts_to_sequences([line])[0]
        for i in range(1, len(token_list)):
            n_gram_sequence = token_list[:i+1]
            input_sequences.append(n_gram_sequence)
    
    # Pad sequences
    input_sequences = pad_sequences(input_sequences, maxlen=SEQ_LENGTH+1, padding='pre')
    
    # Split into predictors and target
    X = input_sequences[:, :-1]
    y = input_sequences[:, -1]
    y = to_categorical(y, num_classes=total_words)
    
    # Create and train model
    model = create_model(total_words, SEQ_LENGTH, EMBEDDING_DIM, GRU_UNITS)
    model.fit(X, y, batch_size=64, epochs=10, validation_split=0.2)
    
    return model, tokenizer, total_words

# Model creation function
def create_model(total_words, seq_length, embedding_dim, gru_units):
    inputs = Input(shape=(seq_length,))
    x = Embedding(total_words, embedding_dim, input_length=seq_length)(inputs)
    x = Bidirectional(GRU(gru_units, return_sequences=False))(x)
    x = Dropout(0.2)(x)
    outputs = Dense(total_words, activation='softmax')(x)
    model = Model(inputs, outputs)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# Modified prediction function to generate a single completion with one word
def predict_next_words(model, tokenizer, text, num_words=1, temperature=1.0):
    original_text = text
    for _ in range(num_words):
        token_list = tokenizer.texts_to_sequences([text])[0]
        token_list = pad_sequences([token_list], maxlen=SEQ_LENGTH, padding='pre')
        predicted_probs = model.predict(token_list, verbose=0)[0]
        
        # Apply temperature for randomness
        predicted_probs = np.asarray(predicted_probs).astype('float64')
        predicted_probs = np.log(predicted_probs) / temperature
        exp_preds = np.exp(predicted_probs)
        predicted_probs = exp_preds / np.sum(exp_preds)
        
        # Sample from the distribution
        probas = np.random.multinomial(1, predicted_probs, 1)
        predicted_index = np.argmax(probas)
        
        output_word = ""
        for word, index in tokenizer.word_index.items():
            if index == predicted_index:
                output_word = word
                break
        text += " " + output_word
    return text

# Generate multiple different completions
def generate_completions(model, tokenizer, text, num_completions=5, num_words=5):
    completions = []
    for i in range(num_completions):
        # Use different temperatures for variety
        temperature = 0.7 + (i * 0.1)  # Increase temperature for more diversity
        completion = predict_next_words(model, tokenizer, text, num_words, temperature)
        completions.append(completion)
    return completions

# Initialize model at startup
print("Initializing and training text generation model...")
model, tokenizer, total_words = initialize_model()
print("Model initialized successfully!")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get data from request
        data = request.json
        user_message = data.get('message', '')
        language = data.get('language', 'english').lower()
        session_id = data.get('session_id', 'default')
        
        # Print debug info
        print(f"Received message: '{user_message}' in language: '{language}'")
        
        # Get language code
        lang_code = LANGUAGE_CODES.get(language, 'en')
        
        # Initialize conversation history for this session if it doesn't exist
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Translate user message to English if not in English
        if lang_code != 'en':
            translator_to_en = GoogleTranslator(source=lang_code, target='en')
            translated_input = translator_to_en.translate(user_message)
            print(f"Translated to English: '{translated_input}'")
        else:
            translated_input = user_message
            print("No translation needed (English input)")
        
        # Add user message to conversation history
        conversation_history[session_id].append({"role": "user", "parts": [{"text": translated_input}]})
        
        # Prepare request for Gemini API
        gemini_request = {
            "contents": conversation_history[session_id]
        }
        
        # Call Gemini API
        print("Calling Gemini API...")
        response = requests.post(URL, headers=HEADERS, json=gemini_request)
        
        if response.status_code == 200:
            response_json = response.json()
            
            # Extract AI response
            ai_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
            print(f"AI response: '{ai_text}'")
            
            # Add AI response to conversation history
            conversation_history[session_id].append({"role": "model", "parts": [{"text": ai_text}]})
            
            # Translate AI response back to user's language if not English
            if lang_code != 'en':
                translator_from_en = GoogleTranslator(source='en', target=lang_code)
                translated_response = translator_from_en.translate(ai_text)
                print(f"Translated response: '{translated_response}'")
            else:
                translated_response = ai_text
                print("No translation needed for response (English)")
            
            # Limit conversation history length to avoid token issues
            if len(conversation_history[session_id]) > 10:
                conversation_history[session_id] = conversation_history[session_id][-10:]
            
            # Return response
            return jsonify({
                'response': translated_response
            })
        else:
            print(f"API Error: {response.status_code}, {response.text}")
            return jsonify({
                'error': f"API Error: {response.status_code}",
                'response': "Sorry, I'm having trouble connecting to the AI service."
            }), 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': str(e),
            'response': "An error occurred. Please try again."
        }), 500

@app.route('/suggest', methods=['POST'])
def suggest():
    try:
        # Get data from request
        data = request.json
        current_text = data.get('current_text', '')
        language = data.get('language', 'english').lower()
        
        # Print debug info
        print(f"Received suggestion request for: '{current_text}' in language: '{language}'")
        
        # Get language code
        lang_code = LANGUAGE_CODES.get(language, 'en')
        
        # Translate user text to English if not in English
        if lang_code != 'en':
            translator_to_en = GoogleTranslator(source=lang_code, target='en')
            translated_input = translator_to_en.translate(current_text)
            print(f"Translated to English: '{translated_input}'")
        else:
            translated_input = current_text
        
        # For empty input, use some generic starter words
        if not current_text.strip():
            # Generate some generic starting phrases using our model
            starter_phrases = ["hello", "hi", "hey", "good", "the"]
            suggestions = []
            
            # Generate predictions for each starter phrase - just one word each
            for phrase in starter_phrases:
                completion = predict_next_words(model, tokenizer, phrase, num_words=1, temperature=1.0)
                suggestions.append(completion)
                
            # Remove duplicates and limit to 5
            suggestions = list(dict.fromkeys(suggestions))[:5]
        else:
            # Use our model to generate suggestions based on current text
            suggestions = []
            # Generate multiple suggestions with different temperatures
            for i in range(5):
                temperature = 0.7 + (i * 0.15)  # Vary temperature for diversity
                completion = predict_next_words(model, tokenizer, translated_input, num_words=1, temperature=temperature)
                suggestions.append(completion)
            
            # Ensure we have unique suggestions
            suggestions = list(dict.fromkeys(suggestions))
            
            # If we don't have enough unique suggestions, try different temperatures
            if len(suggestions) < 3:
                for i in range(5):
                    temperature = 1.2 + (i * 0.2)  # Try higher temperatures
                    completion = predict_next_words(model, tokenizer, translated_input, num_words=1, temperature=temperature)
                    if completion not in suggestions:
                        suggestions.append(completion)
                    if len(suggestions) >= 5:
                        break
            
            # Limit to 5 suggestions
            suggestions = suggestions[:5]
        
        # Translate suggestions if not in English
        if lang_code != 'en':
            try:
                translator_from_en = GoogleTranslator(source='en', target=lang_code)
                translated_suggestions = [translator_from_en.translate(sugg) for sugg in suggestions]
                suggestions = translated_suggestions
            except Exception as e:
                print(f"Error translating suggestions: {e}")
        
        return jsonify({'suggestions': suggestions})
            
    except Exception as e:
        print(f"Error in suggestions: {str(e)}")
        return jsonify({
            'error': str(e),
            'suggestions': []
        }), 500

@app.route('/reset', methods=['POST'])
def reset():
    data = request.json
    session_id = data.get('session_id', 'default')
    
    if session_id in conversation_history:
        conversation_history[session_id] = []
        
    return jsonify({
        'success': True,
        'message': 'Conversation reset successfully'
    })

if __name__ == '__main__':
    print("Starting server on http://localhost:5000")
    app.run(debug=True)