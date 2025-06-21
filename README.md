# AI Chatbot - روبوت المحادثة الذكي

## English Description

A smart AI chatbot built with Python (Flask) for the backend and HTML/CSS/JavaScript for the frontend. This chatbot operates locally without requiring any external APIs and features self-learning capabilities with a **modern, simplified interface**.

### ✨ New Modern Interface Features:
- **Simplified Design**: Clean, modern interface with improved usability
- **Enhanced Mobile Experience**: Responsive design with mobile-first approach
- **Improved Navigation**: Streamlined sidebar with better organization
- **Modern Typography**: Better font choices and text hierarchy
- **Enhanced Animations**: Smooth transitions and micro-interactions
- **Better Accessibility**: Improved keyboard navigation and screen reader support
- **Quick Actions**: One-click starter prompts for new users
- **Character Counter**: Real-time character count with visual feedback

### Core Features:
- Bilingual support (English and Arabic) with automatic language detection
- Modern, responsive chat interface with typing indicators
- Pattern-based responses that intelligently match the user's language
- Simple NLP processing using NLTK
- Configurable settings via config.py
- Real-time responses for date and time requests
- Clean separation of concerns (HTML, CSS, JavaScript)
- **Self-learning capabilities** that allow the chatbot to improve over time
- Memory system to store and learn from conversations
- User-teaching interface to correct and improve responses
- Statistics dashboard to track learning progress

### Installation and Setup:

1. Clone this repository
2. Create a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the application:
   ```
   python app.py
   ```
   or use the run script:
   ```
   python run.py
   ```
6. Open your browser and navigate to `http://localhost:5000`

## الوصف بالعربية

روبوت محادثة ذكي مبني باستخدام Python (Flask) للخلفية و HTML/CSS/JavaScript للواجهة الأمامية. يعمل روبوت المحادثة هذا محلياً دون الحاجة إلى أي واجهات برمجة تطبيقات خارجية ويتميز بقدرات التعلم الذاتي مع **واجهة حديثة ومبسطة**.

### ✨ ميزات الواجهة الحديثة الجديدة:
- **تصميم مبسط**: واجهة نظيفة وحديثة مع تحسين قابلية الاستخدام
- **تجربة محسنة للموبايل**: تصميم متجاوب يركز على الأجهزة المحمولة أولاً
- **تنقل محسن**: شريط جانبي مبسط مع تنظيم أفضل
- **خطوط حديثة**: خيارات خطوط أفضل وتسلسل هرمي للنصوص
- **رسوم متحركة محسنة**: انتقالات سلسة وتفاعلات دقيقة
- **إمكانية وصول أفضل**: تنقل محسن بلوحة المفاتيح ودعم قارئ الشاشة
- **إجراءات سريعة**: اقتراحات بدء بنقرة واحدة للمستخدمين الجدد
- **عداد الأحرف**: عدد الأحرف في الوقت الفعلي مع تغذية راجعة بصرية

### الميزات الأساسية:
- دعم ثنائي اللغة (الإنجليزية والعربية) مع اكتشاف اللغة تلقائياً
- واجهة دردشة حديثة ومتجاوبة مع مؤشرات الكتابة
- ردود قائمة على الأنماط تتطابق بذكاء مع لغة المستخدم
- معالجة لغوية طبيعية بسيطة باستخدام NLTK
- إعدادات قابلة للتكوين عبر ملف config.py
- ردود في الوقت الفعلي لطلبات التاريخ والوقت
- فصل نظيف بين المكونات (HTML، CSS، JavaScript)
- **قدرات التعلم الذاتي** التي تسمح لروبوت المحادثة بالتحسن مع مرور الوقت
- نظام ذاكرة لتخزين المحادثات والتعلم منها
- واجهة تعليم المستخدم لتصحيح وتحسين الردود
- لوحة إحصائيات لتتبع تقدم التعلم

### التثبيت والإعداد:

1. استنسخ هذا المستودع
2. قم بإنشاء بيئة افتراضية (اختياري ولكن موصى به):
   ```
   python -m venv .venv
   ```
