# AI Chatbot - روبوت المحادثة الذكي

## English Description

A smart AI chatbot built with Python (Flask) for the backend and HTML/CSS/JavaScript for the frontend. This chatbot operates locally without requiring any external APIs and features self-learning capabilities.

### Features:
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

روبوت محادثة ذكي مبني باستخدام Python (Flask) للخلفية و HTML/CSS/JavaScript للواجهة الأمامية. يعمل روبوت المحادثة هذا محلياً دون الحاجة إلى أي واجهات برمجة تطبيقات خارجية ويتميز بقدرات التعلم الذاتي.

### الميزات:
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

Click the statistics button in the top-right corner of the chat interface to view:
- Total number of learned responses
- Number of conversation sessions
- Most popular topics discussed

انقر على زر الإحصائيات في الزاوية العلوية اليمنى من واجهة المحادثة لعرض:
- العدد الإجمالي للردود المتعلمة
- عدد جلسات المحادثة
- أكثر المواضيع شيوعًا في المناقشة

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

## How to Customize - كيفية التخصيص

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

## Recent UI/UX Enhancements - تحسينات واجهة المستخدم الحديثة

### Enhanced Interface - واجهة محسنة

We've recently implemented several UI/UX improvements to make the chatbot more modern, responsive, and user-friendly:

لقد قمنا مؤخرًا بتنفيذ العديد من التحسينات على واجهة المستخدم لجعل روبوت المحادثة أكثر حداثة واستجابة وسهولة في الاستخدام:

#### Scrolling and Message Display - التمرير وعرض الرسائل
- Enhanced auto-scrolling functionality to follow new messages
- Improved message spacing and formatting
- Better RTL (Right-to-Left) support for Arabic text
- Fixed message overflow problems
- Optimized message container for long conversations

- تحسين وظيفة التمرير التلقائي لمتابعة الرسائل الجديدة
- تحسين تباعد وتنسيق الرسائل
- دعم أفضل للكتابة من اليمين إلى اليسار للنص العربي
- إصلاح مشكلات تجاوز حدود الرسائل
- تحسين حاوية الرسائل للمحادثات الطويلة

#### Modern Design Elements - عناصر تصميم حديثة
- Modern color gradients for a more appealing look
- Improved animations and transitions between states
- Enhanced message bubbles with shadows and depth
- Better responsive design for various screen sizes
- Ripple effects on buttons for improved interactivity

- تدرجات ألوان حديثة لمظهر أكثر جاذبية
- تحسين الرسوم المتحركة والانتقالات بين الحالات
- تعزيز فقاعات الرسائل بالظلال والعمق
- تصميم متجاوب أفضل لمختلف أحجام الشاشات
- تأثيرات تموج على الأزرار لتحسين التفاعلية

#### Dark Mode & Theming - الوضع الداكن والسمات
- Complete dark mode system with toggle button
- CSS variables for comprehensive theme management
- User preference saving in localStorage
- Keyboard shortcuts for mode switching (Alt+D)
- Animated sun/moon icons for the theme toggle
- Improved color contrast in both light and dark modes

- نظام وضع داكن كامل مع زر تبديل
- متغيرات CSS لإدارة شاملة للسمات
- حفظ تفضيلات المستخدم في التخزين المحلي
- اختصارات لوحة المفاتيح لتبديل الوضع (Alt+D)
- أيقونات شمس/قمر متحركة لتبديل السمة
- تحسين تباين الألوان في كل من الوضعين الفاتح والداكن

These enhancements create a more modern, bilingual chatbot interface with smooth animations, proper text handling for both languages, and a complete theming system that adapts to user preferences.

تخلق هذه التحسينات واجهة روبوت محادثة ثنائية اللغة أكثر حداثة مع رسوم متحركة سلسة، ومعالجة نصوص مناسبة لكلتا اللغتين، ونظام سمات كامل يتكيف مع تفضيلات المستخدم. 