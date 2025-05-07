document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const statsButton = document.getElementById('stats-button');
    const statsModal = document.getElementById('stats-modal');
    const closeModal = document.querySelector('.close');
    
    // Message history for context
    let messageHistory = [];
    
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message === '') return;

        // Add user message to chat
        addMessage(message, 'user');
        messageInput.value = '';

        // Store message in history
        messageHistory.push({
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
        });
        
        // Limit history to last 10 messages
        if (messageHistory.length > 10) {
            messageHistory = messageHistory.slice(-10);
        }

        // Show typing indicator
        typingIndicator.style.display = 'block';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Send message to server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            
            // Add bot response to chat
            if (data.response) {
                // Check if we have HTML formatted response
                if (data.has_markdown && data.response_html) {
                    addMessage(data.response, 'bot', data.response_html);
                } else {
                    addMessage(data.response, 'bot');
                }
                
                // Store bot message in history
                messageHistory.push({
                    role: 'bot',
                    content: data.response,
                    timestamp: new Date().toISOString()
                });
            } else {
                addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            typingIndicator.style.display = 'none';
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        });
    }

    function addMessage(text, sender, htmlContent) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(sender + '-message');
        
        // Check if message contains Gemini AI notice
        if (sender === 'bot' && text.includes("using Gemini AI")) {
            // Split the message into notice and content
            const parts = text.split("\n\n");
            if (parts.length >= 2) {
                const notice = parts[0];
                const content = parts.slice(1).join("\n\n");
                
                // Create notice element
                const noticeElement = document.createElement('div');
                noticeElement.className = 'ai-notice';
                noticeElement.textContent = notice;
                
                // Create content element
                const contentElement = document.createElement('div');
                
                // Use HTML content if available, otherwise use text
                if (htmlContent) {
                    contentElement.innerHTML = htmlContent;
                } else {
                    contentElement.textContent = content;
                }
                
                // Add to message
                messageElement.appendChild(noticeElement);
                messageElement.appendChild(contentElement);
            } else {
                // Use HTML content if available, otherwise use text
                if (htmlContent) {
                    messageElement.innerHTML = htmlContent;
                } else {
                    messageElement.textContent = text;
                }
            }
        } 
        // Check if the message is for learning
        else if (sender === 'user' && (text.toLowerCase().startsWith('learn:') || text.startsWith('تعلم:'))) {
            messageElement.style.fontStyle = 'italic';
            messageElement.style.backgroundColor = '#b5e6a1';
            messageElement.style.color = '#2e5a1c';
            messageElement.textContent = text;
        } else {
            // Use HTML content if available, otherwise use text
            if (htmlContent && sender === 'bot') {
                messageElement.innerHTML = htmlContent;
            } else {
                messageElement.textContent = text;
            }
        }
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Load and display statistics
    function loadStats() {
        fetch('/stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('learned-responses').textContent = data.learned_responses;
                document.getElementById('conversation-sessions').textContent = data.conversation_sessions;
                
                // Display Gemini status
                const geminiStatus = document.getElementById('gemini-status');
                if (data.gemini_available) {
                    geminiStatus.textContent = "Connected ✓";
                    geminiStatus.style.color = "#4CAF50";
                } else {
                    geminiStatus.textContent = "Not Connected ✗";
                    geminiStatus.style.color = "#f44336";
                }
                
                // Display markdown status
                if (document.getElementById('markdown-status')) {
                    const markdownStatus = document.getElementById('markdown-status');
                    if (data.markdown_enabled) {
                        markdownStatus.textContent = "Enabled ✓";
                        markdownStatus.style.color = "#4CAF50";
                    } else {
                        markdownStatus.textContent = "Disabled ✗";
                        markdownStatus.style.color = "#f44336";
                    }
                }
                
                // Display popular topics
                const topicsElement = document.getElementById('popular-topics');
                if (data.popular_topics && data.popular_topics.length > 0) {
                    topicsElement.innerHTML = data.popular_topics.map(topic => {
                        return `<div>${topic[0]}: ${topic[1]}</div>`;
                    }).join('');
                } else {
                    topicsElement.textContent = "No data yet";
                }
            })
            .catch(error => {
                console.error('Error loading stats:', error);
            });
    }
    
    // Show stats modal
    statsButton.addEventListener('click', function() {
        loadStats();
        statsModal.style.display = 'block';
    });
    
    // Close modal when clicking X
    closeModal.addEventListener('click', function() {
        statsModal.style.display = 'none';
    });
    
    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target === statsModal) {
            statsModal.style.display = 'none';
        }
    });

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Handle learning commands with special styling
    messageInput.addEventListener('input', function() {
        const text = messageInput.value.trim().toLowerCase();
        if (text.startsWith('learn:') || text.startsWith('تعلم:')) {
            messageInput.style.backgroundColor = '#e8f5e4';
        } else {
            messageInput.style.backgroundColor = '';
        }
    });

    // Focus input on load
    messageInput.focus();
}); 