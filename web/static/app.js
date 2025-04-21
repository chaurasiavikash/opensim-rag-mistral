// OpenSim RAG Chat Assistant JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const loading = document.getElementById('loading');
    
    // Add welcome message with OpenSim styling
    const welcomeDiv = document.querySelector('.message.assistant-message .message-content');
    welcomeDiv.classList.add('welcome-message');
    
    // Function to escape HTML to prevent XSS
    function escapeHTML(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
    
    // Function to format code blocks in text
    function formatCodeBlocks(text) {
        // Replace ```code``` with <pre><code>code</code></pre>
        let formatted = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Replace `code` with <code>code</code>
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        return formatted;
    }
    
    // Function to highlight search terms in text
    function highlightSearchTerms(text, query) {
        if (!query) return text;
        
        const terms = query.split(' ')
            .filter(term => term.length > 3) // Only highlight terms with more than 3 characters
            .map(term => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')); // Escape regex special characters
        
        if (terms.length === 0) return text;
        
        const regex = new RegExp(`(${terms.join('|')})`, 'gi');
        return text.replace(regex, '<span class="highlight">$1</span>');
    }
    
    // Function to add a message to the chat
    function addMessage(content, isUser, sources = [], context = '', query = '') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Format and sanitize content
        let formattedContent = escapeHTML(content);
        formattedContent = formatCodeBlocks(formattedContent);
        
        if (!isUser) {
            formattedContent = highlightSearchTerms(formattedContent, query);
        }
        
        contentDiv.innerHTML = formattedContent;
        messageDiv.appendChild(contentDiv);
        
        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources';
            sourcesDiv.innerHTML = '<strong>Sources:</strong>';
            
            const sourcesList = document.createElement('ul');
            sources.forEach(source => {
                const sourceItem = document.createElement('li');
                sourceItem.className = 'source-item';
                
                if (source.url) {
                    sourceItem.innerHTML = `<a href="${escapeHTML(source.url)}" target="_blank" class="source-tooltip">
                        ${escapeHTML(source.title || 'Link')}
                        <span class="tooltip-text">${escapeHTML(source.file || source.url)}</span>
                    </a>`;
                } else {
                    sourceItem.textContent = source.title || source.file || 'Unknown source';
                }
                
                sourcesList.appendChild(sourceItem);
            });
            
            sourcesDiv.appendChild(sourcesList);
            messageDiv.appendChild(sourcesDiv);
        }
        
        // Add context if available
        if (context) {
            const contextToggle = document.createElement('div');
            contextToggle.className = 'context-toggle';
            contextToggle.textContent = 'Show context';
            
            const contextSection = document.createElement('div');
            contextSection.className = 'context-section';
            contextSection.style.display = 'none';
            
            // Format and highlight context
            let formattedContext = escapeHTML(context);
            formattedContext = highlightSearchTerms(formattedContext, query);
            contextSection.innerHTML = formattedContext;
            
            contextToggle.addEventListener('click', function() {
                if (contextSection.style.display === 'none') {
                    contextSection.style.display = 'block';
                    contextToggle.textContent = 'Hide context';
                } else {
                    contextSection.style.display = 'none';
                    contextToggle.textContent = 'Show context';
                }
            });
            
            messageDiv.appendChild(contextToggle);
            messageDiv.appendChild(contextSection);
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to send a message
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, true);
        
        // Clear input
        userInput.value = '';
        
        // Show loading indicator
        loading.style.display = 'block';
        
        // Send request to server
        fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: message })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loading.style.display = 'none';
            
            if (data.error) {
                addMessage(`Error: ${data.error}`, false);
                return;
            }
            
            // Add assistant message to chat
            addMessage(data.answer, false, data.sources, data.context, message);
        })
        .catch(error => {
            // Hide loading indicator
            loading.style.display = 'none';
            
            // Add error message
            addMessage(`Sorry, there was an error processing your request: ${error.message}`, false);
        });
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Focus input field on page load
    userInput.focus();
});
