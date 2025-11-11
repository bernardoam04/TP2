#!/usr/bin/env python3
"""
Flask REST API Server for Playlist Recommendation System
Provides /api/recommend endpoint that uses ML model to recommend songs
"""

import os
import pickle
import time
from datetime import datetime
from flask import Flask, request, jsonify
import threading

# Configuration
MODEL_PATH = os.environ.get('MODEL_PATH', '../models/recommendation_model.pkl')
CHECK_MODEL_INTERVAL = int(os.environ.get('CHECK_MODEL_INTERVAL', '5'))  # seconds
SERVER_VERSION = os.environ.get('SERVER_VERSION', '1.0')

app = Flask(__name__)

# Global variables for model and metadata
app.model_data = None
app.model_last_modified = None
app.model_lock = threading.Lock()

def load_model():
    """
    Load the pickled model from disk
    """
    if not os.path.exists(MODEL_PATH):
        print(f"Warning: Model file not found at {MODEL_PATH}")
        return None

    try:
        with open(MODEL_PATH, 'rb') as f:
            model_data = pickle.load(f)
        print(f"Model loaded successfully from {MODEL_PATH}")
        return model_data
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def check_and_reload_model():
    """
    Check if model file has been modified and reload if necessary
    This function runs in a background thread
    """
    while True:
        try:
            if os.path.exists(MODEL_PATH):
                current_mtime = os.path.getmtime(MODEL_PATH)

                with app.model_lock:
                    # Check if model needs reloading
                    if app.model_last_modified is None or current_mtime > app.model_last_modified:
                        print(f"\n[{datetime.now()}] Model file changed, reloading...")
                        new_model = load_model()
                        if new_model:
                            app.model_data = new_model
                            app.model_last_modified = current_mtime
                            print(f"Model reloaded! Version: {app.model_data['metadata'].get('version', 'unknown')}")
                            print(f"Model date: {app.model_data['metadata'].get('model_date', 'unknown')}")

        except Exception as e:
            print(f"Error in model checking thread: {e}")

        # Wait before checking again
        time.sleep(CHECK_MODEL_INTERVAL)

def get_recommendations(input_songs, rules, max_recommendations=10):
    """
    Generate song recommendations based on association rules

    Args:
        input_songs: List of song names the user likes
        rules: Association rules from the model
        max_recommendations: Maximum number of songs to recommend

    Returns:
        List of recommended song names
    """
    if not rules:
        return []

    # Convert input songs to set for faster lookup
    input_set = set(input_songs)
    recommendations = {}  # song -> confidence score

    # Iterate through all rules
    for rule in rules:
        antecedent = rule[0]  # IF part (can be set or single item)
        consequent = rule[1]  # THEN part (can be set or single item)
        confidence = rule[2]

        # Convert to sets if needed
        if not isinstance(antecedent, set):
            antecedent = {antecedent}
        if not isinstance(consequent, set):
            consequent = {consequent}

        # Check if all antecedent items are in user's input
        if antecedent.issubset(input_set):
            # Recommend items from consequent that user hasn't already selected
            for song in consequent:
                if song not in input_set:
                    # Keep track of highest confidence for each song
                    if song not in recommendations or confidence > recommendations[song]:
                        recommendations[song] = confidence

    # Sort by confidence and return top N
    sorted_recommendations = sorted(
        recommendations.items(),
        key=lambda x: x[1],
        reverse=True
    )[:max_recommendations]

    return [song for song, _ in sorted_recommendations]

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    POST /api/recommend

    Request body (JSON):
    {
        "songs": ["Song Name 1", "Song Name 2", ...]
    }

    Response (JSON):
    {
        "songs": ["Recommended Song 1", "Recommended Song 2", ...],
        "version": "1.0",
        "model_date": "2024-01-01T12:00:00"
    }
    """
    # Check if model is loaded
    with app.model_lock:
        if app.model_data is None:
            return jsonify({
                'error': 'Model not loaded',
                'message': 'The recommendation model is not available. Please try again later.'
            }), 503

        # Parse request
        try:
            data = request.get_json(force=True)
        except Exception as e:
            return jsonify({
                'error': 'Invalid JSON',
                'message': str(e)
            }), 400

        if not data or 'songs' not in data:
            return jsonify({
                'error': 'Missing required field',
                'message': 'Request must include a "songs" field with a list of song names'
            }), 400

        input_songs = data['songs']
        if not isinstance(input_songs, list):
            return jsonify({
                'error': 'Invalid input',
                'message': '"songs" field must be a list'
            }), 400

        # Generate recommendations
        try:
            rules = app.model_data.get('rules', [])
            recommendations = get_recommendations(input_songs, rules)

            # Build response
            response = {
                'songs': recommendations,
                'version': SERVER_VERSION,
                'model_date': app.model_data['metadata'].get('model_date', 'unknown'),
                'input_songs': input_songs,
                'num_recommendations': len(recommendations)
            }

            return jsonify(response), 200

        except Exception as e:
            return jsonify({
                'error': 'Recommendation failed',
                'message': str(e)
            }), 500

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    with app.model_lock:
        is_healthy = app.model_data is not None

    return jsonify({
        'status': 'healthy' if is_healthy else 'unhealthy',
        'model_loaded': is_healthy,
        'version': SERVER_VERSION,
        'timestamp': datetime.now().isoformat()
    }), 200 if is_healthy else 503

@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint with API information
    """
    return jsonify({
        'service': 'Playlist Recommendation API',
        'version': SERVER_VERSION,
        'endpoints': {
            '/api/recommend': 'POST - Get song recommendations',
            '/health': 'GET - Health check'
        }
    }), 200

def initialize_app():
    """
    Initialize the application by loading the model and starting background threads
    """
    print("="*60)
    print("Playlist Recommendation API Server")
    print("="*60)
    print(f"Version: {SERVER_VERSION}")
    print(f"Model path: {MODEL_PATH}")
    print(f"Model check interval: {CHECK_MODEL_INTERVAL}s")
    print()

    # Load initial model
    print("Loading initial model...")
    with app.model_lock:
        app.model_data = load_model()
        if app.model_data:
            app.model_last_modified = os.path.getmtime(MODEL_PATH)
            print(f"Initial model loaded successfully!")
        else:
            print("Warning: Could not load initial model. Server will wait for model file.")

    # Start background thread for model monitoring
    print("\nStarting model monitoring thread...")
    monitor_thread = threading.Thread(target=check_and_reload_model, daemon=True)
    monitor_thread.start()
    print("Model monitoring active!")
    print("="*60)
    print()

if __name__ == '__main__':
    # Initialize application
    initialize_app()

    # Run Flask server
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')

    print(f"Starting server on {host}:{port}")
    print(f"API endpoint: http://{host}:{port}/api/recommend")
    print()

    app.run(host=host, port=port, debug=False)
