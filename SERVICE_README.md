# 🤖 AI Chatbot Windows Service

تم إنشاء مجموعة شاملة من الأدوات لتشغيل AI Chatbot كخدمة Windows تلقائياً.

## 📋 الملفات المتوفرة

### ⚙️ ملفات الإعداد الأساسية
- `start_service.bat` - تشغيل التطبيق مباشرة
- `test_service.bat` - اختبار النظام قبل التثبيت
- `service_manager.bat` - أداة الإدارة الشاملة 🎛️
- `setup_firewall.bat` - إعداد جدار الحماية للوصول الخارجي 🔥
- `network_test.bat` - اختبار الوصول من الشبكة 🌐

### 🔧 ملفات NSSM Service
- `install_service.bat` - تثبيت خدمة Windows
- `uninstall_service.bat` - إلغاء تثبيت الخدمة

### 📅 ملفات Task Scheduler
- `create_task_scheduler.bat` - إنشاء مهمة مجدولة
- `remove_task_scheduler.bat` - إزالة المهمة المجدولة

### 📚 ملفات الدليل والإعدادات
- `QUICK_START.md` - دليل البدء السريع
- `SERVICE_SETUP_GUIDE.md` - دليل الإعداد المفصل
- `production_config.py` - إعدادات الإنتاج

## 🚀 البدء السريع

### الطريقة الأولى: NSSM (موصى بها للخوادم)

1. **تحميل NSSM**
   - اذهب إلى: https://nssm.cc/download
   - حمل `nssm.exe` وضعه في مجلد المشروع

2. **اختبار النظام**
   ```batch
   test_service.bat
   ```

3. **تثبيت الخدمة**
   ```batch
   # تشغيل كمدير (Run as Administrator)
   install_service.bat
   ```

4. **الوصول للتطبيق**
   ```
   http://localhost:5000
   ```

### الطريقة الثانية: Task Scheduler (للاستخدام الشخصي)

1. **إنشاء مهمة مجدولة**
   ```batch
   # تشغيل كمدير (Run as Administrator)
   create_task_scheduler.bat
   ```

2. **إعادة تشغيل الكمبيوتر**
   ```
   سيبدأ التطبيق تلقائياً
   ```

## 🎛️ إدارة الخدمة

### استخدام أداة الإدارة الشاملة
```batch
service_manager.bat
```

هذه الأداة تتيح لك:
- ✅ تثبيت/إلغاء تثبيت الخدمة
- ▶️ تشغيل/إيقاف/إعادة تشغيل الخدمة
- 📊 فحص حالة الخدمة
- 📋 عرض السجلات
- 📅 إدارة Task Scheduler
- 🔥 إعداد جدار الحماية
- 🌐 اختبار الوصول من الشبكة

### الأوامر المباشرة
```batch
net start AIChatbotService      # تشغيل الخدمة
net stop AIChatbotService       # إيقاف الخدمة
sc query AIChatbotService       # فحص الحالة
```

## 📊 معلومات الخدمة

| المعلومة | القيمة |
|----------|---------|
| اسم الخدمة | AIChatbotService |
| المنفذ | 5000 |
| العنوان المحلي | http://localhost:5000 |
| عنوان الشبكة | http://[IP]:5000 |
| مجلد السجلات | `logs/` |
| مجلد البيانات | `data/` |

## 🔧 استكشاف الأخطاء

### المشاكل الشائعة

1. **الخدمة لا تبدأ**
   ```batch
   # فحص السجلات
   type logs\service_error.log
   
   # فحص المتطلبات
   pip install -r requirements.txt
   ```

2. **المنفذ مستخدم**
   ```batch
   # فحص المنفذ
   netstat -an | findstr :5000
   
   # تغيير المنفذ في config.py
   ```

3. **مشاكل الصلاحيات**
   - تأكد من تشغيل الأوامر كـ Administrator
   - تأكد من صلاحيات الكتابة في المجلد

## 🛡️ الأمان والإنتاج

### إعدادات الإنتاج
- استخدم `production_config.py` للإنتاج
- غير `DEBUG = False` في `config.py`
- استخدم مفتاح سري قوي
- قم بتحديث API keys بانتظام

### جدار الحماية
```batch
# إضافة استثناء للمنفذ 5000
netsh advfirewall firewall add rule name="AI Chatbot" dir=in action=allow protocol=TCP localport=5000
```

## 📁 هيكل الملفات

```
chatbot-2025-05/
├── 🎛️ service_manager.bat          # أداة الإدارة الشاملة
├── ⚙️ install_service.bat          # تثبيت NSSM
├── 🗑️ uninstall_service.bat        # إلغاء تثبيت NSSM
├── 📅 create_task_scheduler.bat    # إنشاء مهمة مجدولة
├── 🗑️ remove_task_scheduler.bat    # إزالة مهمة مجدولة
├── ▶️ start_service.bat            # تشغيل مباشر
├── 🧪 test_service.bat             # اختبار النظام
├── 📚 QUICK_START.md               # دليل البدء السريع
├── 📖 SERVICE_SETUP_GUIDE.md       # دليل الإعداد المفصل
├── ⚙️ production_config.py         # إعدادات الإنتاج
└── 📄 SERVICE_README.md            # هذا الملف
```

## 📞 الدعم

في حالة مواجهة مشاكل:

1. **اختبر النظام أولاً**
   ```batch
   test_service.bat
   ```

2. **فحص السجلات**
   ```batch
   type logs\service_output.log
   type logs\service_error.log
   ```

3. **استخدم أداة الإدارة**
   ```batch
   service_manager.bat
   ```

## 🔄 التحديث

### تحديث التطبيق
1. أوقف الخدمة: `net stop AIChatbotService`
2. حدث الملفات
3. شغل الخدمة: `net start AIChatbotService`

### تحديث المتطلبات
```batch
pip install -r requirements.txt --upgrade
```

---

**🎉 مبروك! تطبيق AI Chatbot جاهز للعمل كخدمة Windows تلقائية!**

**💡 نصيحة**: ابدأ بـ `test_service.bat` ثم استخدم `service_manager.bat` لإدارة كل شيء!