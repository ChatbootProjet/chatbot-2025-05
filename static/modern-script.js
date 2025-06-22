/**
 * Modern AI Chatbot - Frontend Script
 * Enhanced functionality for the modern chatbot interface
 */

// DOM Elements
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const messagesContainer = document.getElementById('messages-container');
const messages = document.getElementById('messages');
const welcomeScreen = document.getElementById('welcome-screen');
const typingIndicator = document.getElementById('typing-indicator');
const scrollToBottomBtn = document.getElementById('scroll-to-bottom');
const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
const sidebar = document.getElementById('sidebar');
const toggleThemeBtn = document.getElementById('toggle-theme-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const statsButton = document.getElementById('stats-button');
const statsModal = document.getElementById('stats-modal');
const helpButton = document.getElementById('help-button');
const helpModal = document.getElementById('help-modal');
const conversationList = document.getElementById('conversation-list');
const charCount = document.getElementById('char-count');
const unreadCount = document.getElementById('unread-count');
const chatTitle = document.getElementById('chat-title');

// Global State
let messageHistory = [];
let historyIndex = -1;
let isTyping = false;
let currentConversationId = null;
let unreadMessages = 0;
let isAutoScrollEnabled = true;
let themePreference = localStorage.getItem('theme') || 'light';
let learningChart = null;
let lastScrollPosition = 0;
let scrollTimeout = null;

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    applyTheme();
    loadConversationHistory();
    updateCharacterCount();
    checkFirebaseStatus();
    enhanceMarkdownDisplay();
    autoEnhanceNewMessages();
});

// Initialize the application
function initializeApp() {
    // Focus on input field
    messageInput.focus();
    
    // Generate conversation ID if needed
    if (!currentConversationId) {
        currentConversationId = generateConversationId();
    }
    
    // Show/hide welcome screen
    toggleWelcomeScreen();
    
    // Setup auto-resize for textarea
    setupTextareaAutoResize();
    
    // Initialize scroll position
    setTimeout(() => {
        scrollToBottom(false);
    }, 100);
    
   
}

// Setup all event listeners
function setupEventListeners() {
    // Send message events
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', handleInputKeydown);
    messageInput.addEventListener('input', handleInputChange);
    
    // Scroll events
    messages.addEventListener('scroll', handleScroll);
    scrollToBottomBtn.addEventListener('click', () => scrollToBottom(true));
    
    // Navigation events
    mobileSidebarToggle.addEventListener('click', toggleSidebar);
    toggleThemeBtn.addEventListener('click', toggleTheme);
    newChatBtn.addEventListener('click', startNewConversation);
    
    // Modal events
    statsButton.addEventListener('click', () => openModal(statsModal));
    helpButton.addEventListener('click', () => openModal(helpModal));
    
    // Close modal events
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            closeModal(modal);
        });
    });
    
    // Click outside modal to close
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal);
            }
        });
    });
    
    // Quick action buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const message = e.target.closest('.quick-action-btn').dataset.message;
            if (message) {
                messageInput.value = message;
                sendMessage();
            }
        });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleGlobalKeydown);
    
    // Window events
    window.addEventListener('resize', handleWindowResize);
    window.addEventListener('beforeunload', saveConversationState);
    
    // Focus management
    document.addEventListener('click', handleDocumentClick);
}

// Handle input keydown events
function handleInputKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    } else if (e.key === 'ArrowUp' && messageInput.value === '') {
        e.preventDefault();
        navigateHistory('up');
    } else if (e.key === 'ArrowDown' && messageInput.value === '') {
        e.preventDefault();
        navigateHistory('down');
    }
}

// Handle input change events
function handleInputChange() {
    updateCharacterCount();
    adjustTextareaHeight();
}

// Handle global keyboard shortcuts
function handleGlobalKeydown(e) {
    // Alt+D - Toggle dark mode
    if (e.altKey && e.key === 'd') {
        e.preventDefault();
        toggleTheme();
    }
    
    // Alt+S - Toggle sidebar (mobile)
    if (e.altKey && e.key === 's') {
        e.preventDefault();
        toggleSidebar();
    }
    
    // Escape - Close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.show').forEach(modal => {
            closeModal(modal);
        });
    }
}

// Handle window resize
function handleWindowResize() {
    if (isAutoScrollEnabled) {
        scrollToBottom(false);
    }
}

// Handle document click for focus management
function handleDocumentClick(e) {
    const isModal = e.target.closest('.modal');
    const isButton = e.target.closest('button');
    const isLink = e.target.tagName === 'A';
    const isInput = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA';
    
    if (!isModal && !isButton && !isLink && !isInput) {
        messageInput.focus();
    }
}

