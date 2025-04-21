# OpenSim RAG Chat Agent - Technical Documentation

This document provides technical details about the implementation of the OpenSim RAG Chat Agent.

## System Architecture

The OpenSim RAG Chat Agent consists of several components:

1. **Data Collection**: Scrapers for gathering OpenSim documentation
2. **Data Processing**: Scripts for cleaning and chunking text
3. **Vector Database**: FAISS index for efficient similarity search
4. **RAG System**: Core retrieval and generation logic
5. **Web Interface**: Flask-based web application

### Data Flow

1. User submits a question through the web interface
2. The question is processed and converted to an embedding vector
3. The vector database is queried to find similar chunks
4. Relevant chunks are retrieved and combined
5. The response is generated and returned to the user

## Component Details

### Data Collection

The data collection system uses several scrapers:

- `confluence_scraper.py`: Scrapes OpenSim's Confluence documentation
- `github_scraper.py`: Collects documentation from GitHub repositories
- `api_docs_scraper.py`: Extracts API documentation
- `scholar_scraper.py`: Finds open access papers about OpenSim

Each scraper implements:
- Rate limiting to avoid overloading servers
- Error handling for robust operation
- Metadata collection for source attribution

### Data Processing

The data processing pipeline includes:

1. **Text Extraction**: Extracting plain text from various formats
2. **Cleaning**: Removing irrelevant content and normalizing text
3. **Chunking**: Splitting documents into manageable chunks with overlap
4. **Metadata Preservation**: Maintaining source information for each chunk

### Vector Database

The vector database uses FAISS (Facebook AI Similarity Search) for efficient similarity search:

- **Index Type**: L2 distance for similarity measurement
- **Vector Dimension**: 300-dimensional embeddings
- **Embedding Method**: Combination of spaCy word vectors and TF-IDF-like representation

### RAG System

The RAG system implements:

- **Query Processing**: Converting questions to embedding vectors
- **Retrieval**: Finding relevant chunks using vector similarity
- **Context Building**: Combining chunks to provide comprehensive context
- **Source Attribution**: Tracking and presenting source information

### Web Interface

The web interface uses:

- **Backend**: Flask web framework
- **Frontend**: HTML, CSS, and JavaScript
- **API**: RESTful API for communication between frontend and backend
- **Responsive Design**: Adapts to different screen sizes

## Implementation Details

### Embedding Generation

The system uses a hybrid approach for generating embeddings:

```python
def get_embedding(text):
    # Process with spaCy
    doc = nlp(text)
    
    # Create a fixed-size vector
    vec = np.zeros(EMBEDDING_SIZE, dtype=np.float32)
    
    # Use spaCy's built-in word vectors if available
    if doc.vector.any() and len(doc.vector) == EMBEDDING_SIZE:
        return doc.vector
    
    # Create a simple TF-IDF like representation
    word_freq = {}
    for token in doc:
        if token.is_alpha and not token.is_stop:
            word = token.text.lower()
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Use hash of words to determine vector positions
    for word, freq in word_freq.items():
        pos = hash(word) % EMBEDDING_SIZE
        vec[pos] += freq
    
    # Normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    
    return vec
```

### Vector Search

The system implements vector search with dimension handling:

```python
def query(self, query_text, top_k=TOP_K):
    # Get query embedding
    query_embedding = self.get_embedding(query_text)
    query_embedding = query_embedding.reshape(1, -1)
    
    # Ensure the embedding has the correct shape
    if query_embedding.shape[1] != self.embedding_size:
        # Resize the embedding to match the index dimension
        resized_embedding = np.zeros((1, self.embedding_size), dtype=np.float32)
        min_dim = min(query_embedding.shape[1], self.embedding_size)
        resized_embedding[0, :min_dim] = query_embedding[0, :min_dim]
        query_embedding = resized_embedding
    
    # Search the index
    distances, indices = self.index.search(query_embedding, top_k)
    
    # Process results...
```

## Performance Considerations

- **Memory Usage**: The system is designed to work with limited memory by using a subset of chunks
- **Search Efficiency**: FAISS provides efficient similarity search even with large vector databases
- **Scalability**: The system can be scaled by adjusting the number of chunks and vector dimensions

## Security Considerations

- **Input Validation**: All user inputs are validated to prevent injection attacks
- **Error Handling**: Comprehensive error handling to prevent information leakage
- **Resource Limits**: Limits on query complexity to prevent resource exhaustion

## Future Improvements

- **Language Model Integration**: Adding a language model for better answer synthesis
- **Incremental Updates**: Allowing the vector database to be updated without full rebuilds
- **Multi-language Support**: Adding support for multiple languages
- **Personalization**: Implementing user profiles for personalized responses
- **Feedback Loop**: Adding a mechanism for users to provide feedback on responses
