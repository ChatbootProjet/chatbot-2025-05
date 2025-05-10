/**
 * AI Chatbot - Main Frontend Script
 * Provides interactive functionality for the chatbot interface
 * With improved message handling and scroll management
 */

// DOM Elements
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const messagesContainer = document.getElementById('messages-container');
const messages = document.getElementById('messages');
const welcomeScreen = document.getElementById('welcome-screen');
const typingIndicator = document.getElementById('typing-indicator');
const scrollToBottomBtn = document.getElementById('scroll-to-bottom');
const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
const sidebar = document.getElementById('sidebar');
const toggleThemeBtn = document.getElementById('toggle-theme-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const statsButton = document.getElementById('stats-button');
const statsModal = document.getElementById('stats-modal');
const helpButton = document.getElementById('help-button');
const helpModal = document.getElementById('help-modal');
const conversationList = document.getElementById('conversation-list');

// Global variables
let messageHistory = []; // Store message history for up/down navigation
let historyIndex = -1; // Current position in message history
let isTyping = false; // Flag to prevent multiple message sending
let currentConversationId = null; // Current conversation ID
let unreadMessages = 0; // Track unread messages when scrolled up
let lastScrollPosition = 0; // Track last scroll position
let isAutoScrollEnabled = true; // Flag to enable/disable auto-scrolling
let themePreference = localStorage.getItem('theme') || 'light'; // Theme preference

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    // Add class to the message container to enable animations
    setTimeout(() => {
        messagesContainer.classList.add('animation-enabled');
    }, 500);
    
    initializeChat();
    setupEventListeners();
    applyTheme();
    loadConversationHistory();
    
    // Check for saved theme preference
    if (localStorage.getItem('theme')) {
        themePreference = localStorage.getItem('theme');
        applyTheme();
    }
});

// Initialize the chat interface
function initializeChat() {
    // Focus on input field
    messageInput.focus();
    
    // Generate a new conversation ID if none exists
    if (!currentConversationId) {
        currentConversationId = generateConversationId();
    }
    
    // Show welcome screen if no messages
    if (messages.children.length === 0) {
        welcomeScreen.style.display = 'flex';
    } else {
        welcomeScreen.style.display = 'none';
    }
    
    // Adjust textarea height on input
    messageInput.addEventListener('input', () => {
        adjustTextareaHeight();
    });
}

// Setup all event listeners
function setupEventListeners() {
    // Send message on button click
    sendButton.addEventListener('click', sendMessage);
    
    // Send message on Enter key (with Shift+Enter for new line)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        } else if (e.key === 'ArrowUp' && messageInput.value === '') {
            navigateHistory('up');
        } else if (e.key === 'ArrowDown' && messageInput.value === '') {
            navigateHistory('down');
        }
    });
    
    // Scroll event listener for messages container
    messages.addEventListener('scroll', handleScroll);
    
    // Scroll to bottom button
    scrollToBottomBtn.addEventListener('click', scrollToBottom);
    
    // Toggle sidebar
    toggleSidebarBtn.addEventListener('click', toggleSidebar);
    
    // Toggle theme
    toggleThemeBtn.addEventListener('click', toggleTheme);
    
    // New chat button
    newChatBtn.addEventListener('click', startNewConversation);
    
    // Stats button
    statsButton.addEventListener('click', () => toggleModal(statsModal));
    
    // Help button
    helpButton.addEventListener('click', () => toggleModal(helpModal));
    
    // Close modals when clicking close button
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            toggleModal(modal, false);
        });
    });
    
    // Close modals when clicking outside content
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                toggleModal(modal, false);
            }
        });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Alt+D - Toggle dark mode
        if (e.altKey && e.key === 'd') {
            toggleTheme();
        }
        // Alt+S - Toggle sidebar
        if (e.altKey && e.key === 's') {
            toggleSidebar();
        }
        // Escape - Close modals
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(modal => {
                toggleModal(modal, false);
            });
        }
    });
    
    // Window resize handler
    window.addEventListener('resize', () => {
        if (isAutoScrollEnabled) {
            scrollToBottom();
        }
    });
}

