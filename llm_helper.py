#!/usr/bin/env python3
"""
OpenSim RAG System - LLM Helper using Mistral

This module handles generation of conversational responses using the Mistral model,
with optimizations for memory efficiency and response quality.
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class MistralLLM:
    def __init__(self, models_dir="./models/mistral"):
        """
        Initialize the Mistral Language Model
        
        Key Responsibilities:
        1. Load the Mistral model from local files
        2. Set up tokenizer and model with optimized settings
        3. Prepare for efficient response generation
        """
        self.models_dir = models_dir
        self._load_model()
    
    def _load_model(self):
        """
        Load the Mistral model with careful configuration
        
        Main Actions:
        - Load tokenizer from local files
        - Load model weights with memory-efficient settings
        - Configure token handling
        """
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.models_dir,
                trust_remote_code=True
            )
            
            # Set pad token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with optimized settings
            self.model = AutoModelForCausalLM.from_pretrained(
                self.models_dir,
                device_map="auto",  # Automatically distribute across available devices
                torch_dtype=torch.float16,  # Reduce memory usage
                trust_remote_code=True
            )
            
            print("Mistral model loaded successfully!")
        
        except Exception as e:
            print(f"Model loading error: {e}")
            raise RuntimeError(f"Failed to load Mistral model: {e}")
    
    def generate_response(self, query, context_chunks, max_length=256):
        """
        Generate a response based on query and context
        
        Key Steps:
        1. Combine context chunks
        2. Create an instruction-based prompt
        3. Generate response using Mistral's specific format
        4. Clean and return the response
        """
        # Combine context chunks
        context = "\n\n".join([chunk.strip() for chunk in context_chunks])
        
        # Truncate context if too long
        if len(context) > 3000:
            context = context[:3000] + "..."
        
        # Create Mistral-specific instruction prompt
        prompt = f"""<s>[INST] You are OpenSimAssistant, a helpful AI focused on OpenSim documentation.

Context Information:
{context}

User Question: {query}

Provide a clear, concise, and accurate response based on the context. 
If the information is incomplete, explain what you know and suggest further research. [/INST]"""
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=4096
            )
            
            # Move inputs to model's device
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_new_tokens=max_length,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode and clean response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract response after instruction
            response_start = full_response.find('[/INST]')
            if response_start != -1:
                response = full_response[response_start+7:].strip()
            else:
                response = full_response.replace(prompt, "").strip()
            
            return response or self.fallback_response(query)
        
        except Exception as e:
            print(f"Response generation error: {e}")
            return self.fallback_response(query)
    
    def fallback_response(self, query):
        """
        Provide a helpful response if generation fails
        """
        return f"""I apologize, but I couldn't generate a specific response to: "{query}"

For OpenSim information:
1. Visit the official OpenSim website
2. Check the documentation at https://simtk-confluence.stanford.edu/display/OpenSim/
3. Consult user guides and community forums
"""

# Test the module
if __name__ == "__main__":
    llm = MistralLLM()
    test_query = "How do I install OpenSim on Windows?"
    test_context = [
        "OpenSim can be installed on Windows by downloading the installer from the website.",
        "System requirements include Windows 10 or newer, 8GB RAM minimum."
    ]
    response = llm.generate_response(test_query, test_context)
    print(f"Query: {test_query}")
    print(f"Response:\n{response}")