3. قم بتنشيط البيئة الافتراضية:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. قم بتثبيت التبعيات:
   ```
   pip install -r requirements.txt
   ```
5. قم بتشغيل التطبيق:
   ```
   python app.py
   ```
   أو استخدم سكريبت التشغيل:
   ```
   python run.py
   ```
6. افتح متصفحك وانتقل إلى `http://localhost:5000`

## 🎨 Modern Interface Design - تصميم الواجهة الحديثة

### Design Philosophy - فلسفة التصميم

The new interface follows modern design principles:
- **Minimalism**: Clean, uncluttered design that focuses on content
- **Accessibility**: WCAG compliant with proper contrast ratios and keyboard navigation
- **Responsiveness**: Mobile-first approach that works on all screen sizes
- **Performance**: Optimized CSS and JavaScript for fast loading
- **User Experience**: Intuitive navigation and clear visual hierarchy

تتبع الواجهة الجديدة مبادئ التصميم الحديثة:
- **البساطة**: تصميم نظيف وغير مزدحم يركز على المحتوى
- **إمكانية الوصول**: متوافق مع WCAG مع نسب تباين مناسبة وتنقل بلوحة المفاتيح
- **الاستجابة**: نهج يركز على الأجهزة المحمولة أولاً ويعمل على جميع أحجام الشاشات
- **الأداء**: CSS و JavaScript محسنان للتحميل السريع
- **تجربة المستخدم**: تنقل بديهي وتسلسل هرمي بصري واضح

### Key Interface Components - مكونات الواجهة الرئيسية

#### 1. Modern Sidebar - الشريط الجانبي الحديث
- Clean logo and branding
- Prominent "New Chat" button
- Conversation history (when implemented)
- Statistics and help buttons at the bottom

#### 2. Enhanced Chat Header - رأس المحادثة المحسن
- Chat title and status indicator
- Theme toggle button
- Simplified action buttons

#### 3. Improved Welcome Screen - شاشة الترحيب المحسنة
- Animated bot icon
- Bilingual welcome message
- Quick action buttons for common queries
- Feature showcase cards

#### 4. Modern Message Design - تصميم الرسائل الحديث
- Clean message bubbles with proper spacing
- Avatar icons for user and bot
- Smooth animations for new messages
- Proper RTL support for Arabic text

#### 5. Enhanced Input Area - منطقة الإدخال المحسنة
- Auto-resizing textarea
- Character counter with visual feedback
- Modern send button design
- Input hints and shortcuts

## Self-Learning Features - ميزات التعلم الذاتي

### Teaching the Chatbot - تعليم روبوت المحادثة

You can teach the chatbot new responses when it gives an incorrect or unsatisfactory answer. Simply use:

يمكنك تعليم روبوت المحادثة ردودًا جديدة عندما يقدم إجابة غير صحيحة أو غير مرضية. ببساطة استخدم:

```
Learn: The correct response should be this
```
or in Arabic:
```
تعلم: الرد الصحيح يجب أن يكون هذا
```

The chatbot will store this information and use it to respond to similar queries in the future.

سيقوم روبوت المحادثة بتخزين هذه المعلومات واستخدامها للرد على استفسارات مماثلة في المستقبل.

### Learning Statistics - إحصائيات التعلم

Click the statistics button in the sidebar to view:
- Total number of learned responses
- Number of conversation sessions
- Most popular topics discussed
- Learning progress chart

انقر على زر الإحصائيات في الشريط الجانبي لعرض:
- العدد الإجمالي للردود المتعلمة
- عدد جلسات المحادثة
- أكثر المواضيع شيوعًا في المناقشة
- مخطط تقدم التعلم

### How the Learning Works - كيف يعمل التعلم

The chatbot's self-learning system works by:
1. Storing user messages and bot responses
2. Recording corrections provided by users
3. Analyzing patterns in conversations
4. Building a dynamic knowledge base
5. Using similarity matching to improve responses over time

