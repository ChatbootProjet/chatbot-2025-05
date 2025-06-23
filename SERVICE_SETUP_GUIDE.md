# دليل إعداد خدمة AI Chatbot على Windows

هذا الدليل يوضح كيفية تشغيل تطبيق AI Chatbot تلقائياً على Windows باستخدام طريقتين مختلفتين.

## الطريقة الأولى: استخدام NSSM (Non-Sucking Service Manager)

### 1. تحميل NSSM
- اذهب إلى: https://nssm.cc/download
- حمل الإصدار المناسب لنظامك (32-bit أو 64-bit)
- استخرج ملف `nssm.exe` وضعه في مجلد المشروع

### 2. تثبيت الخدمة
```batch
# تشغيل كمدير (Run as Administrator)
install_service.bat
```

### 3. إدارة الخدمة
```batch
# استخدام أداة الإدارة الشاملة
service_manager.bat

# أو استخدام الأوامر المباشرة
net start AIChatbotService      # تشغيل الخدمة
net stop AIChatbotService       # إيقاف الخدمة
net restart AIChatbotService    # إعادة تشغيل الخدمة
```

### 4. إلغاء تثبيت الخدمة
```batch
# تشغيل كمدير (Run as Administrator)
uninstall_service.bat
```

## الطريقة الثانية: استخدام Task Scheduler

### 1. إنشاء مهمة مجدولة
```batch
# تشغيل كمدير (Run as Administrator)
create_task_scheduler.bat
```

### 2. إزالة المهمة المجدولة
```batch
# تشغيل كمدير (Run as Administrator)
remove_task_scheduler.bat
```

## الملفات المتاحة

| الملف | الوصف |
|-------|--------|
| `start_service.bat` | تشغيل التطبيق مباشرة |
| `install_service.bat` | تثبيت خدمة Windows باستخدام NSSM |
| `uninstall_service.bat` | إلغاء تثبيت الخدمة |
| `create_task_scheduler.bat` | إنشاء مهمة Task Scheduler |
| `remove_task_scheduler.bat` | إزالة مهمة Task Scheduler |
| `service_manager.bat` | أداة إدارة شاملة للخدمة |

## إعدادات الخدمة

### المعلومات الأساسية
- **اسم الخدمة**: AIChatbotService
- **المنفذ الافتراضي**: 5000
- **العنوان**: http://localhost:5000

### ملفات السجلات
- **مجلد السجلات**: `logs/`
- **سجل الإخراج**: `logs/service_output.log`
- **سجل الأخطاء**: `logs/service_error.log`

## استكشاف الأخطاء

### 1. فحص حالة الخدمة
```batch
sc query AIChatbotService
```

### 2. عرض السجلات
```batch
type logs\service_output.log
type logs\service_error.log
```

### 3. فحص المنفذ
```batch
netstat -an | findstr :5000
```

### 4. المشاكل الشائعة

#### الخدمة لا تبدأ
- تأكد من وجود Python مثبت
- تأكد من تثبيت المتطلبات: `pip install -r requirements.txt`
- فحص ملفات السجلات للأخطاء

#### المنفذ مستخدم
- غير المنفذ في `config.py`
- أو أوقف التطبيق الذي يستخدم المنفذ 5000

#### مشاكل الصلاحيات
- تأكد من تشغيل الأوامر كمدير (Administrator)
- تأكد من صلاحيات الكتابة في مجلد المشروع

## الأمان

### إعدادات الإنتاج
- غير `DEBUG = False` في `config.py`
- استخدم مفتاح سري قوي في `app.secret_key`
- قم بتحديث API keys بانتظام

### جدار الحماية
- أضف استثناء للمنفذ 5000 في Windows Firewall
- أو استخدم منفذ مختلف حسب احتياجاتك

## النسخ الاحتياطي

### الملفات المهمة للنسخ الاحتياطي
- `data/` - بيانات المحادثات والتعلم
- `config.py` - الإعدادات
- `firebase-service-account.json` - مفاتيح Firebase
- `uploads/` - الملفات المرفوعة

## التحديث

### تحديث التطبيق
1. أوقف الخدمة: `net stop AIChatbotService`
2. حدث الملفات
3. شغل الخدمة: `net start AIChatbotService`

### تحديث المتطلبات
```batch
pip install -r requirements.txt --upgrade
```

## الدعم

في حالة مواجهة مشاكل:
1. فحص ملفات السجلات
2. تأكد من تشغيل الأوامر كمدير
3. تأكد من تثبيت جميع المتطلبات
4. فحص إعدادات جدار الحماية

---

**ملاحظة**: يُنصح باستخدام NSSM للخوادم الإنتاجية، و Task Scheduler للاستخدام الشخصي.