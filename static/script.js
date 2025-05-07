document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const statsButton = document.getElementById('stats-button');
    const statsModal = document.getElementById('stats-modal');
    const closeModal = document.querySelector('.close');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    const conversationList = document.getElementById('conversation-list');
    const appContainer = document.querySelector('.app-container');
    
    // Conversation history
    let conversations = {};
    let currentConversationId = generateConversationId();
    
    // Message history for context
    let messageHistory = [];
    let isUserScrolling = false;
    let scrollTimeout;
    
    // Add a tooltip to the send button
    sendButton.setAttribute('title', 'Send message (Enter)');
    toggleSidebarBtn.setAttribute('title', 'Toggle sidebar (H)');
    
    // Scroll initialization - make sure we start at the bottom
    setTimeout(() => {
        scrollToBottom('auto');
    }, 100);
    
    // Initialize sidebar state
    const isSidebarHidden = localStorage.getItem('sidebar-hidden') === 'true';
    if (isSidebarHidden) {
        appContainer.classList.add('sidebar-hidden');
    }
    
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
            // قم بتأخير بسيط للسماح للمتصفح بتحديث DOM قبل التمرير
            setTimeout(() => {
                // Method 1: Modern scrollTo with behavior
                chatMessages.scrollTo({
                    top: chatMessages.scrollHeight,
                    behavior: behavior
                });
                
                // Method 2: Direct scrollTop assignment (fallback)
                setTimeout(() => {
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }, 100);
            }, 10);
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
    
    // Toggle sidebar
    function toggleSidebar() {
        appContainer.classList.toggle('sidebar-hidden');
        
        // Save sidebar state to localStorage
        const isHidden = appContainer.classList.contains('sidebar-hidden');
        localStorage.setItem('sidebar-hidden', isHidden.toString());
        
        // Adjust scroll after sidebar toggle animation completes
        setTimeout(() => {
            scrollToBottom();
        }, 300);
    }
    
    // Generate unique conversation ID
    function generateConversationId() {
        return 'conv-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }
    
    // Create a new conversation
    function createNewConversation() {
        // Save current conversation
        saveCurrentConversation();
        
        // Clear chat messages
        chatMessages.innerHTML = '';
        
        // Add welcome message
        addMessage('مرحباً! كيف يمكنني مساعدتك اليوم؟ أنا روبوت محادثة يمكنه التعلم من محادثاتنا واستخدام Gemini AI للإجابة على الأسئلة المعقدة.\nHello! How can I help you today? I\'m a chatbot that can learn from our conversations and use Gemini AI to answer complex questions.', 'bot');
        
        // Reset message history
        messageHistory = [];
        
        // Generate new conversation ID
        currentConversationId = generateConversationId();
        
        // Create new conversation item in sidebar
        addConversationToSidebar('New Conversation', '', currentConversationId, true);
        
        // Focus on input
        messageInput.focus();
    }
    
    // Save current conversation
    function saveCurrentConversation() {
        if (messageHistory.length > 0) {
            // Get conversation content
            const title = messageHistory.length > 0 ? 
                messageHistory[0].content.substring(0, 30) + (messageHistory[0].content.length > 30 ? '...' : '') : 
                'New Conversation';
            
            const preview = messageHistory.length > 1 ? 
                messageHistory[messageHistory.length - 1].content.substring(0, 40) + (messageHistory[messageHistory.length - 1].content.length > 40 ? '...' : '') : 
                '';
            
            // Save conversation
            conversations[currentConversationId] = {
                title: title,
                preview: preview,
                messages: [...messageHistory],
                timestamp: new Date().toISOString()
            };
            
            // Update conversation in sidebar
            updateConversationInSidebar(title, preview, currentConversationId);
            
            // Store in localStorage (if not too large)
            try {
                localStorage.setItem('chatbot-conversations', JSON.stringify(conversations));
            } catch (e) {
                console.error('Failed to save conversations to localStorage:', e);
                // If storage is full, remove oldest conversations
                pruneConversations();
            }
        }
    }
    
    // Prune conversations to fit in localStorage
    function pruneConversations() {
        // Get all conversations sorted by time
        const convEntries = Object.entries(conversations).sort((a, b) => {
            return new Date(a[1].timestamp) - new Date(b[1].timestamp);
        });
        
        // Remove oldest conversations until it fits
        while (convEntries.length > 0) {
            const oldest = convEntries.shift();
            delete conversations[oldest[0]];
            
            try {
                localStorage.setItem('chatbot-conversations', JSON.stringify(conversations));
                break; // Successfully saved, exit loop
            } catch (e) {
                // Still too large, continue removing
                console.log('Pruned conversation:', oldest[0]);
            }
        }
    }
    
    // Load conversations from localStorage
    function loadConversations() {
        try {
            const saved = localStorage.getItem('chatbot-conversations');
            if (saved) {
                conversations = JSON.parse(saved);
                
                // Populate sidebar with saved conversations
                const convEntries = Object.entries(conversations).sort((a, b) => {
                    return new Date(b[1].timestamp) - new Date(a[1].timestamp);
                });
                
                // Add each conversation to sidebar (limit to 20 most recent)
                convEntries.slice(0, 20).forEach(([id, conv]) => {
                    addConversationToSidebar(conv.title, conv.preview, id);
                });
            }
        } catch (e) {
            console.error('Failed to load conversations:', e);
        }
    }
    
    // Add conversation to sidebar
    function addConversationToSidebar(title, preview, id, isActive = false) {
        // Check if conversation already exists in sidebar
        const existingItem = document.getElementById('conv-' + id);
        if (existingItem) {
            // Update existing item
            existingItem.querySelector('.conversation-title').textContent = title;
            existingItem.querySelector('.conversation-preview').textContent = preview;
            
            // Set active state
            if (isActive) {
                document.querySelectorAll('.conversation-item').forEach(item => {
                    item.classList.remove('active');
                });
                existingItem.classList.add('active');
            }
            return;
        }
        
        // Create conversation item
        const item = document.createElement('div');
        item.className = 'conversation-item' + (isActive ? ' active' : '');
        item.id = 'conv-' + id;
        item.innerHTML = `
            <div class="conversation-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 12C21 16.9706 16.9706 21 12 21C9.69494 21 7.59227 20.1334 5.98961 18.7083L3 19L3.89645 16.1084C3.33539 14.8855 3 13.4843 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div class="conversation-content">
                <div class="conversation-title">${title}</div>
                <div class="conversation-preview">${preview}</div>
            </div>
        `;
        
        // Add click event to load conversation
        item.addEventListener('click', function() {
            loadConversation(id);
        });
        
        // Add to sidebar (after new chat button)
        conversationList.insertBefore(item, newChatBtn.nextSibling);
    }
    
    // Update conversation in sidebar
    function updateConversationInSidebar(title, preview, id) {
        const item = document.getElementById('conv-' + id);
        if (item) {
            item.querySelector('.conversation-title').textContent = title;
            item.querySelector('.conversation-preview').textContent = preview;
        } else {
            addConversationToSidebar(title, preview, id, true);
        }
    }
    
    // Load conversation
    function loadConversation(id) {
        // Save current conversation first
        saveCurrentConversation();
        
        // Set current conversation
        currentConversationId = id;
        
        // Set active state in sidebar
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        const item = document.getElementById('conv-' + id);
        if (item) {
            item.classList.add('active');
        }
        
        // Load conversation
        const conversation = conversations[id];
        if (conversation) {
            // Clear chat messages
            chatMessages.innerHTML = '';
            
            // Load message history
            messageHistory = [...conversation.messages];
            
            // Add messages to chat
            messageHistory.forEach(msg => {
                if (msg.html) {
                    addMessage(msg.content, msg.role, msg.html);
                } else {
                    addMessage(msg.content, msg.role);
                }
            });
            
            // Scroll to bottom
            scrollToBottom();
        }
    }
    
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
        
        // Update conversation in sidebar with preview of user's message
        updateConversationInSidebar(
            messageHistory.length > 0 ? 
                messageHistory[0].content.substring(0, 30) + (messageHistory[0].content.length > 30 ? '...' : '') : 
                'New Conversation',
            message.substring(0, 40) + (message.length > 40 ? '...' : ''),
            currentConversationId
        );
        
        // Limit history to last 50 messages
        if (messageHistory.length > 50) {
            messageHistory = messageHistory.slice(-50);
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
                    
                    // Save the HTML version for history
                    messageHistory.push({
                        role: 'bot',
                        content: data.response,
                        html: data.response_html,
                        timestamp: new Date().toISOString()
                    });
                } else {
                    addMessage(data.response, 'bot');
                    
                    // Store bot message in history
                    messageHistory.push({
                        role: 'bot',
                        content: data.response,
                        timestamp: new Date().toISOString()
                    });
                }
                
                // Update conversation in sidebar with preview of bot's response
                updateConversationInSidebar(
                    messageHistory.length > 0 ? 
                        messageHistory[0].content.substring(0, 30) + (messageHistory[0].content.length > 30 ? '...' : '') : 
                        'New Conversation',
                    data.response.substring(0, 40) + (data.response.length > 40 ? '...' : ''),
                    currentConversationId
                );
                
                // Save conversation to localStorage
                saveCurrentConversation();
                
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
                
                // Store error message in history
                messageHistory.push({
                    role: 'bot',
                    content: 'Sorry, I encountered an error. Please try again.',
                    timestamp: new Date().toISOString()
                });
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
            
            // Store error message in history
            messageHistory.push({
                role: 'bot',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date().toISOString()
            });
            
            scrollToBottom();
        });
    }

    function addMessage(text, sender, htmlContent) {
        // محاولة دمج الرسائل المتتالية من نفس المرسل إذا كانت قريبة زمنياً
        const lastMessage = chatMessages.lastElementChild;
        const isConsecutive = lastMessage && lastMessage.classList.contains(sender + '-message');
        const shouldCombine = false; // تعطيل الدمج حالياً لمنع مشاكل التمرير
        
        let messageElement;
        
        if (shouldCombine && isConsecutive) {
            // إذا كانت رسالة متتالية من نفس المرسل، أضف إليها بدلاً من إنشاء فقاعة جديدة
            messageElement = lastMessage;
            
            // إضافة فاصل بين الرسائل
            const separator = document.createElement('div');
            separator.className = 'message-separator';
            messageElement.appendChild(separator);
            
        } else {
            // إنشاء فقاعة رسالة جديدة
            messageElement = document.createElement('div');
            messageElement.classList.add('message');
            messageElement.classList.add(sender + '-message');
            
            // Add timestamp data attribute
            const timestamp = new Date().toLocaleTimeString();
            messageElement.setAttribute('data-time', timestamp);
            messageElement.setAttribute('title', timestamp);
        }
        
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
        if (sender === 'bot' && window.innerWidth > 768 && !shouldCombine) {
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
        
        // فقط أضف العنصر إلى DOM إذا كان جديداً (غير مدمج مع رسالة سابقة)
        if (!shouldCombine || !isConsecutive) {
            chatMessages.appendChild(messageElement);
        }
        
        // ملاحظة الارتفاع الحالي للتمرير
        const prevScrollHeight = chatMessages.scrollHeight;
        
        // تحديث المحتوى قد يغير ارتفاع العنصر، لذلك قد نحتاج للتمرير مرة أخرى
        setTimeout(() => {
            const newScrollHeight = chatMessages.scrollHeight;
            if (newScrollHeight !== prevScrollHeight) {
                scrollToBottom();
            }
        }, 50);
        
        // Use a multi-stage scroll approach for reliability
        setTimeout(() => {
            scrollToBottom();
        }, 150);
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
    
    // Event listeners for sidebar actions
    toggleSidebarBtn.addEventListener('click', toggleSidebar);
    newChatBtn.addEventListener('click', createNewConversation);
    
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
        
        // 'H' key to toggle sidebar
        if ((e.key === 'h' || e.key === 'H') && document.activeElement !== messageInput) {
            toggleSidebar();
            e.preventDefault();
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
    
    // Load saved conversations
    loadConversations();
    
    // Perform initial scroll to bottom
    scrollToBottom('auto');
    
    // Final scroll check to ensure we start at the bottom
    window.addEventListener('load', function() {
        setTimeout(() => {
            scrollToBottom('auto');
        }, 300);
    });
}); 