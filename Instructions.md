# 🚀 OpenSim RAG Mistral: Installation and Setup Guide

## 📋 Prerequisites

Before you begin, ensure you have:
- Python 3.9+
- Git
- Minimum 32GB RAM
- CUDA-capable GPU (recommended)

## 🔧 Step-by-Step Installation

### 1. Clone the Repository
```bash
git clone https://github.com/chaurasiavikash/opensim-rag-mistral.git
cd opensim-rag-mistral
```

### 2. Create Virtual Environment
```bash
# For macOS/Linux
python3 -m venv env
source env/bin/activate

# For Windows
python -m venv env
env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Up Mistral Model

#### Option 1: Manual Download
1. Download model files from Hugging Face:
   - https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1
2. Create a directory:
   ```bash
   mkdir -p models/mistral
   ```
3. Place downloaded files in `models/mistral/`

#### Option 2: Using Git LFS
```bash
# Install Git LFS
git lfs install

# Clone Mistral model (optional)
git lfs clone https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1 models/mistral
```

### 5. Prepare Vector Database
```bash
# Generate or update vector database
python scripts/build_vector_db.py
```

### 6. Run the Application
```bash
python app.py
```

## 🔍 Troubleshooting

- **Model Loading Issues**: 
  - Ensure all model files are present
  - Check CUDA/GPU configuration
  - Verify Python and library versions

- **Memory Constraints**:
  - Use CPU mode if GPU is insufficient
  - Reduce context window size in `llm_helper.py`

## 💡 Performance Tips
- Use a machine with 32GB+ RAM
- CUDA-capable GPU highly recommended
- Close other memory-intensive applications

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support
- Open GitHub issues for bugs
- Discussion forums for general questions
- Check documentation for detailed guidance