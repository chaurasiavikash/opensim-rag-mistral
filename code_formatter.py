import re

def format_code_blocks(text):
    """
    Process the LLM output to ensure code blocks are properly formatted.
    
    Args:
        text (str): The LLM-generated text that may contain code blocks
        
    Returns:
        str: Text with properly formatted code blocks
    """
    # Pattern to match code blocks (including the language specifier)
    pattern = r"```(\w*)\n(.*?)\n```"
    
    def format_code(match):
        language = match.group(1) or "python"  # Default to python if language not specified
        code = match.group(2)
        
        # Remove excess blank lines at beginning and end
        code = code.strip()
        
        # Standardize indentation (4 spaces)
        lines = code.split('\n')
        # Find the minimum indentation (excluding empty lines)
        non_empty_lines = [line for line in lines if line.strip()]
        if non_empty_lines:
            min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines if line.strip())
            # Remove common leading whitespace but maintain relative indentation
            code = '\n'.join(line[min_indent:] if line.strip() else line for line in lines)
        
        # Add proper language specifier
        return f"```{language}\n{code}\n```"
    
    # Replace all code blocks with properly formatted ones
    formatted_text = re.sub(pattern, format_code, text, flags=re.DOTALL)
    return formatted_text

class CodeFormattingLLM:
    """Wrapper class that adds code formatting to any LLM implementation"""
    
    def __init__(self, base_llm):
        """
        Initialize with an existing LLM instance
        
        Args:
            base_llm: The base LLM implementation that generates responses
        """
        self.base_llm = base_llm
    
    def generate_response(self, query, context_chunks, max_length=256):
        """
        Generate a response and post-process it to format code blocks properly
        
        Args:
            query (str): The user query
            context_chunks (list): List of context chunk strings
            max_length (int): Maximum length for generation
            
        Returns:
            str: Formatted response with properly formatted code blocks
        """
        # Generate response using the base LLM
        response = self.base_llm.generate_response(query, context_chunks, max_length)
        
        # Post-process to format code blocks
        formatted_response = format_code_blocks(response)
        
        return formatted_response