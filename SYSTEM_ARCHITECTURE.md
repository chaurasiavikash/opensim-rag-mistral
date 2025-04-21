# 🏗️ OpenSim RAG System Architecture

This document explains the internal architecture and data flow of the OpenSim RAG system, detailing how different components interact to provide intelligent responses to user queries.

## 🔄 Complete System Flow

### 1️⃣ Data Preparation Phase

Before the application can be used, a preparation phase is required:

1. **Data Collection**: Documentation about OpenSim is collected from various sources
2. **Text Chunking**: Large documents are split into smaller, meaningful chunks
3. **Vector Embedding**: Each chunk is converted to a vector embedding using Sentence Transformers
4. **Database Creation**: Embeddings are indexed using FAISS for efficient similarity search

### 2️⃣ Application Execution Flow

When a user interacts with the system, the following sequence occurs:

#### Server-Side Initialization
1. **Flask Server Start**: When `app.py` runs, it:
   - Initializes the Flask web application
   - Creates the OpenSimRAG instance
   - Loads the vector database and chunks into memory
   - Prepares the embedding model for query conversion
   - Begins listening for HTTP requests on port 5100

#### Client-Side Initialization
2. **Web Interface Loading**:
   - User visits the application URL (typically http://localhost:5100)
   - Flask serves the `index.html` template from `web/templates/`
   - Browser loads CSS (`styles.css`) and JavaScript (`app.js`) from `web/static/`
   - JavaScript initializes the chat interface and displays welcome message

#### Query Processing
3. **User Query Submission**:
   - User types a question and clicks "Send" or presses Enter
   - JavaScript in `app.js`:
     - Displays the user's message in the chat
     - Shows a loading indicator
     - Sends an AJAX POST request to `/api/query` endpoint with the query

4. **Server-Side Processing**:
   - Flask routes the request to the API endpoint
   - The query text is converted to a vector embedding
   - FAISS index is searched to find most similar chunks
   - Top-K most relevant chunks are retrieved (default: 5)

5. **Language Model Generation**:
   - If not already loaded, the Mistral LLM is initialized from `llm_helper.py`
   - For code-related queries, enhanced prompting is used
   - Retrieved chunks are passed as context to the model
   - Mistral generates a response based on the context and query
   - Code formatting is applied if the response contains code blocks

6. **Response Delivery**:
   - Server returns a JSON response containing:
     - Generated answer text
     - Source information (titles, URLs, file origins)
     - Flag indicating if the response contains code
     - Supporting context documents

#### Response Rendering
7. **Client-Side Display**:
   - JavaScript processes the received response
   - Formats code blocks with VS Code-like styling
   - Adds syntax highlighting and copy buttons to code
   - Displays source references with tooltips
   - Renders the complete message in the chat interface

#### Continued Interaction
8. **Subsequent Queries**:
   - LLM remains loaded in memory for faster responses
   - Vector database continues to be available for searches
   - The process repeats from step 3 for new queries

## 🧩 Component Interactions

### Key Files and Their Roles

- **`app.py`**: Main application coordinator
  - Initializes and serves the web application
  - Handles API endpoints and request routing
  - Manages the OpenSimRAG instance lifecycle

- **`llm_helper.py`**: Language model interface
  - Loads and configures the Mistral model
  - Handles prompt engineering and context formatting
  - Generates responses based on retrieved context
  - Applies special handling for code-related queries

- **`code_formatter.py`**: Code output enhancer
  - Post-processes LLM output to improve code formatting
  - Standardizes indentation and language tags
  - Ensures code blocks are properly structured

- **`index.html`**: Web interface structure
  - Defines the layout of the chat application
  - Includes necessary script and style references
  - Creates containers for messages and UI elements

- **`styles.css`**: Visual presentation
  - Controls colors, spacing, and visual appearance
  - Defines dark theme and code block styling
  - Handles responsive design for different devices

- **`app.js`**: Client-side functionality
  - Manages user interactions and input handling
  - Formats messages and code for display
  - Communicates with the server via AJAX
  - Implements UI effects and copy functionality

### Data Flow Diagram

```
┌─────────────┐     HTTP Request      ┌─────────────┐
│             │ ─────────────────────→│             │
│   Browser   │                       │  Flask App  │
│ (User's PC) │ ←───────────────────── │  (app.py)   │
│             │     HTTP Response     │             │
└─────────────┘                       └──────┬──────┘
       ↑                                     │
       │                                     ↓
       │                              ┌─────────────┐
       │                              │ OpenSimRAG  │
       │                              │   System    │
       │                              └──────┬──────┘
       │                                     │
       │                                     ↓
┌─────────────┐                       ┌─────────────┐
│             │                       │             │
│   app.js    │                       │Vector Search│
│ (Frontend)  │                       │  (FAISS)    │
│             │                       │             │
└─────────────┘                       └──────┬──────┘
                                             │
                                             ↓
                                      ┌─────────────┐
                                      │   Mistral   │
                                      │     LLM     │
                                      │(llm_helper) │
                                      └─────────────┘
```

## 🔍 Technical Details

### Vector Database

- Uses FAISS (Facebook AI Similarity Search) for efficient vector similarity search
- Embeddings are created using Sentence Transformers (all-MiniLM-L6-v2)
- Vector dimension: 384 (depends on the specific embedding model)
- Cosine similarity is used as the distance metric

### Language Model Configuration

- Model: Mistral 7B Instruct
- Uses half-precision (FP16) for reduced memory footprint
- Device mapping: Automatic distribution across available GPUs/CPU
- Context window: Up to 4096 tokens
- Temperature: 0.7 (balanced between creativity and determinism)
- Special handling for code-related queries

### Web Interface

- Pure JavaScript frontend (no framework dependencies)
- Syntax highlighting using highlight.js
- Code copying functionality via clipboard.js
- Mobile-responsive design
- VS Code-inspired dark theme

## 🔮 Understanding the Results

The system's effectiveness depends on several factors:

1. **Quality of the Vector Database**: Better documentation coverage improves context relevance
2. **Query Formulation**: More specific queries generally yield better results
3. **Context Length**: The system is limited by how much context can be provided to the LLM
4. **Model Capabilities**: Mistral 7B has inherent limitations in reasoning and domain knowledge

## 🛠️ Extension Points

The system architecture is designed for modularity. Key extension points include:

1. **Vector Database**: Could be replaced with other vector stores (Pinecone, Milvus, etc.)
2. **Language Model**: Can be swapped with other models (Claude, GPT, Llama, etc.)
3. **Web Interface**: The frontend can be enhanced or replaced with a framework-based solution
4. **Document Processing**: The chunking and embedding process can be customized

---

This document provides a high-level overview of the system architecture. For implementation details, please refer to the source code.