// Send a message to the server
function sendMessage() {
    const messageText = messageInput.value.trim();
    
    // Don't send empty messages or if already typing
    if (messageText === '' || isTyping) return;
    
    // Hide welcome screen if visible
    if (welcomeScreen.style.display !== 'none') {
        welcomeScreen.style.display = 'none';
    }
    
    // Add user message to chat
    addMessage(messageText, 'user');
    
    // Clear input and reset height
    messageInput.value = '';
    adjustTextareaHeight();
    
    // Add to message history
    messageHistory.unshift(messageText);
    historyIndex = -1;
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send message to server
    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: messageText,
            conversation_id: currentConversationId
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add bot response to chat
        addMessage(data.response, 'bot');
        
        // Update conversation list if this is a new conversation
        updateConversationsList();
        
        // Update statistics if available
        if (data.stats) {
            updateStatistics(data.stats);
        }
    })
    .catch(error => {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        addMessage('Sorry, there was an error processing your request. Please try again.', 'bot');
    });
}

// Add a message to the chat
function addMessage(text, sender) {
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}-message`;
    
    // Check if text is in Arabic to add RTL
    const isRTL = containsArabic(text);
    messageElement.dir = isRTL ? 'rtl' : 'ltr';
    
    // Create message content wrapper
    const contentElement = document.createElement('div');
    contentElement.className = 'message-content';
    
    // Check if we need to add date separator
    addDateSeparatorIfNeeded();
    
    // Process markdown if the message is from bot
    if (sender === 'bot') {
        // Handle markdown with marked.js (to be included in HTML)
        try {
            // We need to handle multi-line text properly before parsing markdown
            const formattedText = text.split('\n').join('\n\n');
            contentElement.innerHTML = marked.parse(formattedText);
            
            // Add appropriate dir attribute to all elements
            Array.from(contentElement.querySelectorAll('*')).forEach(el => {
                const content = el.textContent || '';
                el.dir = containsArabic(content) ? 'rtl' : 'ltr';
            });
            
            // Make links open in new tab
            contentElement.querySelectorAll('a').forEach(link => {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            });
        } catch (error) {
            console.error('Error parsing markdown:', error);
            renderPlainText(text, contentElement, isRTL);
        }
    } else {
        // Render plain text for user messages
        renderPlainText(text, contentElement, isRTL);
    }
    
    // Add timestamp
    const timeElement = document.createElement('div');
    timeElement.className = 'message-time';
    const now = new Date();
    timeElement.textContent = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    
    // Add visual feedback for new messages
    messageElement.classList.add('new-message');
    
    // Assemble message
    messageElement.appendChild(contentElement);
    messageElement.appendChild(timeElement);
    
    // Add to chat
    messages.appendChild(messageElement);
    
    // Add copy button to bot messages with markdown
    if (sender === 'bot') {
        addCopyButton(messageElement, text);
    }
    
    // Remove new-message class after animation
    setTimeout(() => {
        messageElement.classList.remove('new-message');
    }, 1000);
    
    // Scroll to the bottom if auto-scrolling is enabled
    if (isAutoScrollEnabled) {
        scrollToBottom();
    } else {
        // Show scroll to bottom button and increment unread counter
        showScrollToBottomButton();
        unreadMessages++;
        updateScrollButtonCounter();
    }
    
    // Add message to DOM
    if (welcomeScreen.style.display !== 'none') {
        welcomeScreen.style.display = 'none';
    }
    
    // Check if message was a learning request
    checkForLearningRequest(text, sender);
}

// Render plain text with proper handling of newlines and directionality
function renderPlainText(text, container, isRTL) {
    text.split('\n').forEach((line, index, array) => {
        if (line.trim() === '') {
            container.appendChild(document.createElement('br'));
            return;
        }
        
        const paragraph = document.createElement('p');
        paragraph.textContent = line;
        paragraph.dir = containsArabic(line) ? 'rtl' : 'ltr';
        container.appendChild(paragraph);
        
        // Add a line break if not the last line
        if (index < array.length - 1) {
            container.appendChild(document.createElement('br'));
        }
    });
}

// Add copy button to messages
function addCopyButton(messageElement, text) {
    const copyButton = document.createElement('button');
    copyButton.className = 'copy-btn';
    copyButton.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5 15H4C2.89543 15 2 14.1046 2 13V4C2 2.89543 2.89543 2 4 2H13C14.1046 2 15 2.89543 15 4V5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    `;
    copyButton.setAttribute('aria-label', 'Copy message');
    copyButton.setAttribute('title', 'Copy message');
    
    copyButton.addEventListener('click', () => {
        navigator.clipboard.writeText(text).then(() => {
            copyButton.classList.add('copied');
            copyButton.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `;
            
            setTimeout(() => {
                copyButton.classList.remove('copied');
                copyButton.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M5 15H4C2.89543 15 2 14.1046 2 13V4C2 2.89543 2.89543 2 4 2H13C14.1046 2 15 2.89543 15 4V5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                `;
            }, 2000);
        }).catch(err => {
            console.error('Could not copy text: ', err);
        });
    });
    
    messageElement.appendChild(copyButton);
}

