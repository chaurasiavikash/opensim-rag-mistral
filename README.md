# 🧠 OpenSim RAG Chat Agent: Powered by Mistral AI

## 🚀 Project Overview

This cutting-edge Retrieval-Augmented Generation (RAG) chat agent provides intelligent, context-aware assistance for OpenSim biomechanics software users. Leveraging the powerful Mistral 7B Instruct model, our application delivers precise and helpful responses.

## 🔧 Key Features

- 💬 Advanced AI-powered chat interface
- 📚 Retrieval from comprehensive OpenSim documentation
- 🤖 Mistral 7B Instruct model integration
- 🔍 Semantic search capabilities

## 🖥️ Project Structure

```
opensim-rag/
│
├── 📁 models/
│   └── mistral/         # Mistral model files
├── 📄 app.py            # Main application
├── 📄 llm_helper.py     # Mistral model handler
├── 📂 rag_system/       # RAG system implementation
└── 📂 vector_db/        # Vector database
```

## 🛠️ Mistral Model Setup

### Downloading the Mistral Model

1. Visit the Hugging Face repository:
   https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1

2. Download these essential files:
   - `model-00001-of-00002.safetensors`
   - `model-00002-of-00002.safetensors`
   - `config.json`
   - `tokenizer.json`
   - `tokenizer_config.json`

3. Place files in `models/mistral/` directory

### Recommended Download Methods

#### 🐧 Using Git LFS (Recommended)
```bash
# Install Git LFS
git lfs install

# Clone the model repository
git clone https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1
```

#### 🌐 Manual Download
- Visit Hugging Face repository
- Manually download each required file
- Ensure consistent folder structure

## 💻 System Requirements

### 🔬 Minimum Hardware
- 🧮 RAM: 32GB
- 💾 Disk Space: 20GB
- 🖥️ GPU: 24GB VRAM recommended

### 📦 Software Dependencies
```bash
pip install torch transformers accelerate
```

## 🚀 Quick Start

1. Clone the repository
```bash
git clone https://github.com/yourusername/opensim-rag.git
cd opensim-rag
```

2. Set up virtual environment
```bash
python -m venv env
source env/bin/activate  # Unix/MacOS
# Or
env\Scripts\activate    # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize the RAG system
```bash
python app.py
```

## 🤝 Model Interaction

The Mistral model is integrated via a custom LLM helper that:
- Handles efficient model loading
- Manages context-aware response generation
- Provides fallback mechanisms
- Optimizes memory usage

## 🔍 Performance Optimization

- Uses `device_map="auto"` for intelligent GPU/CPU distribution
- Employs `torch.float16` for reduced memory footprint
- Implements smart token handling

## ⚠️ Potential Challenges

- Large model size requires significant computational resources
- Initial load time may be longer compared to smaller models
- Requires careful memory management

## 🌟 Future Improvements

- [ ] Implement model quantization
- [ ] Add more comprehensive fallback mechanisms
- [ ] Develop more sophisticated context retrieval

## 📄 License

Open-source project for research and educational purposes.

## 🙌 Contributions Welcome!

Interested in improving OpenSim RAG? Open an issue or submit a pull request!

---

🔗 **Links**
- [OpenSim Official Website](https://opensim.stanford.edu/)
- [Mistral AI Model](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1)
- [Project Repository](https://github.com/yourusername/opensim-rag)