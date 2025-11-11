#!/bin/bash
# Quick local testing script for the playlist recommendation system

set -e  # Exit on error

echo "=================================="
echo "Playlist Recommendation System"
echo "Local Testing Script"
echo "=================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.deps_installed" ]; then
    echo "Installing dependencies..."
    pip install -q -r ml/requirements.txt -r api/requirements.txt -r client/requirements.txt
    touch venv/.deps_installed
    echo "Dependencies installed!"
fi

# Check if model exists
if [ ! -f "models/recommendation_model.pkl" ]; then
    echo ""
    echo "Generating ML model..."
    cd ml
    python model_generator.py
    cd ..
    echo "Model generated successfully!"
fi

# Start API server in background
echo ""
echo "Starting API server..."
cd api
python app.py > ../api_server.log 2>&1 &
API_PID=$!
cd ..
echo "API server started (PID: $API_PID)"

# Wait for server to be ready
echo "Waiting for server to initialize..."
sleep 3

# Test the API
echo ""
echo "Testing API with sample songs..."
echo "=================================="
python client/client.py "HUMBLE." "DNA."

echo ""
echo "=================================="
echo "Test completed successfully!"
echo ""
echo "To stop the API server, run:"
echo "  kill $API_PID"
echo ""
echo "To test with different songs, run:"
echo "  python client/client.py \"Song 1\" \"Song 2\""
echo "=================================="