// Send message function
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || isTyping) return;
    
    // Add to history
    messageHistory.unshift(text);
    if (messageHistory.length > 50) {
        messageHistory.pop();
    }
    historyIndex = -1;
    
    // Clear input and hide welcome screen
    messageInput.value = '';
    updateCharacterCount();
    adjustTextareaHeight();
    hideWelcomeScreen();
    
    // Add user message
    addMessage(text, 'user');
    
    // Show typing indicator
    showTypingIndicator();
    isTyping = true;
    
    try {
        // Get auth headers if available
        const headers = window.getAuthHeaders ? await window.getAuthHeaders() : {
            'Content-Type': 'application/json'
        };
        
        // Send to backend using the send_message endpoint
        const response = await fetch('/send_message', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                message: text,
                conversation_id: currentConversationId
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Update conversation ID if it was created by backend
        if (data.conversation_id) {
            currentConversationId = data.conversation_id;
        }
        
        // Update conversation title if AI generated one
        if (data.conversation_title) {
            updateChatTitle(data.conversation_title);
        }
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add bot response
        addMessage(data.response, 'bot');
        
        // Update conversation list
        await loadConversationHistory();
        
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        addMessage('عذراً، حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.\nSorry, there was a connection error. Please try again.', 'bot');
    } finally {
        isTyping = false;
        messageInput.focus();
    }
    
    setTimeout(() => {
        enhanceMarkdownDisplay();
    }, 500);
}

