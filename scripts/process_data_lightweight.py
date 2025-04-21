#!/usr/bin/env python3
"""
OpenSim RAG Data Processor with Improved Embeddings

This script enhances the embedding quality by using Sentence Transformers.
"""

import os
import re
import json
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm
import faiss

# Configuration
DATA_DIR = "../data"
PROCESSED_DIR = "../processed_data"
VECTOR_DB_DIR = "../vector_db"
MODELS_DIR = "../models"  # Directory to store downloaded models
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Character overlap between chunks
MAX_CHUNKS_PER_FILE = 50  # Maximum number of chunks to extract from a single file
EMBEDDING_DIMENSION = 384  # Will be set based on the model

# Create directories if they don't exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Setup for the embedding model
def setup_embedding_model():
    """Set up the Sentence Transformers model for embeddings."""
    try:
        from sentence_transformers import SentenceTransformer
        
        # Choose a small but effective model (about 40-80MB)
        # 'all-MiniLM-L6-v2' is a good balance of size and quality
        model_name = 'all-MiniLM-L6-v2'
        print(f"Loading SentenceTransformer model: {model_name}")
        
        model = SentenceTransformer(model_name, cache_folder=MODELS_DIR)
        
        # Update the global embedding dimension based on the model
        global EMBEDDING_DIMENSION
        EMBEDDING_DIMENSION = model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {EMBEDDING_DIMENSION}")
        
        return model
    
    except ImportError:
        print("SentenceTransformers not installed. Installing now...")
        import subprocess
        subprocess.check_call(["pip", "install", "sentence-transformers"])
        
        from sentence_transformers import SentenceTransformer
        model_name = 'all-MiniLM-L6-v2'
        model = SentenceTransformer(model_name, cache_folder=MODELS_DIR)
        
        
        EMBEDDING_DIMENSION = model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {EMBEDDING_DIMENSION}")
        
        return model

# Initialize the embedding model (only once)
print("Setting up the embedding model...")
embedding_model = setup_embedding_model()

def clean_text(text):
    """Clean and normalize text."""
    # Replace multiple newlines with a single one
    text = re.sub(r'\n+', '\n', text)
    
    # Replace multiple spaces with a single one
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters and digits (keep letters, spaces, and basic punctuation)
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    
    return text.strip()

def create_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP, max_chunks=MAX_CHUNKS_PER_FILE):
    """Split text into overlapping chunks."""
    chunks = []
    
    if len(text) <= chunk_size:
        chunks.append(text)
    else:
        start = 0
        while start < len(text) and len(chunks) < max_chunks:
            end = start + chunk_size
            
            # Adjust end to not break in the middle of a sentence if possible
            if end < len(text):
                # Try to find a sentence boundary
                sentence_end = text.rfind('. ', start, end)
                if sentence_end != -1:
                    end = sentence_end + 1
            
            # Add the chunk
            chunks.append(text[start:end])
            
            # Move start position for next chunk, considering overlap
            start = end - overlap
    
    return chunks

def get_embedding(text):
    """Get embedding vector for a text using Sentence Transformers."""
    # Handle empty or very short text
    if not text or len(text.strip()) < 5:
        return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)
    
    try:
        # Limit text length to avoid memory issues with very long texts
        if len(text) > 10000:
            text = text[:10000]
        
        # Get embedding from Sentence Transformers
        embedding = embedding_model.encode(text, show_progress_bar=False)
        
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
        return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)

