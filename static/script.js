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
    let isUserScrolling = false;
    let scrollTimeout;
    
    // Add a tooltip to the send button
    sendButton.setAttribute('title', 'Send message (Enter)');
    
    // Scroll initialization - make sure we start at the bottom
    setTimeout(() => {
        scrollToBottom('auto');
    }, 100);
    
    // Track scroll position and show scroll button when needed
    function checkScrollPosition() {
        const scrollTop = chatMessages.scrollTop;
        const scrollHeight = chatMessages.scrollHeight;
        const clientHeight = chatMessages.clientHeight;
        const scrollBottom = scrollHeight - scrollTop - clientHeight;
        
        // If user has scrolled up significantly, show the scroll-to-bottom button
        if (scrollBottom > 100) {
            chatMessages.classList.add('show-scroll-button');
            isUserScrolling = true;
        } else {
            chatMessages.classList.remove('show-scroll-button');
            isUserScrolling = false;
        }
    }
    
    // Scroll to bottom function with more robust behavior
    function scrollToBottom(behavior = 'smooth') {
        // Try multiple approaches to ensure scrolling works
        try {
            // Method 1: Modern scrollTo with behavior
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: behavior
            });
            
            // Method 2: Direct scrollTop assignment (fallback)
            setTimeout(() => {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 50);
        } catch (e) {
            console.error("Error in scrolling:", e);
            // Ultimate fallback
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    // Listen for scroll events
    chatMessages.addEventListener('scroll', function() {
        checkScrollPosition();
        
        // Clear previous timeout
        clearTimeout(scrollTimeout);
        
        // Set a timeout to check if user has stopped scrolling
        scrollTimeout = setTimeout(function() {
            isUserScrolling = false;
        }, 1000);
    });
    
    // Add click event for the scroll button
    chatMessages.addEventListener('click', function(e) {
        // Check if the click is within the auto-scroll button area
        const rect = chatMessages.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const chatMessagesWidth = chatMessages.offsetWidth;
        const chatMessagesHeight = chatMessages.offsetHeight;
        
        if (x > chatMessagesWidth - 60 && y > chatMessagesHeight - 60) {
            scrollToBottom();
        }
    });
    
    // Force scroll check on window resize
    window.addEventListener('resize', function() {
        checkScrollPosition();
        
        // Reapply scroll to bottom if we were already at bottom
        if (!isUserScrolling) {
            scrollToBottom('auto');
        }
    });
    
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message === '') return;

        // Add user message to chat
        addMessage(message, 'user');
        messageInput.value = '';
        
        // Auto-adjust input height back to default
        messageInput.style.height = '';

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
        
        // Scroll to show typing indicator - make sure this always works
        scrollToBottom();
        
        // Extra scroll after a short delay to ensure it catches up with rendering
        setTimeout(() => {
            scrollToBottom();
        }, 50);

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
                
                // Desktop notification when window is not focused
                if (document.hidden && "Notification" in window) {
                    if (Notification.permission === "granted") {
                        const notification = new Notification("New Message from AI Chatbot", {
                            body: data.response.substring(0, 100) + (data.response.length > 100 ? "..." : ""),
                            icon: "/static/favicon.ico"
                        });
                        
                        notification.onclick = function() {
                            window.focus();
                            notification.close();
                        };
                    } else if (Notification.permission !== "denied") {
                        Notification.requestPermission();
                    }
                }
            } else {
                addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
            
            // Scroll to bottom after adding bot message with multi-stage approach for reliability
            setTimeout(() => {
                scrollToBottom();
                
                // Double-check scroll position after all content is rendered
                setTimeout(() => {
                    scrollToBottom();
                }, 200);
            }, 100);
        })
        .catch(error => {
            console.error('Error:', error);
            typingIndicator.style.display = 'none';
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            
            scrollToBottom();
        });
    }

    function addMessage(text, sender, htmlContent) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(sender + '-message');
        
        // Add timestamp data attribute
        const timestamp = new Date().toLocaleTimeString();
        messageElement.setAttribute('data-time', timestamp);
        messageElement.setAttribute('title', timestamp);
        
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
        
        // Add copy button for bot messages on desktop
        if (sender === 'bot' && window.innerWidth > 768) {
            const copyButton = document.createElement('button');
            copyButton.className = 'copy-button';
            copyButton.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M16 1H4C2.9 1 2 1.9 2 3V17H4V3H16V1ZM19 5H8C6.9 5 6 5.9 6 7V21C6 22.1 6.9 23 8 23H19C20.1 23 21 22.1 21 21V7C21 5.9 20.1 5 19 5ZM19 21H8V7H19V21Z" fill="currentColor"/></svg>';
            copyButton.title = 'Copy to clipboard';
            copyButton.addEventListener('click', function(event) {
                event.stopPropagation(); // Prevent triggering other click events
                const textToCopy = text;
                navigator.clipboard.writeText(textToCopy).then(
                    function() {
                        copyButton.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="#4CAF50"/></svg>';
                        setTimeout(() => {
                            copyButton.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M16 1H4C2.9 1 2 1.9 2 3V17H4V3H16V1ZM19 5H8C6.9 5 6 5.9 6 7V21C6 22.1 6.9 23 8 23H19C20.1 23 21 22.1 21 21V7C21 5.9 20.1 5 19 5ZM19 21H8V7H19V21Z" fill="currentColor"/></svg>';
                        }, 2000);
                    }
                );
            });
            messageElement.appendChild(copyButton);
        }
        
        chatMessages.appendChild(messageElement);
        
        // Use a multi-stage scroll approach for reliability
        setTimeout(() => {
            scrollToBottom();
        }, 10);
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
    
    // Add message history navigation with up/down arrows
    let historyIndex = -1;
    let tempInput = '';
    
    function navigateHistory(direction) {
        const userMessages = messageHistory.filter(msg => msg.role === 'user');
        
        if (userMessages.length === 0) return;
        
        if (historyIndex === -1) {
            // Save current input before navigating
            tempInput = messageInput.value;
        }
        
        if (direction === 'up') {
            if (historyIndex < userMessages.length - 1) {
                historyIndex++;
                messageInput.value = userMessages[userMessages.length - 1 - historyIndex].content;
            }
        } else if (direction === 'down') {
            if (historyIndex > 0) {
                historyIndex--;
                messageInput.value = userMessages[userMessages.length - 1 - historyIndex].content;
            } else if (historyIndex === 0) {
                historyIndex = -1;
                messageInput.value = tempInput;
            }
        }
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

    // Auto-resize input field as user types
    messageInput.addEventListener('input', function() {
        // Reset height to ensure accurate scrollHeight measurement
        this.style.height = 'auto';
        
        // Set new height based on content (with max height limit)
        const newHeight = Math.min(this.scrollHeight, 200);
        this.style.height = newHeight + 'px';
        
        // Apply learning styling
        const text = this.value.trim().toLowerCase();
        if (text.startsWith('learn:') || text.startsWith('تعلم:')) {
            this.style.backgroundColor = '#e8f5e4';
        } else {
            this.style.backgroundColor = '';
        }
    });

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    // Add keyboard shortcut (Enter) to send message
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        } else if (e.key === 'Enter' && e.shiftKey) {
            // Allow multiline input with Shift+Enter
        } else if (e.key === 'ArrowUp' && messageInput.selectionStart === 0) {
            navigateHistory('up');
        } else if (e.key === 'ArrowDown' && messageInput.selectionStart === messageInput.value.length) {
            navigateHistory('down');
        }
    });
    
    // Add global keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+/ or Cmd+/ to focus on input
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            messageInput.focus();
        }
        
        // 'S' key to toggle statistics modal
        if (e.key === 's' || e.key === 'S') {
            if (document.activeElement !== messageInput) {
                if (statsModal.style.display === 'block') {
                    statsModal.style.display = 'none';
                } else {
                    loadStats();
                    statsModal.style.display = 'block';
                }
                e.preventDefault();
            }
        }
        
        // Escape to close modal
        if (e.key === 'Escape' && statsModal.style.display === 'block') {
            statsModal.style.display = 'none';
        }
    });
    
    // Request notification permission for desktop
    if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
        // Delay asking for permission to avoid overwhelming the user on page load
        setTimeout(() => {
            Notification.requestPermission();
        }, 5000);
    }

    // Focus input on load
    messageInput.focus();
    
    // Add resize handle for input box height
    const resizeHandle = document.createElement('div');
    resizeHandle.className = 'resize-handle';
    document.querySelector('.chat-input').appendChild(resizeHandle);
    
    let startY, startHeight;
    
    resizeHandle.addEventListener('mousedown', function(e) {
        startY = e.clientY;
        startHeight = parseInt(document.defaultView.getComputedStyle(messageInput).height, 10);
        document.addEventListener('mousemove', resizeInput);
        document.addEventListener('mouseup', stopResize);
        e.preventDefault();
    });
    
    function resizeInput(e) {
        const newHeight = startHeight - (e.clientY - startY);
        if (newHeight > 30 && newHeight < 200) {
            messageInput.style.height = newHeight + 'px';
        }
    }
    
    function stopResize() {
        document.removeEventListener('mousemove', resizeInput);
        document.removeEventListener('mouseup', stopResize);
    }
    
    // Create favicon if it doesn't exist
    const link = document.createElement('link');
    link.rel = 'shortcut icon';
    link.href = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="0.9em" font-size="90">🤖</text></svg>';
    link.type = 'image/svg+xml';
    document.head.appendChild(link);
    
    // Perform initial scroll to bottom
    scrollToBottom('auto');
    
    // Final scroll check to ensure we start at the bottom
    window.addEventListener('load', function() {
        setTimeout(() => {
            scrollToBottom('auto');
        }, 300);
    });
}); 