// Add message to chat
function addMessage(text, sender, messageId = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.setAttribute('data-sender', sender);
    
    // Generate unique message ID if not provided
    if (!messageId) {
        messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    messageDiv.setAttribute('data-message-id', messageId);
    
    // Create avatar
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    
    if (sender === 'user') {
        avatar.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    } else {
        avatar.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="20" height="20" rx="5" stroke="currentColor" stroke-width="2"/><circle cx="8" cy="10" r="2" fill="currentColor"/><circle cx="16" cy="10" r="2" fill="currentColor"/><path d="M8 16h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
    }
    
    // Create content
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Detect language and set direction
    const isRTL = containsArabic(text);
    messageDiv.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
    
    // Process message content
    if (sender === 'bot') {
        // Render markdown for bot messages
        try {
            const parsedContent = marked.parse(text);
            content.innerHTML = parsedContent;
        } catch (error) {
            content.textContent = text;
        }
    } else {
        content.textContent = text;
    }
    
    // Create message actions
    const actions = createMessageActions(sender, text, messageId);
    
    // Assemble message
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    messageDiv.appendChild(actions);
    
    // Add to messages container
    messages.appendChild(messageDiv);
    
    // Check for learning request
    if (sender === 'user') {
        checkForLearningRequest(text);
    }
    
    // Scroll to bottom
    if (isAutoScrollEnabled) {
        scrollToBottom(true);
    } else {
        updateUnreadCount();
    }
    
    // Update scroll button visibility
    updateScrollButtonVisibility();
    
    return messageId;
}

// Show typing indicator
function showTypingIndicator() {
    typingIndicator.classList.add('active');
    if (isAutoScrollEnabled) {
        scrollToBottom(true);
    }
}

// Hide typing indicator
function hideTypingIndicator() {
    typingIndicator.classList.remove('active');
}

// Toggle welcome screen
function toggleWelcomeScreen() {
    const hasMessages = messages.children.length > 0;
    welcomeScreen.style.display = hasMessages ? 'none' : 'flex';
}

// Hide welcome screen
function hideWelcomeScreen() {
    welcomeScreen.style.display = 'none';
}

// Setup textarea auto-resize
function setupTextareaAutoResize() {
    messageInput.addEventListener('input', adjustTextareaHeight);
}

// Adjust textarea height
function adjustTextareaHeight() {
    messageInput.style.height = 'auto';
    const scrollHeight = messageInput.scrollHeight;
    const maxHeight = 120; // 5 lines approximately
    messageInput.style.height = Math.min(scrollHeight, maxHeight) + 'px';
}

// Update character count
function updateCharacterCount() {
    const count = messageInput.value.length;
    charCount.textContent = count;
    
    // Change color based on limit
    if (count > 1800) {
        charCount.style.color = 'var(--error-color, #ef4444)';
    } else if (count > 1500) {
        charCount.style.color = 'var(--warning-color, #f59e0b)';
    } else {
        charCount.style.color = 'var(--text-muted)';
    }
}

// Handle scroll events
function handleScroll() {
    if (scrollTimeout) {
        clearTimeout(scrollTimeout);
    }
    
    scrollTimeout = setTimeout(() => {
        const scrollTop = messages.scrollTop;
        const scrollHeight = messages.scrollHeight;
        const clientHeight = messages.clientHeight;
        
        // Check if at bottom
        const isAtBottom = scrollTop + clientHeight >= scrollHeight - 50;
        isAutoScrollEnabled = isAtBottom;
        
        // Update scroll button
        updateScrollButtonVisibility();
        
        // Reset unread count if at bottom
        if (isAtBottom) {
            unreadMessages = 0;
            updateUnreadCount();
        }
        
        lastScrollPosition = scrollTop;
    }, 100);
}

// Update scroll button visibility
function updateScrollButtonVisibility() {
    const scrollTop = messages.scrollTop;
    const scrollHeight = messages.scrollHeight;
    const clientHeight = messages.clientHeight;
    const isAtBottom = scrollTop + clientHeight >= scrollHeight - 50;
    
    if (isAtBottom) {
        scrollToBottomBtn.classList.remove('show');
    } else {
        scrollToBottomBtn.classList.add('show');
    }
}

// Update unread count
function updateUnreadCount() {
    if (unreadMessages > 0) {
        unreadCount.textContent = unreadMessages;
        unreadCount.classList.add('show');
    } else {
        unreadCount.classList.remove('show');
    }
}

// Scroll to bottom
function scrollToBottom(animate = true) {
    const scrollHeight = messages.scrollHeight;
    const clientHeight = messages.clientHeight;
    const targetScroll = scrollHeight - clientHeight;
    
    if (animate) {
        messages.scrollTo({
            top: targetScroll,
            behavior: 'smooth'
        });
    } else {
        messages.scrollTop = targetScroll;
    }
    
    isAutoScrollEnabled = true;
    unreadMessages = 0;
    updateUnreadCount();
    updateScrollButtonVisibility();
}

// Toggle sidebar (mobile)
function toggleSidebar() {
    sidebar.classList.toggle('show');
}

// Toggle theme
function toggleTheme() {
    themePreference = themePreference === 'light' ? 'dark' : 'light';
    applyTheme();
    localStorage.setItem('theme', themePreference);
}

// Apply theme
function applyTheme() {
    document.documentElement.setAttribute('data-theme', themePreference);
}

// Navigate message history
function navigateHistory(direction) {
    if (messageHistory.length === 0) return;
    
    if (direction === 'up') {
        historyIndex = Math.min(historyIndex + 1, messageHistory.length - 1);
    } else {
        historyIndex = Math.max(historyIndex - 1, -1);
    }
    
    if (historyIndex >= 0) {
        messageInput.value = messageHistory[historyIndex];
    } else {
        messageInput.value = '';
    }
    
    updateCharacterCount();
    adjustTextareaHeight();
    messageInput.focus();
}

// Start new conversation
async function startNewConversation() {
    // Show loading state
    const newChatBtn = document.getElementById('new-chat-btn');
    const originalText = newChatBtn.innerHTML;
    
    // Generate AI title for previous conversation if it exists and has messages
    if (currentConversationId && messages.children.length > 0) {
        try {
            // Show generating title state
            newChatBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="animate-spin">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-dasharray="31.416" stroke-dashoffset="31.416">
                        <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                        <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
                    </circle>
                </svg>
                <span>Generating title...</span>
            `;
            
            await generateTitleForPreviousConversation(currentConversationId);
        } catch (error) {
            console.error('Error generating title for previous conversation:', error);
        } finally {
            // Restore original button text
            newChatBtn.innerHTML = originalText;
        }
    }
    
    // Clear messages
    messages.innerHTML = '';
    
    // Generate new conversation ID
    currentConversationId = generateConversationId();
    
    // Show welcome screen
    toggleWelcomeScreen();
    
    // Reset state
    unreadMessages = 0;
    updateUnreadCount();
    
    // Update title
    updateChatTitle('AI Assistant');
    
    // Update active conversation in sidebar
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Reload conversation list to show updated titles
    await loadConversationHistory();
    
    // Focus input
    messageInput.focus();
    
    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
        sidebar.classList.remove('show');
    }
}

// Generate AI title for previous conversation
async function generateTitleForPreviousConversation(conversationId) {
    try {
        const response = await fetch('/generate_conversation_title', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                conversation_id: conversationId
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log(`Generated AI title for conversation ${conversationId}: "${data.title}"`);
            return data.title;
        } else {
            console.error('Failed to generate AI title:', response.status);
            return null;
        }
    } catch (error) {
        console.error('Error generating AI title:', error);
        return null;
    }
}

// Generate conversation ID
function generateConversationId() {
    return Date.now().toString() + '.' + Math.random().toString().substr(2);
}

// Open modal
function openModal(modal) {
    modal.classList.add('show');
    
    // Initialize stats if stats modal
    if (modal === statsModal) {
        loadStatistics();
    }
}

// Close modal
function closeModal(modal) {
    modal.classList.remove('show');
}

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch('/stats');
        if (response.ok) {
            const stats = await response.json();
            updateStatisticsDisplay(stats);
            initializeChart(stats);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Update statistics display
function updateStatisticsDisplay(stats) {
    document.getElementById('learned-responses').textContent = stats.learned_responses || 0;
    document.getElementById('conversation-sessions').textContent = stats.conversation_sessions || 0;
    document.getElementById('popular-topics').textContent = stats.popular_topics || 'لا يوجد';
}

// Initialize chart
function initializeChart(stats) {
    const ctx = document.getElementById('learning-chart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (learningChart) {
        learningChart.destroy();
    }
    
    learningChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
            datasets: [{
                label: 'الردود المتعلمة',
                data: stats.learning_progress || [0, 2, 5, 8, 12, 15],
                borderColor: 'var(--primary-color)',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'var(--border-color)'
                    },
                    ticks: {
                        color: 'var(--text-secondary)'
                    }
                },
                x: {
                    grid: {
                        color: 'var(--border-color)'
                    },
                    ticks: {
                        color: 'var(--text-secondary)'
                    }
                }
            }
        }
    });
}

// Load conversation history
async function loadConversationHistory() {
    try {
        console.log('Loading conversation history...'); // Debug log
        
        // Get auth headers if available
        const headers = window.getAuthHeaders ? await window.getAuthHeaders() : {};
        headers['Content-Type'] = 'application/json';
        
        const response = await fetch('/get_conversations', {
            method: 'GET',
            headers: headers
        });
        
        console.log('Conversations response status:', response.status); // Debug log
        
        if (response.ok) {
            const data = await response.json();
            console.log('Conversations data:', data); // Debug log
            updateConversationsList(data.conversations || []);
        } else {
            console.error('Failed to load conversations:', response.status);
            updateConversationsList([]);
        }
    } catch (error) {
        console.error('Error loading conversation history:', error);
        updateConversationsList([]);
    }
}

// Update conversations list
function updateConversationsList(conversations = []) {
    // Clear existing conversations
    conversationList.innerHTML = '';
    
    if (conversations.length === 0) {
        const placeholder = document.createElement('div');
        placeholder.className = 'conversation-placeholder';
        placeholder.innerHTML = `
            <div style="text-align: center; padding: var(--space-4); color: var(--text-muted); font-size: var(--font-size-sm);">
                <p>Previous conversations will appear here</p>
                <p>ستظهر المحادثات السابقة هنا</p>
            </div>
        `;
        conversationList.appendChild(placeholder);
        return;
    }
    
    // Add conversations
    conversations.forEach(conversation => {
        const conversationItem = document.createElement('div');
        conversationItem.className = 'conversation-item';
        conversationItem.setAttribute('data-conversation-id', conversation.id);
        
        // Check if this is the current conversation
        if (conversation.id === currentConversationId) {
            conversationItem.classList.add('active');
        }
        
        conversationItem.innerHTML = `
            <div class="conversation-content">
                <div class="conversation-title">${escapeHtml(conversation.title)}</div>
                <div class="conversation-preview">${escapeHtml(conversation.preview)}</div>
                <div class="conversation-time">${formatTimestamp(conversation.timestamp)}</div>
            </div>
            <div class="conversation-options">
                <button class="options-btn" data-conversation-id="${conversation.id}">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="1" fill="currentColor"/>
                        <circle cx="12" cy="5" r="1" fill="currentColor"/>
                        <circle cx="12" cy="19" r="1" fill="currentColor"/>
                    </svg>
                </button>
            </div>
        `;
        
        // Add click handler for conversation content
        const conversationContent = conversationItem.querySelector('.conversation-content');
        conversationContent.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Conversation clicked:', conversation.id); // Debug log
            loadConversation(conversation.id);
        });
        
        // Add click handler for the entire conversation item as fallback
        conversationItem.addEventListener('click', (e) => {
            // Only handle click if it's not on the options button
            if (!e.target.closest('.options-btn')) {
                e.preventDefault();
                console.log('Conversation item clicked:', conversation.id); // Debug log
                loadConversation(conversation.id);
            }
        });
        
        // Add click handler for options button
        const optionsBtn = conversationItem.querySelector('.options-btn');
        optionsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            showConversationOptions(conversation.id, conversation.title, e.target.closest('.options-btn'));
        });
        
        conversationList.appendChild(conversationItem);
    });
}

// Load a specific conversation
async function loadConversation(conversationId) {
    console.log('Loading conversation:', conversationId); // Debug log
    
    try {
        // Show loading indicator
        showTypingIndicator();
        
        // Get auth headers if available
        const headers = window.getAuthHeaders ? await window.getAuthHeaders() : {};
        headers['Content-Type'] = 'application/json';
        
        const response = await fetch(`/get_conversation/${conversationId}`, {
            method: 'GET',
            headers: headers
        });
        
        console.log('Response status:', response.status); // Debug log
        
        if (response.ok) {
            const data = await response.json();
            console.log('Conversation data:', data); // Debug log
            
            // Clear current messages
            messages.innerHTML = '';
            
            // Load messages
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    addMessage(message.text, message.sender);
                });
            } else {
                console.log('No messages found in conversation');
            }
            
            // Update current conversation ID
            currentConversationId = conversationId;
            
            // Update active conversation in sidebar
            document.querySelectorAll('.conversation-item').forEach(item => {
                item.classList.remove('active');
            });
            const activeItem = document.querySelector(`[data-conversation-id="${conversationId}"]`);
            if (activeItem) {
                activeItem.classList.add('active');
                console.log('Marked conversation as active');
            }
            
            // Hide welcome screen
            hideWelcomeScreen();
            
            // Update chat title if available
            const conversationTitle = activeItem?.querySelector('.conversation-title')?.textContent;
            if (conversationTitle) {
                updateChatTitle(conversationTitle);
            }
            
            // Scroll to bottom
            setTimeout(() => {
                scrollToBottom(false);
            }, 100);
            
            // Close sidebar on mobile
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('show');
            }
            
            // Show success notification
            showNotification('المحادثة تم تحميلها | Conversation loaded', 'success');
            
        } else {
            const errorData = await response.json().catch(() => ({}));
            console.error('Error response:', errorData);
            showNotification('خطأ في تحميل المحادثة | Error loading conversation', 'error');
        }
    } catch (error) {
        console.error('Error loading conversation:', error);
        showNotification('خطأ في الاتصال | Connection error', 'error');
    } finally {
        // Hide loading indicator
        hideTypingIndicator();
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Utility function to format timestamp
function formatTimestamp(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diff = now - date;
    
    // Less than 1 minute
    if (diff < 60000) {
        return 'Just now';
    }
    
    // Less than 1 hour
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes}m ago`;
    }
    
    // Less than 1 day
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours}h ago`;
    }
    
    // Less than 1 week
    if (diff < 604800000) {
        const days = Math.floor(diff / 86400000);
        return `${days}d ago`;
    }
    
    // More than 1 week - show date
    return date.toLocaleDateString();
}

// Check for learning request
function checkForLearningRequest(text) {
    const learningPatterns = [
        /^تعلم:\s*(.+)/i,
        /^learn:\s*(.+)/i
    ];
    
    for (const pattern of learningPatterns) {
        const match = text.match(pattern);
        if (match) {
            // This is a learning request
            // The actual learning logic would be handled by the backend
            break;
        }
    }
}

// Update chat title
function updateChatTitle(title) {
    chatTitle.textContent = title;
}

// Update chat status
function updateChatStatus(status) {
    chatStatus.textContent = status;
}

// Save conversation state
function saveConversationState() {
    // This would typically save to backend or localStorage
    // For now, we'll just log
    console.log('Saving conversation state...');
}

// Utility function to detect Arabic text
function containsArabic(text) {
    const arabicRegex = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
    return arabicRegex.test(text);
}

// Utility function to detect language
function detectLanguage(text) {
    return containsArabic(text) ? 'ar' : 'en';
}

// Show conversation options menu
function showConversationOptions(conversationId, currentTitle, buttonElement) {
    // Remove any existing options menu
    const existingMenu = document.querySelector('.conversation-options-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    // Create options menu
    const optionsMenu = document.createElement('div');
    optionsMenu.className = 'conversation-options-menu';
    optionsMenu.innerHTML = `
        <div class="options-menu-item" data-action="rename">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="m18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>إعادة تسمية | Rename</span>
        </div>
        <div class="options-menu-item" data-action="delete">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <polyline points="3,6 5,6 21,6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>حذف | Delete</span>
        </div>
    `;
    
    // Position menu near the button
    const rect = buttonElement.getBoundingClientRect();
    optionsMenu.style.position = 'fixed';
    optionsMenu.style.top = rect.bottom + 5 + 'px';
    optionsMenu.style.left = rect.left - 100 + 'px';
    optionsMenu.style.zIndex = '1000';
    
    // Add to document
    document.body.appendChild(optionsMenu);
    
    // Add event listeners
    optionsMenu.addEventListener('click', async (e) => {
        const menuItem = e.target.closest('.options-menu-item');
        if (menuItem) {
            const action = menuItem.dataset.action;
            
            if (action === 'rename') {
                await renameConversation(conversationId, currentTitle);
            } else if (action === 'delete') {
                await deleteConversation(conversationId);
            }
            
            optionsMenu.remove();
        }
    });
    
    // Close menu when clicking outside
    setTimeout(() => {
        document.addEventListener('click', function closeMenu(e) {
            if (!optionsMenu.contains(e.target)) {
                optionsMenu.remove();
                document.removeEventListener('click', closeMenu);
            }
        });
    }, 100);
}

// Rename conversation
async function renameConversation(conversationId, currentTitle) {
    // Create a better modal dialog instead of using prompt
    const newTitle = await showRenameDialog(currentTitle);
    
    if (newTitle && newTitle.trim() !== currentTitle) {
        try {
            // Get auth headers if available
            const headers = window.getAuthHeaders ? await window.getAuthHeaders() : {
                'Content-Type': 'application/json'
            };
            
            const response = await fetch('/update_conversation_title', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    conversation_id: conversationId,
                    title: newTitle.trim()
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Rename successful:', result);
                
                // Update current chat title if this is the active conversation
                if (conversationId === currentConversationId) {
                    updateChatTitle(newTitle.trim());
                }
                
                // Reload conversation list to reflect changes
                await loadConversationHistory();
                
                // Show success message
                showNotification('تم تغيير اسم المحادثة بنجاح | Conversation renamed successfully', 'success');
            } else {
                const error = await response.json();
                console.error('Rename failed:', error);
                showNotification('فشل في تغيير اسم المحادثة | Failed to rename conversation', 'error');
            }
        } catch (error) {
            console.error('Error renaming conversation:', error);
            showNotification('حدث خطأ في تغيير الاسم | Error occurred while renaming', 'error');
        }
    }
}

// Show rename dialog (better than prompt)
function showRenameDialog(currentTitle) {
    return new Promise((resolve) => {
        // Remove any existing rename dialog
        const existingDialog = document.querySelector('.rename-dialog');
        if (existingDialog) {
            existingDialog.remove();
        }
        
        // Create dialog
        const dialog = document.createElement('div');
        dialog.className = 'rename-dialog';
        dialog.innerHTML = `
            <div class="rename-dialog-overlay"></div>
            <div class="rename-dialog-content">
                <h3>إعادة تسمية المحادثة | Rename Conversation</h3>
                <input type="text" id="rename-input" value="${escapeHtml(currentTitle)}" placeholder="أدخل اسم المحادثة الجديد | Enter new title">
                <div class="rename-dialog-actions">
                    <button id="rename-cancel" class="btn-secondary">إلغاء | Cancel</button>
                    <button id="rename-confirm" class="btn-primary">تأكيد | Confirm</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        const input = dialog.querySelector('#rename-input');
        const cancelBtn = dialog.querySelector('#rename-cancel');
        const confirmBtn = dialog.querySelector('#rename-confirm');
        
        // Focus and select text
        setTimeout(() => {
            input.focus();
            input.select();
        }, 100);
        
        // Handle confirm
        const handleConfirm = () => {
            const newTitle = input.value.trim();
            dialog.remove();
            resolve(newTitle || null);
        };
        
        // Handle cancel
        const handleCancel = () => {
            dialog.remove();
            resolve(null);
        };
        
        // Event listeners
        confirmBtn.addEventListener('click', handleConfirm);
        cancelBtn.addEventListener('click', handleCancel);
        
        // Enter key to confirm
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleConfirm();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                handleCancel();
            }
        });
        
        // Click overlay to cancel
        dialog.querySelector('.rename-dialog-overlay').addEventListener('click', handleCancel);
    });
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove any existing notification
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Hide notification after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 3000);
}

