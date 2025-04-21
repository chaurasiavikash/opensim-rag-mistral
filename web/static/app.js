// OpenSim RAG Chat Assistant JavaScript
// Enhanced with VS Code-like code formatting

document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const loading = document.getElementById('loading');
    
    // Initialize clipboard.js for code copying
    const clipboard = new ClipboardJS('.code-copy-btn');
    
    clipboard.on('success', function(e) {
        // Show success indicator
        const codeBlock = e.trigger.closest('.code-container');
        const copyBtn = codeBlock.querySelector('.code-copy-btn');
        
        copyBtn.textContent = 'Copied!';
        setTimeout(() => {
            copyBtn.textContent = 'Copy';
        }, 2000);
        
        e.clearSelection();
    });
    
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
        // First, handle code blocks with language specified (```python)
        let formatted = text.replace(/```(\w+)\n([\s\S]*?)```/g, function(match, language, code) {
            // Create VS Code-like container
            return `
            <div class="code-container">
                <div class="code-header">
                    <span class="code-language">${language}</span>
                    <button class="code-copy-btn" data-clipboard-text="${escapeHTML(code)}">Copy</button>
                </div>
                <pre class="code-block"><code class="language-${language}">${escapeHTML(code)}</code></pre>
            </div>`;
        });
        
        // Then, handle generic code blocks (```)
        formatted = formatted.replace(/```\n([\s\S]*?)```/g, function(match, code) {
            return `
            <div class="code-container">
                <div class="code-header">
                    <span class="code-language">plaintext</span>
                    <button class="code-copy-btn" data-clipboard-text="${escapeHTML(code)}">Copy</button>
                </div>
                <pre class="code-block"><code>${escapeHTML(code)}</code></pre>
            </div>`;
        });
        
        // Replace inline code `code` with <code>code</code>
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        return formatted;
    }
    
    // Process normal text for line breaks and paragraphs
    function formatText(text) {
        // Convert line breaks to <br> and handle paragraphs
        let formatted = text;
        
        // Replace double line breaks with paragraph tags
        formatted = formatted.replace(/\n\s*\n/g, '</p><p>');
        
        // Replace single line breaks with <br>
        formatted = formatted.replace(/\n(?!\n)/g, '<br>');
        
        // Wrap in paragraph tags if not already done
        if (!formatted.startsWith('<p>')) {
            formatted = '<p>' + formatted;
        }
        if (!formatted.endsWith('</p>')) {
            formatted += '</p>';
        }
        
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
        
        if (isUser) {
            // For user messages, just escape HTML and apply simple formatting
            contentDiv.innerHTML = formatText(escapeHTML(content));
        } else {
            // For assistant messages, we need more complex formatting
            
            // Step 1: Extract and temporarily replace code blocks
            const codeBlocks = [];
            let withoutCode = content;
            
            // Extract code blocks with language specifier
            withoutCode = withoutCode.replace(/```(\w+)\n([\s\S]*?)```/g, function(match, language, code) {
                codeBlocks.push({ language, code });
                return `[CODE_BLOCK_${codeBlocks.length - 1}]`;
            });
            
            // Extract generic code blocks
            withoutCode = withoutCode.replace(/```\n([\s\S]*?)```/g, function(match, code) {
                codeBlocks.push({ language: 'plaintext', code });
                return `[CODE_BLOCK_${codeBlocks.length - 1}]`;
            });
            
            // Step 2: Process text content
            let formattedContent = escapeHTML(withoutCode);
            formattedContent = highlightSearchTerms(formattedContent, query);
            formattedContent = formatText(formattedContent);
            
            // Step 3: Replace inline code
            formattedContent = formattedContent.replace(/`([^`]+)`/g, '<code>$1</code>');
            
            // Step 4: Put code blocks back
            formattedContent = formattedContent.replace(/\[CODE_BLOCK_(\d+)\]/g, function(match, index) {
                const { language, code } = codeBlocks[parseInt(index)];
                return `
                <div class="code-container">
                    <div class="code-header">
                        <span class="code-language">${language}</span>
                        <button class="code-copy-btn" data-clipboard-text="${escapeHTML(code)}">Copy</button>
                    </div>
                    <pre class="code-block"><code class="language-${language}">${escapeHTML(code)}</code></pre>
                </div>`;
            });
            
            contentDiv.innerHTML = formattedContent;
        }
        
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
        
        // Apply syntax highlighting to code blocks
        messageDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightBlock(block);
        });
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
        loading.style.display = 'flex';
        
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
            
            // Check if the response has the 'has_code' flag
            const hasCode = data.has_code || (data.answer && data.answer.includes('```'));
            
            // Add assistant message to chat
            addMessage(data.answer, false, data.sources, data.source_documents, message);
            
            // If this message had code, reinitialize the copy buttons
            if (hasCode) {
                // Refresh clipboard.js for newly added code blocks
                clipboard.destroy();
                new ClipboardJS('.code-copy-btn');
            }
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