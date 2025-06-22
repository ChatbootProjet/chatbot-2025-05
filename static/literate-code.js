/**
 * Literate Programming Code Display System
 * نظام عرض الكود بنمط البرمجة الأدبية
 */

class LiterateCodeRenderer {
    constructor() {
        this.initializeRenderer();
    }

    /**
     * Initialize the code renderer
     * تهيئة معرض الكود
     */
    initializeRenderer() {
        this.setupCodeBlockHandlers();
        this.setupSyntaxHighlighting();
    }

    /**
     * Create a literate programming code block
     * إنشاء كتلة كود بنمط البرمجة الأدبية
     */
    createLiterateCodeBlock(config) {
        const {
            title = "Code Example",
            language = "javascript",
            code = "",
            explanation = "",
            steps = [],
            output = "",
            fileName = "example.js"
        } = config;

        const container = document.createElement('div');
        container.className = 'literate-code-container';
        
        // Count lines for display
        const lineCount = code.split('\n').length;
        
        container.innerHTML = `
            <!-- Code Section Header -->
            <div class="code-section-header">
                <h3 class="code-section-title">${title}</h3>
                <div class="code-section-meta">
                    <span class="code-language-badge">${language}</span>
                    <span class="code-lines-count">
                        📄 ${lineCount} lines
                    </span>
                </div>
            </div>

            <!-- Code Explanation -->
            ${explanation ? `
            <div class="code-explanation">
                <h4>💡 شرح الكود | Code Explanation</h4>
                <div class="explanation-content">
                    ${this.parseMarkdown(explanation)}
                </div>
            </div>
            ` : ''}

            <!-- Enhanced Code Block -->
            <div class="enhanced-code-block">
                <div class="code-toolbar">
                    <div class="code-toolbar-left">
                        <span class="code-file-name">📁 ${fileName}</span>
                    </div>
                    <div class="code-toolbar-right">
                        <button class="code-action-btn copy-btn" data-code="${this.escapeHtml(code)}">
                            📋 Copy
                        </button>
                        <button class="code-action-btn run-btn" data-language="${language}">
                            ▶️ Run
                        </button>
                        <button class="code-action-btn expand-btn">
                            🔍 Expand
                        </button>
                    </div>
                </div>
                <div class="code-content">
                    <div class="line-numbers">
                        ${this.generateLineNumbers(lineCount)}
                    </div>
                    <div class="code-lines">
                        <pre><code class="language-${language}">${this.highlightSyntax(code, language)}</code></pre>
                    </div>
                </div>
            </div>

            <!-- Code Steps -->
            ${steps.length > 0 ? `
            <div class="code-steps">
                <h4>🔢 خطوات التنفيذ | Implementation Steps</h4>
                ${steps.map((step, index) => `
                    <div class="step-item">
                        <div class="step-number">${index + 1}</div>
                        <div class="step-content">
                            <div class="step-title">${step.title}</div>
                            <div class="step-description">${step.description}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
            ` : ''}

            <!-- Code Output -->
            ${output ? `
            <div class="code-output">
                <h4>📤 المخرجات | Output</h4>
                <div class="output-content">${output}</div>
            </div>
            ` : ''}
        `;

        this.attachEventListeners(container);
        return container;
    }

    /**
     * Generate line numbers for code display
     * إنشاء أرقام الأسطر لعرض الكود
     */
    generateLineNumbers(lineCount) {
        const numbers = [];
        for (let i = 1; i <= lineCount; i++) {
            numbers.push(`<div class="line-number">${i}</div>`);
        }
        return numbers.join('');
    }

    /**
     * Highlight syntax for different programming languages
     * تلوين الكود حسب لغة البرمجة
     */
    highlightSyntax(code, language) {
        // Basic syntax highlighting patterns
        const patterns = {
            javascript: {
                keyword: /\b(function|const|let|var|if|else|for|while|return|class|import|export|async|await)\b/g,
                string: /(["'`])((?:\\.|(?!\1)[^\\\r\n])*?)\1/g,
                comment: /(\/\/.*$|\/\*[\s\S]*?\*\/)/gm,
                number: /\b\d+\.?\d*\b/g,
                function: /\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?=\()/g
            },
            python: {
                keyword: /\b(def|class|if|elif|else|for|while|return|import|from|as|try|except|finally|with|lambda|yield)\b/g,
                string: /(["'])((?:\\.|(?!\1)[^\\\r\n])*?)\1/g,
                comment: /(#.*$)/gm,
                number: /\b\d+\.?\d*\b/g,
                decorator: /@[a-zA-Z_][a-zA-Z0-9_]*/g
            },
            css: {
                selector: /[a-zA-Z0-9_.-]+(?=\s*\{)/g,
                property: /[a-zA-Z-]+(?=\s*:)/g,
                string: /(["'])((?:\\.|(?!\1)[^\\\r\n])*?)\1/g,
                comment: /(\/\*[\s\S]*?\*\/)/g,
                important: /!important/g
            }
        };

        let highlightedCode = this.escapeHtml(code);
        const langPatterns = patterns[language] || patterns.javascript;

        // Apply syntax highlighting
        Object.entries(langPatterns).forEach(([type, pattern]) => {
            highlightedCode = highlightedCode.replace(pattern, (match) => {
                return `<span class="token ${type}">${match}</span>`;
            });
        });

        return highlightedCode;
    }

    /**
     * Parse simple markdown for explanations
     * تحليل الماركداون البسيط للشروحات
     */
    parseMarkdown(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>')
            .replace(/\n- (.*?)(?=\n|$)/g, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    }

    /**
     * Escape HTML characters
     * تشفير أحرف HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Attach event listeners to code blocks
     * ربط مستمعي الأحداث بكتل الكود
     */
    attachEventListeners(container) {
        // Copy button
        const copyBtn = container.querySelector('.copy-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', (e) => {
                const code = e.target.dataset.code;
                this.copyToClipboard(code, e.target);
            });
        }

        // Run button
        const runBtn = container.querySelector('.run-btn');
        if (runBtn) {
            runBtn.addEventListener('click', (e) => {
                const language = e.target.dataset.language;
                this.runCode(container, language);
            });
        }

        // Expand button
        const expandBtn = container.querySelector('.expand-btn');
        if (expandBtn) {
            expandBtn.addEventListener('click', () => {
                this.toggleExpanded(container);
            });
        }
    }

    /**
     * Copy code to clipboard
     * نسخ الكود إلى الحافظة
     */
    async copyToClipboard(text, button) {
        try {
            await navigator.clipboard.writeText(text);
            
            const originalText = button.innerHTML;
            button.innerHTML = '✅ Copied!';
            button.classList.add('copied');
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.classList.remove('copied');
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
            
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            button.innerHTML = '✅ Copied!';
            setTimeout(() => {
                button.innerHTML = '📋 Copy';
            }, 2000);
        }
    }

    /**
     * Run code (placeholder for future implementation)
     * تشغيل الكود (مكان لتنفيذ مستقبلي)
     */
    runCode(container, language) {
        // This would integrate with code execution services
        console.log(`Running ${language} code...`);
        
        // For now, just show a message
        const outputSection = container.querySelector('.code-output');
        if (!outputSection) {
            const newOutput = document.createElement('div');
            newOutput.className = 'code-output';
            newOutput.innerHTML = `
                <h4>📤 المخرجات | Output</h4>
                <div class="output-content">Code execution feature coming soon! 🚀</div>
            `;
            container.appendChild(newOutput);
        }
    }

    /**
     * Toggle expanded view
     * تبديل العرض الموسع
     */
    toggleExpanded(container) {
        const codeContent = container.querySelector('.code-content');
        const isExpanded = codeContent.style.maxHeight === 'none';
        
        if (isExpanded) {
            codeContent.style.maxHeight = '500px';
        } else {
            codeContent.style.maxHeight = 'none';
        }
        
        const expandBtn = container.querySelector('.expand-btn');
        expandBtn.innerHTML = isExpanded ? '🔍 Expand' : '📦 Collapse';
    }

    /**
     * Setup code block handlers for existing content
     * إعداد معالجات كتل الكود للمحتوى الموجود
     */
    setupCodeBlockHandlers() {
        // Enhance existing code blocks
        document.addEventListener('DOMContentLoaded', () => {
            this.enhanceExistingCodeBlocks();
        });

        // Watch for dynamically added content
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) { // Element node
                            this.enhanceCodeBlocksInNode(node);
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    /**
     * Enhance existing code blocks
     * تحسين كتل الكود الموجودة
     */
    enhanceExistingCodeBlocks() {
        const codeBlocks = document.querySelectorAll('pre code');
        codeBlocks.forEach(block => this.enhanceCodeBlock(block));
    }

    /**
     * Enhance code blocks in a specific node
     * تحسين كتل الكود في عقدة محددة
     */
    enhanceCodeBlocksInNode(node) {
        const codeBlocks = node.querySelectorAll ? node.querySelectorAll('pre code') : [];
        codeBlocks.forEach(block => this.enhanceCodeBlock(block));
    }

    /**
     * Enhance a single code block
     * تحسين كتلة كود واحدة
     */
    enhanceCodeBlock(codeElement) {
        if (codeElement.classList.contains('enhanced')) return;
        
        const pre = codeElement.parentElement;
        if (!pre || pre.tagName !== 'PRE') return;

        const code = codeElement.textContent;
        const language = this.detectLanguage(codeElement);
        
        // Create enhanced version
        const enhanced = this.createLiterateCodeBlock({
            title: `${language.charAt(0).toUpperCase() + language.slice(1)} Code`,
            language: language,
            code: code,
            fileName: `example.${this.getFileExtension(language)}`
        });

        // Replace original
        pre.parentNode.replaceChild(enhanced, pre);
    }

    /**
     * Detect programming language from code element
     * اكتشاف لغة البرمجة من عنصر الكود
     */
    detectLanguage(codeElement) {
        // Check class names for language hints
        const classes = Array.from(codeElement.classList);
        for (const cls of classes) {
            if (cls.startsWith('language-')) {
                return cls.replace('language-', '');
            }
        }
        
        // Try to detect from content
        const code = codeElement.textContent;
        if (code.includes('function') && code.includes('{')) return 'javascript';
        if (code.includes('def ') && code.includes(':')) return 'python';
        if (code.includes('<?php')) return 'php';
        if (code.includes('#include') || code.includes('int main')) return 'c';
        if (code.includes('public class') || code.includes('System.out')) return 'java';
        if (code.includes('body {') || code.includes('color:')) return 'css';
        if (code.includes('<html') || code.includes('<div')) return 'html';
        
        return 'text';
    }

    /**
     * Get file extension for language
     * الحصول على امتداد الملف للغة
     */
    getFileExtension(language) {
        const extensions = {
            javascript: 'js',
            python: 'py',
            java: 'java',
            cpp: 'cpp',
            c: 'c',
            php: 'php',
            css: 'css',
            html: 'html',
            sql: 'sql',
            json: 'json',
            xml: 'xml',
            yaml: 'yml',
            bash: 'sh'
        };
        return extensions[language] || 'txt';
    }

    /**
     * Setup syntax highlighting
     * إعداد تلوين الكود
     */
    setupSyntaxHighlighting() {
        // This method can be extended to integrate with libraries like Prism.js or highlight.js
        console.log('Syntax highlighting system initialized');
    }
}

// Initialize the literate code renderer
const literateCodeRenderer = new LiterateCodeRenderer();

// Make it globally available
window.LiterateCodeRenderer = LiterateCodeRenderer;
window.literateCodeRenderer = literateCodeRenderer;
