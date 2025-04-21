#!/usr/bin/env python3
"""
OpenSim RAG System - Improved App with Code Formatting

This script integrates all components of the OpenSim RAG system and runs the web application.
Uses Sentence Transformers for retrieval and Mistral for generating responses.
"""

import os
import json
import numpy as np
import faiss
import re
from flask import Flask, request, jsonify, render_template, send_from_directory
import markdown

# Import the LLM helper
from llm_helper import MistralLLM
from code_formatter import CodeFormattingLLM  # Import your existing CodeFormattingLLM

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Main folder containing app.py
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed_data")
MODELS_DIR = os.path.join(BASE_DIR, "models")  # For storing models
TOP_K = 5  # Number of most relevant chunks to retrieve

# Create directory for models if it doesn't exist
os.makedirs(MODELS_DIR, exist_ok=True)

# Initialize the LLM (will be loaded when first needed)
llm = None

class OpenSimRAG:
    """OpenSim RAG system for answering queries about OpenSim."""
    
    def __init__(self):
        """Initialize the RAG system."""
        self.index = None
        self.chunks = None
        self.id_mapping = None
        self.embedding_model = None
        self.embedding_size = None
        self.load_embedding_model()
        self.load_data()
    
    def load_embedding_model(self):
        """Load the Sentence Transformers model for embeddings."""
        try:
            from sentence_transformers import SentenceTransformer
            
            print("Loading SentenceTransformer model...")
            model_name = 'all-MiniLM-L6-v2'  # Same model used for creating the database
            self.embedding_model = SentenceTransformer(model_name, cache_folder=MODELS_DIR)
            self.embedding_size = self.embedding_model.get_sentence_embedding_dimension()
            print(f"Embedding model loaded. Dimension: {self.embedding_size}")
        except ImportError:
            print("SentenceTransformers not installed. Installing now...")
            import subprocess
            subprocess.check_call(["pip", "install", "sentence-transformers"])
            
            from sentence_transformers import SentenceTransformer
            model_name = 'all-MiniLM-L6-v2'
            self.embedding_model = SentenceTransformer(model_name, cache_folder=MODELS_DIR)
            self.embedding_size = self.embedding_model.get_sentence_embedding_dimension()
            print(f"Embedding model loaded. Dimension: {self.embedding_size}")
    
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
        
        # Try to load successful chunks first, fall back to regular chunks
        successful_chunks_file = os.path.join(VECTOR_DB_DIR, 'successful_chunks.json')
        chunks_file = os.path.join(PROCESSED_DIR, 'chunks.json')
        
        if os.path.exists(successful_chunks_file):
            with open(successful_chunks_file, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            print(f"Loaded {len(self.chunks)} successful chunks from vector_db")
        elif os.path.exists(chunks_file):
            with open(chunks_file, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            print(f"Loaded {len(self.chunks)} chunks from processed_data")
        else:
            print(f"Error: Neither successful_chunks.json nor chunks.json found")
            return False
        
        return True
    
    def get_embedding(self, text):
        """Get embedding vector for a text using Sentence Transformers."""
        try:
            # Handle empty or very short text
            if not text or len(text.strip()) < 5:
                return np.zeros(self.embedding_size, dtype=np.float32)
            
            # Limit text length to avoid memory issues
            if len(text) > 10000:
                text = text[:10000]
            
            # Get embedding from Sentence Transformers
            embedding = self.embedding_model.encode(text, show_progress_bar=False)
            
            # Ensure correct type
            embedding = np.array(embedding, dtype=np.float32)
            
            # Normalize to unit length
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding
        
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector in case of error
            return np.zeros(self.embedding_size, dtype=np.float32)
    
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
            # Check if index is valid
            if idx < 0 or idx >= len(self.id_mapping):
                continue
                
            # Get corresponding chunk ID
            chunk_id = self.id_mapping[idx]
            
            # Check if chunk ID is valid
            if chunk_id < 0 or chunk_id >= len(self.chunks):
                continue
                
            # Get the chunk and add to results
            chunk = self.chunks[chunk_id]
            
            # Extract metadata - handling both original and fixed keys
            chunk_title = chunk.get("title", chunk.get("Title", "Unknown"))
            chunk_url = chunk.get("url", chunk.get("URL", ""))
            
            results.append({
                "chunk_text": chunk["chunk_text"],
                "source_file": chunk.get("source_file", "Unknown"),
                "title": chunk_title,
                "url": chunk_url,
                "score": float(1.0 / (1.0 + distances[0][i]))  # Convert distance to score
            })
        
        return {
            "query": query_text,
            "results": results
        }
    
    def format_answer(self, question, contexts, sources):
        """Format the answer using the retrieved contexts."""
        # In a full implementation, this would use an LLM to generate an answer
        # For now, we'll just format the retrieved chunks nicely
        
        # Format the answer
        answer = f"# Query: {question}\n\n"
        answer += "## Relevant Information\n\n"
        
        # Add each context with its source
        for i, (context, source) in enumerate(zip(contexts, sources)):
            source_text = f"{source['title']}"
            if source['url']:
                source_text += f" ([link]({source['url']}))"
                
            answer += f"### Source {i+1}: {source_text}\n\n"
            answer += f"{context}\n\n"
            
        # Convert markdown to HTML
        html_answer = markdown.markdown(answer)
        
        return html_answer
    
    def answer_question(self, question):
        """Answer a question using the RAG system with LLM-generated responses."""
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
        
        # Generate LLM response
        global llm
        if llm is None:
            # Create base LLM
            base_llm = MistralLLM()
            
            # Check if this is a code-related question
            code_keywords = ["code", "script", "programming", "function", "class", 
                            "implement", "python", "example", "syntax", "how to write"]
            is_code_question = any(keyword in question.lower() for keyword in code_keywords)
            
            # Only wrap with CodeFormattingLLM if enhanced formatting is needed
            if is_code_question:
                llm = CodeFormattingLLM(base_llm)
                print("Enhanced LLM initialized with code formatting capabilities")
            else:
                llm = base_llm
                print("Standard LLM initialized")
        
        try:
            # Generate response using LLM
            generated_answer = llm.generate_response(question, contexts)
            
            # Check if response contains code blocks
            has_code = bool(re.search(r"```\w*\n.*?\n```", generated_answer, re.DOTALL))
            
            # Format sources for display
            formatted_sources = []
            for i, source in enumerate(sources):
                formatted_sources.append({
                    "index": i+1,
                    "title": source["title"],
                    "url": source["url"],
                    "file": source["file"]
                })
            
            # Return the results with both generated answer and sources
            answer = {
                "question": question,
                "answer": generated_answer,
                "sources": formatted_sources,
                "source_documents": combined_context,
                "has_code": has_code
            }
            
            return answer
            
        except Exception as e:
            print(f"Error using LLM for response generation: {e}")
            
            # Fall back to the original formatting method if LLM fails
            formatted_answer = self.format_answer(question, contexts, sources)
            
            # Return the results with the formatted answer as fallback
            answer = {
                "question": question,
                "answer": "Based on the OpenSim documentation, here's what I found:",
                "formatted_answer": formatted_answer,
                "context": combined_context,
                "sources": sources
            }
            
            return answer

# Initialize Flask app
app = Flask(__name__, static_folder='./web/static', template_folder='./web/templates')

# Initialize RAG system
print("Initializing OpenSim RAG system...")
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
    """Main function to run the integrated OpenSim RAG system."""
    print("Starting OpenSim RAG system...")
    
    # Check if the system is properly initialized
    if not rag_system.index or not rag_system.chunks:
        print("Error: RAG system not properly initialized")
        return
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5100, debug=True)

if __name__ == "__main__":
    main()