def process_file(file_path):
    """Process a single file and return chunks with metadata."""
    print(f"Processing {file_path}")
    
    try:
        # Try multiple encodings in case of issues
        content = None
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"Could not read {file_path} with any encoding")
            return []
        
        # Extract metadata from the first few lines if available
        lines = content.split('\n')
        metadata = {}
        
        for i, line in enumerate(lines[:10]):
            if ': ' in line:
                key, value = line.split(': ', 1)
                metadata[key] = value
            
            # Stop if we hit an empty line after finding some metadata
            if not line.strip() and metadata:
                content = '\n'.join(lines[i+1:])
                break
        
        # Add basic file metadata
        file_name = os.path.basename(file_path)
        metadata['file_name'] = file_name
        
        # Clean the text
        cleaned_text = clean_text(content)
        
        # Create chunks
        text_chunks = create_chunks(cleaned_text)
        
        # Prepare result
        result = []
        for i, chunk in enumerate(text_chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'source_file': file_path,
                'chunk_id': i,
                'chunk_text': chunk
            })
            result.append(chunk_metadata)
        
        return result
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def process_all_files():
    """Process all files in the data directory."""
    # Get all text files
    all_files = []
    for subdir in ['confluence_docs', 'api_docs', 'github_docs', 'papers']:
        dir_path = os.path.join(DATA_DIR, subdir)
        if os.path.exists(dir_path):
            files = glob.glob(os.path.join(dir_path, '*.txt'))
            all_files.extend(files)
    
    print(f"Found {len(all_files)} files to process")
    
    # Process files and collect chunks
    all_chunks = []
    
    # Process each file
    for file_path in tqdm(all_files):
        chunks = process_file(file_path)
        all_chunks.extend(chunks)
    
    print(f"Created {len(all_chunks)} chunks from {len(all_files)} files")
    
    # Save chunks to file
    chunks_file = os.path.join(PROCESSED_DIR, 'chunks.json')
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2)
    
    # Create DataFrame for easier processing
    df = pd.DataFrame(all_chunks)
    csv_file = os.path.join(PROCESSED_DIR, 'chunks.csv')
    df.to_csv(csv_file, index=False)
    
    return all_chunks

def build_vector_database(chunks):
    """Build a FAISS vector database from the chunks."""
    print("Building vector database...")
    
    # Generate embeddings for each chunk
    embeddings = []
    chunk_ids = []
    successful_chunks = []
    failed_chunks = []
    
    # Process each chunk
    for i, chunk in enumerate(tqdm(chunks, desc="Generating embeddings")):
        try:
            text = chunk['chunk_text']
            
            # Skip empty chunks
            if not text or len(text.strip()) < 10:
                failed_chunks.append({
                    'chunk_id': i,
                    'reason': 'empty_text',
                    'chunk': chunk
                })
                continue
            
            # Get embedding
            embedding = get_embedding(text)
            
            # Verify embedding
            if embedding is None or embedding.shape[0] != EMBEDDING_DIMENSION:
                print(f"Warning: Chunk {i} has invalid embedding shape: {embedding.shape if embedding is not None else 'None'}")
                # Create a zero vector
                embedding = np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)
            
            # Add to results
            embeddings.append(embedding)
            chunk_ids.append(i)
            successful_chunks.append(chunk)
            
        except Exception as e:
            failed_chunks.append({
                'chunk_id': i,
                'reason': str(e),
                'chunk': chunk
            })
            print(f"Error processing chunk {i}: {e}")
    
    # Log results
    print(f"Successfully processed {len(embeddings)} chunks")
    print(f"Failed to process {len(failed_chunks)} chunks")
    
    if not embeddings:
        raise ValueError("No valid embeddings found. Check your embedding function.")
    
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
    
    # Save successful chunks
    successful_chunks_file = os.path.join(VECTOR_DB_DIR, 'successful_chunks.json')
    with open(successful_chunks_file, 'w') as f:
        json.dump(successful_chunks, f)
    
    # Save failed chunks
    failed_chunks_file = os.path.join(VECTOR_DB_DIR, 'failed_chunks.json')
    with open(failed_chunks_file, 'w') as f:
        json.dump(failed_chunks, f)
    
    print(f"Vector database built with {len(embeddings)} vectors of dimension {dimension}")
    return index

def main():
    """Main function to process data and build vector database."""
    global EMBEDDING_DIMENSION
    print("Starting OpenSim RAG data processing with improved embeddings...")
    
    # You mentioned you already have the data scraped and stored properly
    # So let's load existing chunks if available, or process files if needed
    chunks_file = os.path.join(PROCESSED_DIR, 'chunks.json')
    
    if os.path.exists(chunks_file):
        print(f"Loading existing chunks from {chunks_file}")
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        print(f"Loaded {len(chunks)} existing chunks")
    else:
        # Process all files and get chunks
        chunks = process_all_files()
    
    # Build vector database with improved embeddings
    index = build_vector_database(chunks)
    
    print("Data processing completed!")
    print(f"Processed data saved to {PROCESSED_DIR}")
    print(f"Vector database saved to {VECTOR_DB_DIR}")

if __name__ == "__main__":
    
    main()