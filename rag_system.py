#!/usr/bin/env python3
"""
OpenSim RAG System Implementation

This script implements the RAG (Retrieval-Augmented Generation) system for OpenSim.
It provides a query mechanism to retrieve relevant information from the vector database.
"""

import os
import json
import numpy as np
import faiss
import spacy
from flask import Flask, request, jsonify, render_template, send_from_directory
import markdown

# Configuration
VECTOR_DB_DIR = "./vector_db"
PROCESSED_DIR = "./processed_data"
TOP_K = 5  # Number of most relevant chunks to retrieve

# Load spaCy model
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")

class OpenSimRAG:
    """OpenSim RAG system for answering queries about OpenSim."""
    
    def __init__(self):
        """Initialize the RAG system."""
        self.index = None
        self.chunks = None
        self.id_mapping = None
        self.load_data()
    
    def load_data(self):
        """Load the vector database and chunks."""
        # Load FAISS index
        faiss_index_file = os.path.join(VECTOR_DB_DIR, 'faiss_index.bin')
        if os.path.exists(faiss_index_file):
            self.index = faiss.read_index(faiss_index_file)
            print(f"Loaded FAISS index with {self.index.ntotal} vectors")
        else:
            print(f"Error: FAISS index file not found at {faiss_index_file}")
            return False
        
        # Load ID mapping
        mapping_file = os.path.join(VECTOR_DB_DIR, 'id_mapping.json')
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                self.id_mapping = json.load(f)
            print(f"Loaded ID mapping with {len(self.id_mapping)} entries")
        else:
            print(f"Error: ID mapping file not found at {mapping_file}")
            return False
        
        # Load chunks
        chunks_file = os.path.join(PROCESSED_DIR, 'chunks.json')
        if os.path.exists(chunks_file):
            with open(chunks_file, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            print(f"Loaded {len(self.chunks)} chunks")
        else:
            print(f"Error: Chunks file not found at {chunks_file}")
            return False
        
        return True
    
    def get_embedding(self, text):
        """Get embedding vector for a text using spaCy."""
        # Process with spaCy
        doc = nlp(text)
        
        # Use spaCy's built-in word vectors
        if doc.vector.any():  # Check if vector is non-zero
            vec = doc.vector
        else:
            # Create a simple TF-IDF like representation
            # Count word frequencies
            word_freq = {}
            for token in doc:
                if token.is_alpha and not token.is_stop:
                    word = token.text.lower()
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Create a simple vector (300 dimensions)
            vec_size = 300
            vec = np.zeros(vec_size)
            
            # Use hash of words to determine vector positions
            for word, freq in word_freq.items():
                # Simple hash function to get a position
                pos = hash(word) % vec_size
                vec[pos] += freq
        
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        
        return vec.astype('float32')
    
    def query(self, query_text, top_k=TOP_K):
        """Query the RAG system with a question."""
        if not self.index or not self.chunks or not self.id_mapping:
            return {"error": "RAG system not properly initialized"}
        
        # Get query embedding
        query_embedding = self.get_embedding(query_text)
        query_embedding = query_embedding.reshape(1, -1)
        
        # Search the index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Get the chunks
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.id_mapping):
                continue
                
            chunk_id = self.id_mapping[idx]
            if chunk_id < 0 or chunk_id >= len(self.chunks):
                continue
                
            chunk = self.chunks[chunk_id]
            results.append({
                "chunk_text": chunk["chunk_text"],
                "source_file": chunk.get("source_file", "Unknown"),
                "title": chunk.get("Title", "Unknown"),
                "url": chunk.get("URL", ""),
                "score": float(1.0 / (1.0 + distances[0][i]))  # Convert distance to score
            })
        
        return {
            "query": query_text,
            "results": results
        }
    
    def answer_question(self, question):
        """Answer a question using the RAG system."""
        # Get relevant chunks
        query_result = self.query(question)
        
        if "error" in query_result:
            return {"error": query_result["error"]}
        
        # Extract the relevant texts
        contexts = []
        sources = []
        
        for result in query_result["results"]:
            contexts.append(result["chunk_text"])
            source = {
                "title": result.get("title", "Unknown"),
                "url": result.get("url", ""),
                "file": result.get("source_file", "")
            }
            sources.append(source)
        
        # Combine the contexts
        combined_context = "\n\n".join(contexts)
        
        # For now, we'll just return the most relevant chunks
        # In a full implementation, this would use an LLM to generate an answer
        answer = {
            "question": question,
            "answer": "Based on the OpenSim documentation, here's what I found:",
            "context": combined_context,
            "sources": sources
        }
        
        return answer

# Initialize Flask app
app = Flask(__name__, static_folder='./web/static', template_folder='./web/templates')

# Initialize RAG system
rag_system = OpenSimRAG()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def api_query():
    """API endpoint for querying the RAG system."""
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({"error": "No question provided"})
    
    result = rag_system.answer_question(question)
    return jsonify(result)

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('web/static', path)

def main():
    """Main function to run the RAG system."""
    print("Starting OpenSim RAG system...")
    
    # Check if the system is properly initialized
    if not rag_system.index or not rag_system.chunks:
        print("Error: RAG system not properly initialized")
        return
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5100, debug=True)

if __name__ == "__main__":
    main()