// Delete conversation
async function deleteConversation(conversationId) {
    const confirmMessage = 'هل أنت متأكد من حذف هذه المحادثة؟ لا يمكن التراجع عن هذا الإجراء.\n\nAre you sure you want to delete this conversation? This action cannot be undone.';
    
    if (confirm(confirmMessage)) {
        try {
            // Get auth headers if available
            const headers = window.getAuthHeaders ? await window.getAuthHeaders() : {
                'Content-Type': 'application/json'
            };
            
            const response = await fetch('/delete_conversation', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    conversation_id: conversationId
                })
            });
            
            if (response.ok) {
                console.log('Conversation deleted successfully');
                
                // If this is the current conversation, start a new one
                if (conversationId === currentConversationId) {
                    startNewConversation();
                }
                
                // Reload conversation list
                await loadConversationHistory();
                
                // Show success message
                showNotification('تم حذف المحادثة بنجاح | Conversation deleted successfully', 'success');
            } else {
                const error = await response.json();
                console.error('Delete failed:', error);
                showNotification('فشل في حذف المحادثة | Failed to delete conversation', 'error');
            }
        } catch (error) {
            console.error('Error deleting conversation:', error);
            showNotification('حدث خطأ في حذف المحادثة | Error occurred while deleting', 'error');
        }
    }
}