// Update the scroll button with unread count
function updateScrollButtonCounter() {
    if (unreadMessages > 0) {
        scrollToBottomBtn.innerHTML = `
            <span class="unread-count">${unreadMessages}</span>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 13L12 18L17 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 6L12 11L17 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    } else {
        scrollToBottomBtn.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 13L12 18L17 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 6L12 11L17 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    }
}

// Add date separator if needed
function addDateSeparatorIfNeeded() {
    const today = new Date();
    const todayStr = today.toLocaleDateString();
    
    // Get the last date separator in the chat
    const lastSeparator = messages.querySelector('.date-separator:last-of-type');
    const lastSeparatorDate = lastSeparator ? lastSeparator.dataset.date : null;
    
    // Check if we already have a separator for today
    if (lastSeparatorDate !== todayStr) {
        const separator = document.createElement('div');
        separator.className = 'date-separator';
        separator.dataset.date = todayStr;
        
        const dateText = document.createElement('span');
        dateText.textContent = formatDate(today);
        
        separator.appendChild(dateText);
        messages.appendChild(separator);
    }
}

// Format date for separator
function formatDate(date) {
    const now = new Date();
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    
    if (date.toDateString() === now.toDateString()) {
        return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
    } else {
        return date.toLocaleDateString(undefined, { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }
}

// Check if message is a learning request
function checkForLearningRequest(text, sender) {
    if (sender !== 'user') return;
    
    // Check for "Learn:" or "تعلم:" pattern
    const englishLearnRegex = /^learn\s*:/i;
    const arabicLearnRegex = /^تعلم\s*:/i;
    
    if (englishLearnRegex.test(text) || arabicLearnRegex.test(text)) {
        // Extract the learning content
        const learningContent = text.replace(englishLearnRegex, '').replace(arabicLearnRegex, '').trim();
        
        if (learningContent) {
            // Create a system message acknowledging the learning
            const systemMessage = document.createElement('div');
            systemMessage.className = 'message system-message';
            
            const contentElement = document.createElement('div');
            contentElement.className = 'message-content';
            contentElement.textContent = '✓ I\'ve learned this response - لقد تعلمت هذا الرد';
            
            systemMessage.appendChild(contentElement);
            messages.appendChild(systemMessage);
            
            // Scroll to the bottom if auto-scrolling is enabled
            if (isAutoScrollEnabled) {
                scrollToBottom();
            }
        }
    }
}

// Show typing indicator
function showTypingIndicator() {
    isTyping = true;
    typingIndicator.classList.add('active');
    
    // Scroll to bottom when typing starts if auto-scrolling is enabled
    if (isAutoScrollEnabled) {
        scrollToBottom();
    }
}

// Hide typing indicator
function hideTypingIndicator() {
    isTyping = false;
    typingIndicator.classList.remove('active');
}

// Adjust textarea height based on content
function adjustTextareaHeight() {
    messageInput.style.height = 'auto';
    const newHeight = Math.min(messageInput.scrollHeight, 200); // Max height of 200px
    messageInput.style.height = `${newHeight}px`;
}

// Handle scroll events in the messages container
function handleScroll() {
    if (scrollTimeout) return;
    
    scrollTimeout = setTimeout(() => {
        const { scrollTop, scrollHeight, clientHeight } = messages;
        const isAtBottom = Math.abs(scrollHeight - clientHeight - scrollTop) < 30;
        
        // Check if user has scrolled up
        if (!isAtBottom) {
            if (isAutoScrollEnabled) {
                // User just scrolled up
                isAutoScrollEnabled = false;
                showScrollToBottomButton();
            }
        } else {
            // User has scrolled to bottom
            isAutoScrollEnabled = true;
            hideScrollToBottomButton();
            unreadMessages = 0;
        }
        
        // Update last scroll position
        lastScrollPosition = scrollTop;
        scrollTimeout = null;
    }, 100); // Throttle scroll events
}

// Show the scroll to bottom button
function showScrollToBottomButton() {
    scrollToBottomBtn.classList.add('show');
}

// Hide the scroll to bottom button
function hideScrollToBottomButton() {
    scrollToBottomBtn.classList.remove('show');
}

// Scroll to the bottom of the messages
function scrollToBottom() {
    const currentScroll = messages.scrollTop;
    const targetScroll = messages.scrollHeight - messages.clientHeight;
    const scrollDistance = targetScroll - currentScroll;
    
    // If we're already close to the bottom, just jump there
    if (Math.abs(scrollDistance) < 50) {
        messages.scrollTop = targetScroll;
        isAutoScrollEnabled = true;
        hideScrollToBottomButton();
        unreadMessages = 0;
        return;
    }
    
    // Otherwise, use smooth animation
    const duration = 300; // ms
    const startTime = performance.now();
    
    function scrollStep(timestamp) {
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = easeOutCubic(progress);
        
        messages.scrollTop = currentScroll + scrollDistance * easedProgress;
        
        if (progress < 1) {
            requestAnimationFrame(scrollStep);
        } else {
            isAutoScrollEnabled = true;
            hideScrollToBottomButton();
            unreadMessages = 0;
        }
    }
    
    requestAnimationFrame(scrollStep);
}

// Easing function for smooth scrolling
function easeOutCubic(x) {
    return 1 - Math.pow(1 - x, 3);
}

// Toggle sidebar visibility
function toggleSidebar() {
    sidebar.classList.toggle('show');
}

// Toggle between light and dark themes
function toggleTheme() {
    themePreference = themePreference === 'light' ? 'dark' : 'light';
    applyTheme();
    localStorage.setItem('theme', themePreference);
}

// Apply the current theme
function applyTheme() {
    document.documentElement.setAttribute('data-theme', themePreference);
}

// Navigate message history using up/down keys
function navigateHistory(direction) {
    if (messageHistory.length === 0) return;
    
    if (direction === 'up') {
        historyIndex = Math.min(historyIndex + 1, messageHistory.length - 1);
    } else {
        historyIndex = Math.max(historyIndex - 1, -1);
    }
    
    messageInput.value = historyIndex === -1 ? '' : messageHistory[historyIndex];
    
    // Move cursor to end of input
    setTimeout(() => {
        messageInput.selectionStart = messageInput.selectionEnd = messageInput.value.length;
    }, 0);
}

// Start a new conversation
function startNewConversation() {
    // Generate new conversation ID
    currentConversationId = generateConversationId();
    
    // Clear messages
    messages.innerHTML = '';
    
    // Show welcome screen
    welcomeScreen.style.display = 'flex';
    
    // Update active conversation in list
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Focus on input
    messageInput.focus();
}

// Generate a conversation ID
function generateConversationId() {
    return 'conv_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
}

// Toggle modal visibility
function toggleModal(modal, show = true) {
    if (show) {
        modal.classList.add('show');
        
        // If it's the stats modal, fetch latest stats
        if (modal.id === 'stats-modal') {
            fetchStatistics();
        }
    } else {
        modal.classList.remove('show');
    }
}

// Fetch statistics from the server
function fetchStatistics() {
    fetch('/get_statistics', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        updateStatistics(data);
    })
    .catch(error => {
        console.error('Error fetching statistics:', error);
    });
}

// Update statistics display
function updateStatistics(stats) {
    document.getElementById('learned-responses').textContent = stats.learned_responses || '0';
    document.getElementById('conversation-sessions').textContent = stats.conversation_sessions || '0';
    document.getElementById('popular-topics').textContent = stats.popular_topics?.join(', ') || 'None yet';
}

// Load conversation history from the server
function loadConversationHistory() {
    fetch('/get_conversations', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        if (data.conversations && data.conversations.length > 0) {
            renderConversationList(data.conversations);
        }
    })
    .catch(error => {
        console.error('Error loading conversations:', error);
    });
}

// Render the conversation list
function renderConversationList(conversations) {
    // Clear existing list except for the new chat button
    const newChatButton = conversationList.querySelector('.new-chat-btn');
    conversationList.innerHTML = '';
    conversationList.appendChild(newChatButton);
    
    // Add conversations to the list
    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'conversation-item';
        item.dataset.id = conv.id;
        
        if (conv.id === currentConversationId) {
            item.classList.add('active');
        }
        
        item.innerHTML = `
            <div class="conversation-content">
                <div class="conversation-title">${conv.title || 'Conversation'}</div>
                <div class="conversation-preview">${conv.preview || 'No messages'}</div>
            </div>
        `;
        
        item.addEventListener('click', () => loadConversation(conv.id));
        conversationList.appendChild(item);
    });
}

// Load a specific conversation
function loadConversation(conversationId) {
    fetch(`/get_conversation/${conversationId}`, {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        if (data.messages) {
            // Update current conversation ID
            currentConversationId = conversationId;
            
            // Clear messages
            messages.innerHTML = '';
            
            // Add messages to chat
            data.messages.forEach(msg => {
                addMessage(msg.text, msg.sender);
            });
            
            // Update active conversation in list
            document.querySelectorAll('.conversation-item').forEach(item => {
                item.classList.remove('active');
                if (item.dataset.id === conversationId) {
                    item.classList.add('active');
                }
            });
            
            // Hide welcome screen
            welcomeScreen.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error loading conversation:', error);
    });
}

// Update the conversation list
function updateConversationsList() {
    loadConversationHistory();
}

// Utility function to check if text contains Arabic
function containsArabic(text) {
    const arabicRegex = /[\u0600-\u06FF]/;
    return arabicRegex.test(text);
}

// Function to detect language and set direction
function detectLanguage(text) {
    // Check for Arabic characters
    const arabicRegex = /[\u0600-\u06FF]/;
    const hasArabic = arabicRegex.test(text);
    
    // Check for English or other Latin characters
    const latinRegex = /[a-zA-Z]/;
    const hasLatin = latinRegex.test(text);
    
    // If contains Arabic and no Latin, or Arabic is more dominant
    if (hasArabic && (!hasLatin || text.match(arabicRegex).length > text.match(latinRegex).length)) {
        return 'rtl';
    }
    
    return 'ltr';
} 