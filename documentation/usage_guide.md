# OpenSim RAG Chat Agent - Usage Guide

This guide provides detailed instructions on how to use and extend the OpenSim RAG Chat Agent.

## Basic Usage

After setting up and running the application as described in the README, you can interact with the chat agent through the web interface:

1. Open your browser and navigate to `http://localhost:5000`
2. Type your question about OpenSim in the input field
3. Press Enter or click the Send button
4. The agent will retrieve relevant information from the OpenSim documentation and display it

## Understanding the Results

Each response includes:

- **Answer**: A brief introduction to the information found
- **Context**: The relevant text extracted from the documentation
- **Sources**: References to the original documentation sources

You can click "Show context" to see the full context from which the answer was derived.

## Advanced Usage

### Customizing the Vector Database

You can customize the vector database by modifying the `build_test_db.py` script:

- Change `MAX_CHUNKS` to include more or fewer chunks
- Adjust `EMBEDDING_SIZE` to change the dimension of the embeddings
- Modify the embedding generation method in `get_embedding()`

### Adding New Data Sources

To add new data sources:

1. Create a new scraper in the `scrapers/` directory
2. Update `run_scrapers.py` to include your new scraper
3. Run the scrapers to collect data
4. Process the data using `process_data_lightweight.py`
5. Rebuild the vector database

### Customizing the Web Interface

The web interface can be customized by modifying the files in the `web/` directory:

- `templates/index.html`: Main HTML template
- `static/styles.css`: CSS styles
- `static/app.js`: JavaScript functionality

### Improving Answer Generation

The current implementation returns the most relevant chunks directly. To improve answer generation:

1. Integrate a language model for better answer synthesis
2. Modify the `answer_question()` method in `rag_system.py`
3. Implement prompt engineering techniques for better results

## Troubleshooting

### Vector Database Issues

If you encounter issues with the vector database:

1. Delete the files in `vector_db/` directory
2. Run `python scripts/build_test_db.py` to rebuild the database
3. Restart the application

### Connection Issues

If you can't connect to the web interface:

1. Ensure the Flask server is running
2. Check if port 5000 is already in use by another application
3. Try changing the port in `app.py` if needed

### Memory Issues

If you encounter memory issues:

1. Reduce `MAX_CHUNKS` in `build_test_db.py`
2. Use a smaller subset of the data
3. Implement batching for processing large datasets

## Extending the Project

### Adding New Features

Some ideas for extending the project:

1. Implement user authentication for personalized experiences
2. Add a feedback mechanism to improve responses over time
3. Integrate with OpenSim API for direct interaction with the software
4. Add visualization capabilities for OpenSim models and simulations
5. Implement a history feature to track previous questions and answers

### Deploying to Production

For production deployment:

1. Use a production WSGI server like Gunicorn or uWSGI
2. Set `debug=False` in the Flask application
3. Implement proper error handling and logging
4. Consider containerization with Docker for easier deployment
5. Use a reverse proxy like Nginx for better performance and security
