#!/bin/bash
# Setup script for OpenSim RAG project

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv env
source env/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo "Setup complete! You can now run the application with:"
echo "source env/bin/activate"
echo "python app.py"