// ============================================================================
// FIREBASE INTEGRATION FUNCTIONS - وظائف تكامل Firebase
// ============================================================================

// Check Firebase status
async function checkFirebaseStatus() {
    try {
        const response = await fetch('/firebase_status');
        const data = await response.json();
        
        if (data.firebase_initialized) {
            console.log('🔥 Firebase is available');
        } else {
            console.log('💾 Firebase not available, using local storage');
        }
    } catch (error) {
        console.error('Error checking Firebase status:', error);
    }
}

// Get Firebase authentication headers
function getAuthHeaders() {
    const headers = {};
    
    // Add Firebase ID token if available
    if (window.firebase && firebase.auth && firebase.auth().currentUser) {
        return firebase.auth().currentUser.getIdToken().then(token => {
            return {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            };
        });
    }
    
    return headers;
}

// Export functions for potential external use
window.ChatBot = {
    sendMessage,
    toggleTheme,
    startNewConversation,
    scrollToBottom,
    checkFirebaseStatus
};

// Make getAuthHeaders available globally for other scripts
window.getAuthHeaders = getAuthHeaders;

// ============= MESSAGE ACTIONS FUNCTIONS =============

// Create message actions buttons
function createMessageActions(sender, text, messageId) {
    const actions = document.createElement('div');
    actions.className = 'message-actions';
    
    // Copy message button
    const copyBtn = document.createElement('button');
    copyBtn.className = 'message-action-btn';
    copyBtn.title = 'نسخ الرسالة / Copy Message';
    copyBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
    </svg>`;
    copyBtn.addEventListener('click', () => copyMessage(text));
    actions.appendChild(copyBtn);
    
    if (sender === 'user') {
        // Edit message button (for user messages)
        const editBtn = document.createElement('button');
        editBtn.className = 'message-action-btn';
        editBtn.title = 'تعديل الرسالة / Edit Message';
        editBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>`;
        editBtn.addEventListener('click', () => editMessage(messageId, text));
        actions.appendChild(editBtn);
        
        // Regenerate button
        const regenBtn = document.createElement('button');
        regenBtn.className = 'message-action-btn';
        regenBtn.title = 'إعادة التوليد / Regenerate';
        regenBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
        </svg>`;
        regenBtn.addEventListener('click', () => regenerateFromMessage(messageId, text));
        actions.appendChild(regenBtn);
    }
    
    // Delete message button
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'message-action-btn danger';
    deleteBtn.title = 'حذف الرسالة / Delete Message';
    deleteBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="3,6 5,6 21,6"></polyline>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        <line x1="10" y1="11" x2="10" y2="17"></line>
        <line x1="14" y1="11" x2="14" y2="17"></line>
    </svg>`;
    deleteBtn.addEventListener('click', () => deleteMessage(messageId));
    actions.appendChild(deleteBtn);
    
    return actions;
}

