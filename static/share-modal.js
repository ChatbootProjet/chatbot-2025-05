/**
 * Share Modal JavaScript
 * Handles sharing functionality for conversations
 */

// Initialize share modal when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeShareModal();
});

function initializeShareModal() {
    // Check if share modal exists
    const shareModal = document.getElementById('share-modal');
    if (!shareModal) {
        // Silently skip if modal doesn't exist - this is normal for some pages
        console.log('ℹ️ Share modal not available on this page');
        return;
    }

    // Add share button event listeners only if they exist
    const shareButtons = document.querySelectorAll('.share-btn');
    shareButtons.forEach(button => {
        if (button && typeof button.addEventListener === 'function') {
            button.addEventListener('click', function() {
                const conversationId = this.dataset.conversationId;
                openShareModal(conversationId);
            });
        }
    });

    // Add close modal functionality only if element exists
    const closeButton = shareModal.querySelector('.close-modal');
    if (closeButton && typeof closeButton.addEventListener === 'function') {
        closeButton.addEventListener('click', function() {
            closeShareModal();
        });
    }

    // Close modal when clicking outside - only if modal exists
    if (shareModal && typeof shareModal.addEventListener === 'function') {
        shareModal.addEventListener('click', function(e) {
            if (e.target === shareModal) {
                closeShareModal();
            }
        });
    }
}

function openShareModal(conversationId) {
    const shareModal = document.getElementById('share-modal');
    if (shareModal) {
        shareModal.style.display = 'flex';
        generateShareLink(conversationId);
    } else {
        console.log('⚠️ Share modal not available');
    }
}

function closeShareModal() {
    const shareModal = document.getElementById('share-modal');
    if (shareModal) {
        shareModal.style.display = 'none';
    }
}

function generateShareLink(conversationId) {
    // Generate a shareable link for the conversation
    const baseUrl = window.location.origin;
    const shareUrl = `${baseUrl}/conversation/${conversationId}`;
    
    // Update share link input if it exists
    const shareLinkInput = document.getElementById('share-link');
    if (shareLinkInput) {
        shareLinkInput.value = shareUrl;
    }
    
    return shareUrl;
}

function copyShareLink() {
    const shareLinkInput = document.getElementById('share-link');
    if (shareLinkInput) {
        shareLinkInput.select();
        
        // Try modern clipboard API first, then fallback to execCommand
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(shareLinkInput.value).then(function() {
                showNotificationSafe('تم نسخ الرابط | Link copied!', 'success');
            }).catch(function(err) {
                console.error('Clipboard API failed:', err);
                fallbackCopy(shareLinkInput);
            });
        } else {
            fallbackCopy(shareLinkInput);
        }
    }
}

function fallbackCopy(element) {
    try {
        element.select();
        document.execCommand('copy');
        showNotificationSafe('تم نسخ الرابط | Link copied!', 'success');
    } catch (err) {
        console.error('Copy failed:', err);
        showNotificationSafe('فشل في النسخ | Copy failed', 'error');
    }
}

// Safe notification function that checks if notification system exists
function showNotificationSafe(message, type) {
    if (typeof showNotification === 'function') {
        showNotification(message, type);
    } else {
        // Fallback to simple alert if notification system not available
        alert(message);
    }
}

// Export functions for use in other scripts
window.shareModal = {
    open: openShareModal,
    close: closeShareModal,
    copyLink: copyShareLink
}; 