نظام التعلم الذاتي لروبوت المحادثة يعمل من خلال:
1. تخزين رسائل المستخدم وردود الروبوت
2. تسجيل التصحيحات المقدمة من المستخدمين
3. تحليل الأنماط في المحادثات
4. بناء قاعدة معرفية ديناميكية
5. استخدام مطابقة التشابه لتحسين الردود بمرور الوقت

## Configuration - التكوين

The chatbot can be configured by editing the `config.py` file, which includes settings for:
- Server host and port
- Debug mode
- Response delay
- Maximum message length
- Default language
- Initial greeting

يمكن تكوين روبوت المحادثة عن طريق تعديل ملف `config.py`، الذي يتضمن إعدادات لـ:
- مضيف الخادم ومنفذه
- وضع التصحيح
- تأخير الاستجابة
- الحد الأقصى لطول الرسالة
- اللغة الافتراضية
- التحية الأولية

## 🚀 Technical Improvements - التحسينات التقنية

### Frontend Architecture - هيكل الواجهة الأمامية

#### Modern CSS Features:
- CSS Custom Properties (Variables) for consistent theming
- CSS Grid and Flexbox for responsive layouts
- Modern CSS animations and transitions
- CSS-only components where possible
- Optimized for performance with minimal reflows

#### Enhanced JavaScript:
- ES6+ features for cleaner code
- Async/await for better error handling
- Modular architecture with clear separation of concerns
- Event delegation for better performance
- Optimized DOM manipulation

#### Responsive Design:
- Mobile-first approach
- Breakpoints: 480px, 768px, 1024px
- Touch-friendly interface elements
- Optimized for various screen sizes and orientations

### Accessibility Features - ميزات إمكانية الوصول

- **Keyboard Navigation**: Full keyboard support with proper focus management
- **Screen Reader Support**: Proper ARIA labels and semantic HTML
- **High Contrast**: Proper color contrast ratios for readability
- **Reduced Motion**: Respects user's motion preferences
- **Focus Indicators**: Clear visual focus indicators for all interactive elements

## How to Customize - كيفية التخصيص

### Styling Customization - تخصيص التصميم

The new interface uses CSS custom properties for easy theming:

```css
:root {
  --primary-color: #2563eb;
  --bg-color: #ffffff;
  --text-primary: #1e293b;
  /* ... other variables */
}
```

You can easily change colors, spacing, and other design elements by modifying these variables.

### Adding New Patterns and Responses - إضافة أنماط وردود جديدة

Edit the `patterns` and `responses` dictionaries in `app.py` to add more conversation patterns and responses. Make sure to include both English and Arabic responses.

قم بتعديل قواميس `patterns` و `responses` في ملف `app.py` لإضافة المزيد من أنماط المحادثة والردود. تأكد من تضمين ردود باللغتين الإنجليزية والعربية.

### Enhancing the AI - تحسين الذكاء الاصطناعي

To make the chatbot even smarter, you can:
1. Implement more advanced NLP techniques
2. Add a local ML model
3. Expand the pattern dictionary
4. Connect to external APIs for additional functionality
5. Implement more sophisticated learning algorithms
6. Add sentiment analysis to better understand user emotions
7. Implement context awareness for multi-turn conversations

لجعل روبوت المحادثة أكثر ذكاءً، يمكنك:
1. تنفيذ تقنيات معالجة اللغة الطبيعية أكثر تقدماً
2. إضافة نموذج تعلم آلي محلي
3. توسيع قاموس الأنماط
4. الاتصال بواجهات برمجة تطبيقات خارجية للحصول على وظائف إضافية
5. تنفيذ خوارزميات تعلم أكثر تطوراً
6. إضافة تحليل المشاعر لفهم عواطف المستخدم بشكل أفضل
7. تنفيذ الوعي بالسياق للمحادثات متعددة الدورات

## 📱 Mobile Experience - تجربة الأجهزة المحمولة

The new interface provides an excellent mobile experience:

- **Touch-Optimized**: All buttons and interactive elements are properly sized for touch
- **Swipe Gestures**: Natural swipe gestures for navigation
- **Mobile Keyboard**: Optimized input handling for mobile keyboards
- **Responsive Layout**: Adapts perfectly to different screen sizes
- **Performance**: Optimized for mobile performance and battery life

## 🌟 Quick Start Guide - دليل البدء السريع

### For New Users - للمستخدمين الجدد

1. **Start a Conversation**: Use one of the quick action buttons or type your message
2. **Teach the Bot**: Use "Learn: [correct answer]" to teach new responses
3. **Switch Themes**: Click the sun/moon icon to toggle between light and dark modes
4. **View Statistics**: Click the statistics button to see learning progress
5. **Get Help**: Click the help button for detailed instructions

### Keyboard Shortcuts - اختصارات لوحة المفاتيح

- `Enter`: Send message
- `Shift + Enter`: New line
- `Alt + D`: Toggle dark mode
- `Esc`: Close modals
- `↑/↓`: Navigate message history (when input is empty)

## 🔧 Development Notes - ملاحظات التطوير

### File Structure - هيكل الملفات

```
chatbot-2025-05/
├── templates/
│   └── index.html          # Modern HTML template
├── static/
│   ├── modern-style.css    # New modern CSS styles
│   ├── modern-script.js    # Enhanced JavaScript
│   ├── improved-style.css  # Legacy CSS (backup)
│   └── improved-script.js  # Legacy JS (backup)
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
└── data/                  # Learning data storage
```

### Browser Support - دعم المتصفحات

The modern interface supports:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Legacy browsers may fall back to basic functionality.

## 🤝 Contributing - المساهمة

We welcome contributions to improve the chatbot! Please feel free to:

- Report bugs or suggest features
- Submit pull requests with improvements
- Help with translations
- Improve documentation

نرحب بالمساهمات لتحسين روبوت المحادثة! لا تتردد في:

- الإبلاغ عن الأخطاء أو اقتراح ميزات
- تقديم طلبات السحب مع التحسينات
- المساعدة في الترجمات
- تحسين الوثائق

---

**Note**: This project is designed to work offline and doesn't require any external APIs or internet connection for basic functionality.

**ملاحظة**: هذا المشروع مصمم للعمل دون اتصال بالإنترنت ولا يتطلب أي واجهات برمجة تطبيقات خارجية أو اتصال بالإنترنت للوظائف الأساسية.

## Recent Improvements - التحسينات الأخيرة

### 1. Enhanced Conversation Management - تحسين إدارة المحادثات

- **Conversation History**: Fixed issues with conversation history not being saved or displayed in the sidebar
- **AI-Generated Conversation Titles**: Added automatic title generation for new conversations using Gemini AI
- **Conversation Options**: Implemented a three-dot menu for renaming and deleting conversations
- **Visual Indicators**: Added loading indicators during title generation and message processing

### 2. Improved AI Responses - تحسين ردود الذكاء الاصطناعي

- **Extended Response Length**: Removed character limits to allow for complete responses including code examples
- **Code Block Preservation**: Fixed issues with code blocks being stripped from responses
- **Increased Token Limits**: Upgraded Gemini API token limits from 5000 to 8192 for more comprehensive answers
- **Optimized Temperature Settings**: Adjusted temperature settings for more coherent responses
- **Enhanced AI Prompts**: Improved instructions for code and technical explanations

### 3. User Experience Improvements - تحسينات تجربة المستخدم

- **Increased Message Length**: Maximum message length increased from 1000 to 5000 characters
- **Better Bilingual Support**: Enhanced support for both Arabic and English languages
- **Responsive UI Enhancements**: Improved mobile and desktop user interface
- **Real-time Updates**: Added real-time feedback during AI processing

### 4. Technical Upgrades - الترقيات التقنية

- **Gemini 2.0 Integration**: Updated to use the latest Gemini 2.0 Flash model
- **Optimized API Parameters**: Fine-tuned API parameters for better performance
- **Enhanced Error Handling**: Improved error handling for API failures and edge cases
- **Memory Management**: Better conversation and learning memory management
