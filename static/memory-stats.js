/**
 * Enhanced Memory Statistics Display
 * عرض إحصائيات الذاكرة المحسنة
 */

// Initialize memory stats display
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('memory-stats') || document.getElementById('memory-stats-container')) {
        initializeMemoryStats();
    }
});

async function initializeMemoryStats() {
    try {
        const response = await fetch('/enhanced_memory_stats');
        const stats = await response.json();
        
        displayMemoryStats(stats);
        
    } catch (error) {
        console.error('Error loading memory stats:', error);
        showMemoryStatsError();
    }
}

function displayMemoryStats(stats) {
    const container = document.getElementById('memory-stats-container') || createMemoryStatsContainer();
    
    container.innerHTML = `
        <div class="memory-stats-dashboard">
            <h2>🧠 نظام الذاكرة المحسن | Enhanced Memory System</h2>
            
            <!-- User Profile Section -->
            <div class="stats-section user-profile-section">
                <h3>👤 ملف المستخدم | User Profile</h3>
                <div class="profile-stats">
                    <div class="stat-item">
                        <span class="stat-label">المستخدم | User ID:</span>
                        <span class="stat-value">${stats.current_user_profile.user_id}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">اللغة المفضلة | Language:</span>
                        <span class="stat-value">${stats.current_user_profile.language_preference}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">أسلوب المحادثة | Style:</span>
                        <span class="stat-value">${stats.current_user_profile.conversation_style}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">المواضيع المتكررة | Topics:</span>
                        <span class="stat-value">${stats.current_user_profile.frequently_discussed_topics.join(', ') || 'لا توجد | None'}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">السياق المحفوظ | Saved Context:</span>
                        <span class="stat-value">${stats.current_user_profile.relevant_context_count} entries</span>
                    </div>
                </div>
            </div>
            
            <!-- Global Stats Section -->
            <div class="stats-section global-stats-section">
                <h3>📊 الإحصائيات العامة | Global Statistics</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${stats.global_stats.total_users}</div>
                        <div class="stat-desc">إجمالي المستخدمين<br>Total Users</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.global_stats.total_conversations}</div>
                        <div class="stat-desc">إجمالي المحادثات<br>Total Conversations</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.global_stats.learned_responses}</div>
                        <div class="stat-desc">الردود المتعلمة<br>Learned Responses</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.global_stats.contextual_patterns}</div>
                        <div class="stat-desc">الأنماط السياقية<br>Contextual Patterns</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.global_stats.semantic_clusters}</div>
                        <div class="stat-desc">المجموعات الدلالية<br>Semantic Clusters</div>
                    </div>
                </div>
            </div>
            
            <!-- Memory Features Section -->
            <div class="stats-section features-section">
                <h3>⚙️ ميزات الذاكرة | Memory Features</h3>
                <div class="features-list">
                    <div class="feature-item ${stats.memory_features.long_term_memory ? 'enabled' : 'disabled'}">
                        <span class="feature-icon">${stats.memory_features.long_term_memory ? '✅' : '❌'}</span>
                        <span class="feature-name">الذاكرة طويلة الأمد | Long-term Memory</span>
                    </div>
                    <div class="feature-item ${stats.memory_features.semantic_analysis ? 'enabled' : 'disabled'}">
                        <span class="feature-icon">${stats.memory_features.semantic_analysis ? '✅' : '❌'}</span>
                        <span class="feature-name">التحليل الدلالي | Semantic Analysis</span>
                    </div>
                    <div class="feature-item enabled">
                        <span class="feature-icon">📝</span>
                        <span class="feature-name">رسائل السياق: ${stats.memory_features.context_messages}</span>
                    </div>
                    <div class="feature-item ${stats.memory_features.preserve_history ? 'enabled' : 'disabled'}">
                        <span class="feature-icon">${stats.memory_features.preserve_history ? '✅' : '❌'}</span>
                        <span class="feature-name">حفظ التاريخ | Preserve History</span>
                    </div>
                </div>
            </div>
            
            <!-- Memory Management Actions -->
            <div class="stats-section actions-section">
                <h3>🔧 إدارة الذاكرة | Memory Management</h3>
                <div class="actions-buttons">
                    <button class="action-btn" onclick="refreshMemoryStats()">
                        🔄 تحديث | Refresh
                    </button>
                    <button class="action-btn" onclick="exportMemoryData()">
                        📤 تصدير البيانات | Export Data
                    </button>
                    <button class="action-btn" onclick="clearLocalMemory()">
                        🗑️ مسح الذاكرة المحلية | Clear Local Memory
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add CSS styles
    addMemoryStatsCSS();
}

function createMemoryStatsContainer() {
    const container = document.createElement('div');
    container.id = 'memory-stats-container';
    container.className = 'memory-stats-modal';
    document.body.appendChild(container);
    return container;
}

function addMemoryStatsCSS() {
    if (document.getElementById('memory-stats-css')) return;
    
    const style = document.createElement('style');
    style.id = 'memory-stats-css';
    style.textContent = `
        .memory-stats-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            padding: 20px;
            overflow-y: auto;
        }
        
        .memory-stats-dashboard {
            background: var(--bg-color, #ffffff);
            color: var(--text-color, #333);
            border-radius: 15px;
            padding: 25px;
            max-width: 800px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .memory-stats-dashboard h2 {
            text-align: center;
            margin-bottom: 30px;
            color: var(--primary-color, #007bff);
            font-size: 1.5em;
        }
        
        .stats-section {
            margin-bottom: 25px;
            padding: 20px;
            background: var(--secondary-bg, #f8f9fa);
            border-radius: 10px;
            border: 1px solid var(--border-color, #e0e0e0);
        }
        
        .stats-section h3 {
            margin-bottom: 15px;
            color: var(--primary-color, #007bff);
            font-size: 1.2em;
        }
        
        .profile-stats .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color, #e0e0e0);
        }
        
        .stat-label {
            font-weight: bold;
            color: var(--text-secondary, #666);
        }
        
        .stat-value {
            color: var(--text-color, #333);
            font-family: monospace;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, var(--primary-color, #007bff), var(--secondary-color, #6c757d));
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .stat-desc {
            font-size: 0.9em;
            opacity: 0.9;
            line-height: 1.2;
        }
        
        .features-list {
            display: grid;
            gap: 10px;
        }
        
        .feature-item {
            display: flex;
            align-items: center;
            padding: 12px;
            background: var(--bg-color, #ffffff);
            border-radius: 8px;
            border: 1px solid var(--border-color, #e0e0e0);
        }
        
        .feature-item.enabled {
            border-color: var(--success-color, #28a745);
            background: var(--success-bg, #d4edda);
        }
        
        .feature-item.disabled {
            border-color: var(--danger-color, #dc3545);
            background: var(--danger-bg, #f8d7da);
        }
        
        .feature-icon {
            margin-right: 10px;
            font-size: 1.2em;
        }
        
        .actions-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        
        .action-btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            background: var(--primary-color, #007bff);
            color: white;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
        }
        
        .action-btn:hover {
            background: var(--primary-hover, #0056b3);
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .memory-stats-dashboard {
                margin: 10px;
                padding: 15px;
            }
            
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            }
            
            .actions-buttons {
                grid-template-columns: 1fr;
            }
        }
    `;
    document.head.appendChild(style);
}

// Action functions
async function refreshMemoryStats() {
    const container = document.getElementById('memory-stats-container');
    if (container) {
        container.innerHTML = '<div style="text-align: center; padding: 50px;">🔄 تحديث البيانات... | Refreshing...</div>';
        await initializeMemoryStats();
    }
}

async function exportMemoryData() {
    try {
        const response = await fetch('/enhanced_memory_stats');
        const stats = await response.json();
        
        const dataStr = JSON.stringify(stats, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `memory-stats-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        showNotification('✅ تم تصدير البيانات بنجاح | Data exported successfully', 'success');
    } catch (error) {
        showNotification('❌ فشل في تصدير البيانات | Export failed', 'error');
    }
}

function clearLocalMemory() {
    if (confirm('⚠️ هل أنت متأكد من مسح الذاكرة المحلية؟ | Are you sure you want to clear local memory?')) {
        localStorage.clear();
        sessionStorage.clear();
        showNotification('🗑️ تم مسح الذاكرة المحلية | Local memory cleared', 'info');
        refreshMemoryStats();
    }
}

function showMemoryStatsError() {
    const container = document.getElementById('memory-stats-container') || createMemoryStatsContainer();
    container.innerHTML = `
        <div class="memory-stats-dashboard">
            <h2>❌ خطأ في تحميل إحصائيات الذاكرة</h2>
            <p>حدث خطأ أثناء تحميل إحصائيات نظام الذاكرة المحسن.</p>
            <button class="action-btn" onclick="refreshMemoryStats()">🔄 إعادة المحاولة</button>
            <button class="action-btn" onclick="closeMemoryStats()">❌ إغلاق</button>
        </div>
    `;
}

function closeMemoryStats() {
    const container = document.getElementById('memory-stats-container');
    if (container) {
        container.remove();
    }
}

// Global function to show memory stats
window.showMemoryStats = function() {
    initializeMemoryStats();
};

// Add click outside to close
document.addEventListener('click', function(e) {
    const container = document.getElementById('memory-stats-container');
    if (container && e.target === container) {
        closeMemoryStats();
    }
}); 