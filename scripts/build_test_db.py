#!/usr/bin/env python3
"""
OpenSim RAG System - Simplified Vector Database Builder (Fixed)

This script builds a smaller vector database for testing purposes.
It uses a subset of the processed chunks to create a FAISS index quickly.
"""

import os
import json
import numpy as np
import faiss
import spacy

# Configuration
PROCESSED_DIR = "../processed_data"
VECTOR_DB_DIR = "../vector_db"
MAX_CHUNKS = 1000  # Limit number of chunks for faster processing
EMBEDDING_SIZE = 300  # Fixed embedding size

# Create vector_db directory if it doesn't exist
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

# Load spaCy model
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")

def get_embedding(text):
    """Get embedding vector for a text using spaCy."""
    # Process with spaCy
    doc = nlp(text)
    
    # Create a fixed-size vector
    vec = np.zeros(EMBEDDING_SIZE, dtype=np.float32)
    
    # Use spaCy's built-in word vectors if available
    if doc.vector.any() and len(doc.vector) == EMBEDDING_SIZE:
        return doc.vector
    
    # Create a simple TF-IDF like representation
    # Count word frequencies
    word_freq = {}
    for token in doc:
        if token.is_alpha and not token.is_stop:
            word = token.text.lower()
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Use hash of words to determine vector positions
    for word, freq in word_freq.items():
        # Simple hash function to get a position
        pos = hash(word) % EMBEDDING_SIZE
        vec[pos] += freq
    
    # Normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    
    return vec

def build_vector_database():
    """Build a FAISS vector database from the chunks."""
    print("Building vector database (simplified version)...")
    
    # Load chunks
    chunks_file = os.path.join(PROCESSED_DIR, 'chunks.json')
    if not os.path.exists(chunks_file):
        print(f"Error: Chunks file not found at {chunks_file}")
        return False
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        all_chunks = json.load(f)
    
    print(f"Loaded {len(all_chunks)} chunks")
    
    # Limit number of chunks for faster processing
    chunks = all_chunks[:MAX_CHUNKS]
    print(f"Using {len(chunks)} chunks for simplified vector database")
    
    # Generate embeddings for each chunk
    embeddings = []
    chunk_ids = []
    
    print("Generating embeddings...")
    for i, chunk in enumerate(chunks):
        if i % 100 == 0:
            print(f"Processing chunk {i}/{len(chunks)}")
        
        text = chunk['chunk_text']
        embedding = get_embedding(text)
        
        # Ensure embedding is the correct shape
        if embedding.shape != (EMBEDDING_SIZE,):
            print(f"Warning: Embedding {i} has shape {embedding.shape}, fixing...")
            embedding = np.zeros(EMBEDDING_SIZE, dtype=np.float32)
        
        embeddings.append(embedding)
        chunk_ids.append(i)
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings, dtype=np.float32)
    
    # Create FAISS index
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    
    # Save the index
    faiss_index_file = os.path.join(VECTOR_DB_DIR, 'faiss_index.bin')
    faiss.write_index(index, faiss_index_file)
    
    # Save the mapping from FAISS IDs to chunk IDs
    mapping_file = os.path.join(VECTOR_DB_DIR, 'id_mapping.json')
    with open(mapping_file, 'w') as f:
        json.dump(chunk_ids, f)
    
    # Also save a mapping from chunk IDs to original chunks
    chunk_mapping_file = os.path.join(VECTOR_DB_DIR, 'chunk_mapping.json')
    chunk_mapping = {}
    for i, chunk_id in enumerate(chunk_ids):
        chunk_mapping[str(i)] = chunks[chunk_id]
    
    with open(chunk_mapping_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_mapping, f)
    
    print(f"Vector database built with {len(embeddings)} vectors of dimension {dimension}")
    print(f"FAISS index saved to {faiss_index_file}")
    print(f"ID mapping saved to {mapping_file}")
    print(f"Chunk mapping saved to {chunk_mapping_file}")
    
    return True

def main():
    """Main function to build the vector database."""
    print("Starting simplified vector database builder...")
    
    # Build vector database
    success = build_vector_database()
    
    if success:
        print("Vector database built successfully!")
    else:
        print("Failed to build vector database.")

if __name__ == "__main__":
    main()
