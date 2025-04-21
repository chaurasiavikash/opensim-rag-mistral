#!/usr/bin/env python3
"""
OpenSim RAG System - LLM Helper using Microsoft Phi-2

This module handles generation of conversational responses using the Phi-2 model,
with fixes for numerical stability issues.
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Configuration
MODELS_DIR = "./models"  # Directory to store models
os.makedirs(MODELS_DIR, exist_ok=True)

# Singleton pattern to avoid loading the model multiple times
class Phi2LLM:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            print("Initializing Phi-2 model (this may take a moment)...")
            cls._instance = super(Phi2LLM, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        """Load the Phi-2 model without quantization."""
        try:
            # Path to locally downloaded model
            model_path = os.path.join(MODELS_DIR, "microsoft/phi-2")
            
            # Check if using local files or downloading
            if os.path.exists(model_path) and os.path.isdir(model_path):
                print(f"Loading Phi-2 model from local directory: {model_path}")
                # Load model and tokenizer from local files
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    device_map="auto",
                    torch_dtype=torch.float32,  # Use float32 for better stability
                    trust_remote_code=True
                )
            else:
                print("Downloading Phi-2 model from HuggingFace (this may take a while)...")
                # Load model and tokenizer from HuggingFace
                model_name = "microsoft/phi-2"
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=MODELS_DIR)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto",
                    cache_dir=MODELS_DIR,
                    torch_dtype=torch.float32,  # Use float32 for better stability
                    trust_remote_code=True
                )
            
            # Fix attention mask issue
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.model.config.eos_token_id
            
            print("Phi-2 model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading model with default settings: {e}")
            print("Trying with minimal settings...")
            
            # Fallback to CPU with minimal settings
            model_name = "microsoft/phi-2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=MODELS_DIR)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=MODELS_DIR,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            self.model.config.pad_token_id = self.model.config.eos_token_id
            print("Phi-2 model loaded with minimal settings (CPU only, might be slower)")
    
    def generate_response(self, query, context_chunks, max_length=256):  # Reduced max_length
        """
        Generate a conversational response based on the query and retrieved context.
        
        Args:
            query (str): The user's question
            context_chunks (list): Retrieved context chunks
            max_length (int): Maximum length of the generated response
            
        Returns:
            str: The generated response
        """
        # Combine context chunks into a single context (limit length)
        context = "\n\n".join([chunk.strip() for chunk in context_chunks])
        
        # Truncate context if it's too long (to avoid exceeding token limits)
        if len(context) > 2000:  # Reduced further to help with stability
            context = context[:2000] + "..."
        
        # Create the prompt for the model (Phi-2 uses a simpler prompt format)
        prompt = f"""You are OpenSimAssistant, a helpful AI assistant focused on answering questions about OpenSim, 
a biomechanical simulation software. Provide accurate, clear, and concise answers to users' questions.
When responding, be friendly and educational. Focus on being practically helpful to new users of the software.

User question: {query}

Here is information from the OpenSim documentation that may be helpful:
{context}

Please create a helpful response based on this information. If the information doesn't 
fully answer the question, clarify what you know and what might need further research.

OpenSimAssistant's response:
"""
        
        try:
            # Generate response with more stable settings and explicit attention mask
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
            
            # Move to the right device
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                # Use more stable generation parameters
                outputs = self.model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],  # Explicitly provide attention mask
                    max_new_tokens=max_length,
                    temperature=0.2,  # Lower temperature for more stability
                    do_sample=False,  # Disable sampling for deterministic output
                    num_beams=1,  # Use greedy decoding
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode and clean up the response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the assistant's response (remove the prompt)
            if "OpenSimAssistant's response:" in full_response:
                response = full_response.split("OpenSimAssistant's response:")[-1].strip()
            else:
                # Fallback if the split doesn't work
                response = full_response.replace(prompt, "").strip()
            
            return response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            # Provide a helpful fallback response
            return f"""I apologize, but I encountered a technical issue while generating a response. Here's what I can tell you:

For questions about OpenSim, you can check the official documentation at https://simtk-confluence.stanford.edu/display/OpenSim/

The user guides and tutorials section is particularly helpful for new users.
"""

# Test the module if run directly
if __name__ == "__main__":
    llm = Phi2LLM()
    test_query = "How do I install OpenSim on Windows?"
    test_context = ["OpenSim can be installed on Windows by downloading the installer from the website and following the setup instructions.",
                   "System requirements for OpenSim include Windows 10 or newer, 8GB RAM minimum, and 1GB free disk space."]
    
    response = llm.generate_response(test_query, test_context)
    print(f"Query: {test_query}")
    print(f"Response:\n{response}")