// Copy message to clipboard
async function copyMessage(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('تم نسخ الرسالة! / Message copied!', 'success');
    } catch (error) {
        console.error('Failed to copy message:', error);
        showNotification('فشل في نسخ الرسالة / Failed to copy message', 'error');
    }
}

// Edit message
function editMessage(messageId, currentText) {
    const messageDiv = document.querySelector(`[data-message-id="${messageId}"]`);
    if (!messageDiv) return;
    
    const contentDiv = messageDiv.querySelector('.message-content');
    const actionsDiv = messageDiv.querySelector('.message-actions');
    
    // Hide actions during edit
    actionsDiv.style.display = 'none';
    
    // Create edit form
    const editForm = document.createElement('div');
    editForm.className = 'message-edit-form';
    editForm.innerHTML = `
        <textarea class="edit-textarea" rows="3">${currentText}</textarea>
        <div class="edit-actions">
            <button class="edit-save-btn">حفظ / Save</button>
            <button class="edit-cancel-btn">إلغاء / Cancel</button>
        </div>
    `;
    
    // Replace content with edit form
    contentDiv.style.display = 'none';
    messageDiv.appendChild(editForm);
    
    const textarea = editForm.querySelector('.edit-textarea');
    const saveBtn = editForm.querySelector('.edit-save-btn');
    const cancelBtn = editForm.querySelector('.edit-cancel-btn');
    
    // Auto-resize textarea
    textarea.addEventListener('input', () => {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    });
    
    // Focus and select text
    textarea.focus();
    textarea.select();
    
    // Save edit
    saveBtn.addEventListener('click', () => {
        const newText = textarea.value.trim();
        if (newText && newText !== currentText) {
            // Update message content
            contentDiv.textContent = newText;
            
            // Regenerate response with new prompt
            regenerateFromMessage(messageId, newText);
        }
        
        // Restore original view
        contentDiv.style.display = 'block';
        actionsDiv.style.display = 'flex';
        editForm.remove();
    });
    
    // Cancel edit
    cancelBtn.addEventListener('click', () => {
        contentDiv.style.display = 'block';
        actionsDiv.style.display = 'flex';
        editForm.remove();
    });
    
    // Handle Enter key
    textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            saveBtn.click();
        } else if (e.key === 'Escape') {
            cancelBtn.click();
        }
    });
}

