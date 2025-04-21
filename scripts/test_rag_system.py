#!/usr/bin/env python3
"""
OpenSim RAG System - Test Script

This script tests the OpenSim RAG system by sending sample queries and evaluating responses.
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:5000/api/query"
TEST_QUERIES = [
    "What is OpenSim?",
    "How do I install OpenSim?",
    "What are the system requirements for OpenSim?",
    "How do I create a musculoskeletal model in OpenSim?",
    "What is inverse kinematics in OpenSim?",
    "How do I run a simulation in OpenSim?",
    "What file formats does OpenSim support?",
    "How do I visualize results in OpenSim?",
    "What is the OpenSim API?",
    "How do I use the OpenSim Python API?"
]

def test_query(query):
    """Test a single query and return the result."""
    print(f"\nTesting query: '{query}'")
    
    try:
        response = requests.post(
            API_URL,
            json={"question": query},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response received (status {response.status_code})")
            return result
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def evaluate_response(query, response):
    """Evaluate the quality of a response."""
    if not response:
        return "Failed"
    
    if "error" in response:
        return f"Error: {response['error']}"
    
    # Check if we have context
    if not response.get("context"):
        return "No context provided"
    
    # Check if we have sources
    if not response.get("sources") or len(response["sources"]) == 0:
        return "No sources provided"
    
    # Check context length
    context_length = len(response["context"])
    if context_length < 100:
        return f"Context too short ({context_length} chars)"
    
    # Simple relevance check - see if query terms appear in context
    query_terms = query.lower().split()
    query_terms = [term for term in query_terms if len(term) > 3]  # Filter out short words
    
    context_lower = response["context"].lower()
    matched_terms = [term for term in query_terms if term in context_lower]
    
    relevance_score = len(matched_terms) / len(query_terms) if query_terms else 0
    
    if relevance_score < 0.5:
        return f"Low relevance ({relevance_score:.2f})"
    
    return f"Good response (relevance: {relevance_score:.2f})"

def main():
    """Main function to test the OpenSim RAG system."""
    print("Starting OpenSim RAG system tests...")
    
    results = {}
    
    for query in TEST_QUERIES:
        response = test_query(query)
        evaluation = evaluate_response(query, response)
        
        results[query] = {
            "evaluation": evaluation,
            "has_response": response is not None,
            "has_context": response and "context" in response,
            "has_sources": response and "sources" in response and len(response["sources"]) > 0,
            "context_length": len(response["context"]) if response and "context" in response else 0,
            "num_sources": len(response["sources"]) if response and "sources" in response else 0
        }
        
        print(f"Evaluation: {evaluation}")
        
        # Add a delay between requests to avoid overwhelming the server
        time.sleep(1)
    
    # Print summary
    print("\n=== Test Summary ===")
    success_count = sum(1 for r in results.values() if "Good response" in r["evaluation"])
    print(f"Successful queries: {success_count}/{len(TEST_QUERIES)}")
    
    print("\nDetailed results:")
    for query, result in results.items():
        print(f"- '{query}': {result['evaluation']}")
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nTest results saved to test_results.json")

if __name__ == "__main__":
    main()