// Regenerate from message
async function regenerateFromMessage(messageId, userText) {
    try {
        // Find the message and remove all subsequent messages
        const messageDiv = document.querySelector(`[data-message-id="${messageId}"]`);
        if (!messageDiv) return;
        
        // Remove all messages after this one
        let nextSibling = messageDiv.nextElementSibling;
        while (nextSibling) {
            const toRemove = nextSibling;
            nextSibling = nextSibling.nextElementSibling;
            toRemove.remove();
        }
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send regeneration request
        const headers = await getAuthHeaders();
        const response = await fetch('/chat', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                message: userText,
                conversation_id: currentConversationId,
                regenerate: true
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        if (data.response) {
            // Add new bot response
            addMessage(data.response, 'bot');
            showNotification('تم إعادة التوليد! / Response regenerated!', 'success');
        } else {
            throw new Error('No response received');
        }
        
    } catch (error) {
        console.error('Error regenerating response:', error);
        hideTypingIndicator();
        showNotification('فشل في إعادة التوليد / Failed to regenerate response', 'error');
    }
}

// Delete message
function deleteMessage(messageId) {
    if (confirm('هل أنت متأكد من حذف هذه الرسالة؟ / Are you sure you want to delete this message?')) {
        const messageDiv = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageDiv) {
            messageDiv.remove();
            showNotification('تم حذف الرسالة! / Message deleted!', 'success');
        }
    }
}

// Enhanced Markdown and Code Processing
function enhanceMarkdownDisplay() {
    // Process all messages for better Markdown display
    document.querySelectorAll('.message-content').forEach(messageContent => {
        if (!messageContent.classList.contains('markdown-processed')) {
            processMarkdownContent(messageContent);
            messageContent.classList.add('markdown-processed');
        }
    });
}

function processMarkdownContent(element) {
    // Add copy buttons to code blocks
    const codeBlocks = element.querySelectorAll('pre code');
    codeBlocks.forEach((codeBlock, index) => {
        addCopyButtonToCodeBlock(codeBlock, index);
    });
    
    // Enhance other Markdown elements
    enhanceMarkdownElements(element);
}

function addCopyButtonToCodeBlock(codeBlock, index) {
    const pre = codeBlock.parentElement;
    if (pre.querySelector('.code-copy-btn')) return; // Already has button
    
    // Create wrapper for code block
    const wrapper = document.createElement('div');
    wrapper.className = 'code-block-wrapper';
    
    // Create header with copy button
    const header = document.createElement('div');
    header.className = 'code-block-header';
    
    // Detect language
    const language = detectCodeLanguage(codeBlock);
    const languageLabel = document.createElement('span');
    languageLabel.className = 'code-language-label';
    languageLabel.textContent = language.toUpperCase();
    
    // Create copy button
    const copyBtn = document.createElement('button');
    copyBtn.className = 'code-copy-btn';
    copyBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
        نسخ الكود
    `;
    
    // Add click event to copy button
    copyBtn.addEventListener('click', () => {
        copyCodeToClipboard(codeBlock.textContent, copyBtn);
    });
    
    // Build header
    header.appendChild(languageLabel);
    header.appendChild(copyBtn);
    
    // Wrap the pre element
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(header);
    wrapper.appendChild(pre);
}

function detectCodeLanguage(codeBlock) {
    // Check class names for language
    const classes = Array.from(codeBlock.classList);
    for (const cls of classes) {
        if (cls.startsWith('language-')) {
            return cls.replace('language-', '');
        }
    }
    
    // Try to detect from content
    const code = codeBlock.textContent.trim();
    if (code.includes('function') && code.includes('{')) return 'javascript';
    if (code.includes('def ') && code.includes(':')) return 'python';
    if (code.includes('<?php')) return 'php';
    if (code.includes('public class')) return 'java';
    if (code.includes('#include')) return 'c';
    if (code.includes('body {') || code.includes('color:')) return 'css';
    if (code.includes('<html') || code.includes('<div')) return 'html';
    
    return 'code';
}

function copyCodeToClipboard(code, button) {
    // Clean the code (remove extra whitespace)
    const cleanCode = code.trim();
    
    navigator.clipboard.writeText(cleanCode).then(() => {
        // Show success feedback
        const originalHTML = button.innerHTML;
        button.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <polyline points="20,6 9,17 4,12" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            تم النسخ!
        `;
        button.classList.add('copied');
        
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.classList.remove('copied');
        }, 2000);
        
    }).catch(err => {
        console.error('Failed to copy: ', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = cleanCode;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        button.innerHTML = '✅ تم النسخ!';
        setTimeout(() => {
            button.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke="currentColor" stroke-width="2" fill="none"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" stroke-width="2" fill="none"/>
                </svg>
                نسخ الكود
            `;
        }, 2000);
    });
}

function enhanceMarkdownElements(element) {
    // Add icons to headers
    const headers = element.querySelectorAll('h1, h2, h3, h4, h5, h6');
    headers.forEach(header => {
        if (!header.querySelector('.header-icon')) {
            const icon = document.createElement('span');
            icon.className = 'header-icon';
            icon.textContent = '📝';
            header.insertBefore(icon, header.firstChild);
        }
    });
    
    // Style code snippets (inline code)
    const inlineCode = element.querySelectorAll('code:not(pre code)');
    inlineCode.forEach(code => {
        code.classList.add('inline-code');
    });
    
    // Style blockquotes
    const blockquotes = element.querySelectorAll('blockquote');
    blockquotes.forEach(quote => {
        quote.classList.add('enhanced-blockquote');
    });
}

// Auto-enhance when new messages arrive
function autoEnhanceNewMessages() {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.classList.contains('message')) {
                        setTimeout(() => {
                            enhanceMarkdownDisplay();
                        }, 100);
                    }
                });
            }
        });
    });
    
    const messagesContainer = document.querySelector('.messages');
    if (messagesContainer) {
        observer.observe(messagesContainer, {
            childList: true,
            subtree: true
        });
    }
} 