# 🔧 دليل إعداد خدمة AI Chatbot

## المحتويات
- [متطلبات النظام](#متطلبات-النظام)
- [طرق التثبيت](#طرق-التثبيت)
- [إعداد NSSM Service](#إعداد-nssm-service)
- [إعداد Task Scheduler](#إعداد-task-scheduler)
- [إعداد الشبكة](#إعداد-الشبكة)
- [استكشاف الأخطاء](#استكشاف-الأخطاء)

## متطلبات النظام

### الأساسية
- Windows 10/11 أو Windows Server 2016+
- Python 3.8+
- صلاحيات Administrator (للمنفذ 80)
- 2GB RAM كحد أدنى
- 1GB مساحة قرص صلب

### الاختيارية
- Virtual Environment (موصى به)
- NSSM (Non-Sucking Service Manager)
- جدار حماية Windows مفعل

## طرق التثبيت

### 1. NSSM Service (الأفضل للخوادم)

**المزايا:**
- ✅ يعمل كخدمة Windows حقيقية
- ✅ إدارة متقدمة للسجلات
- ✅ إعادة تشغيل تلقائي عند الفشل
- ✅ تحكم كامل في متغيرات البيئة

**العيوب:**
- ❌ يتطلب تحميل NSSM
- ❌ أكثر تعقيداً في الإعداد

### 2. Task Scheduler (الأفضل للاستخدام الشخصي)

**المزايا:**
- ✅ مدمج في Windows
- ✅ سهل الإعداد
- ✅ لا يتطلب برامج إضافية

**العيوب:**
- ❌ إدارة أقل للسجلات
- ❌ أقل مرونة في التحكم

## إعداد NSSM Service

### الخطوة 1: تحميل NSSM
```bash
# اذهب إلى: https://nssm.cc/download
# حمل nssm.exe وضعه في مجلد المشروع
```

### الخطوة 2: التثبيت
```batch
# انقر بالزر الأيمن واختر "Run as administrator"
install_service.bat
```

### الخطوة 3: التحقق من التثبيت
```batch
# فحص حالة الخدمة
sc query AIChatbotService

# أو استخدم أداة الإدارة
service_manager.bat
```

### إعدادات NSSM المتقدمة

```batch
# عرض جميع إعدادات الخدمة
nssm dump AIChatbotService

# تغيير وقت التأخير لإعادة التشغيل
nssm set AIChatbotService AppThrottle 1500

# تغيير مستوى السجلات
nssm set AIChatbotService AppStdoutCreationDisposition 4
```

## إعداد Task Scheduler

### الخطوة 1: إنشاء المهمة
```batch
# انقر بالزر الأيمن واختر "Run as administrator"
create_task_scheduler.bat
```

### الخطوة 2: التحقق من المهمة
```batch
# فتح Task Scheduler
taskschd.msc

# البحث عن: "AI Chatbot Service"
```

### إعدادات Task Scheduler المتقدمة

```batch
# تشغيل المهمة يدوياً
schtasks /run /tn "AI Chatbot Service"

# حذف المهمة
schtasks /delete /tn "AI Chatbot Service" /f

# عرض معلومات المهمة
schtasks /query /tn "AI Chatbot Service" /v
```

## إعداد الشبكة

### إعداد جدار الحماية (مطلوب)

```batch
# تشغيل كـ Administrator
setup_firewall.bat
```

**أو يدوياً:**
```batch
# إضافة قاعدة للمنفذ 80
netsh advfirewall firewall add rule name="AI Chatbot" dir=in action=allow protocol=TCP localport=80
```

### اختبار الوصول من الشبكة

```batch
# تشغيل اختبار الشبكة
network_test.bat
```

### الحصول على عنوان IP

```batch
# عرض عناوين IP
ipconfig | findstr "IPv4"

# أو
ipconfig /all
```

## استكشاف الأخطاء

### 1. الخدمة لا تبدأ

**الأعراض:**
- الخدمة تفشل في البدء
- رسائل خطأ في Event Viewer

**الحلول:**
```batch
# فحص السجلات
type logs\service_error.log

# فحص صلاحيات Python
where python

# تشغيل يدوي للاختبار
python run.py
```

### 2. المنفذ 80 مستخدم

**الأعراض:**
- خطأ "Address already in use"
- التطبيق لا يمكن الوصول إليه

**الحلول:**
```batch
# فحص ما يستخدم المنفذ 80
netstat -ano | findstr :80

# إيقاف الخدمة المتداخلة (مثل IIS)
net stop w3svc

# أو تغيير المنفذ في config.py
```

### 3. مشاكل الصلاحيات

**الأعراض:**
- "Access Denied" errors
- فشل في إنشاء ملفات السجلات

**الحلول:**
```batch
# تشغيل كـ Administrator
# تحقق من صلاحيات مجلد المشروع
icacls . /grant Users:F

# إعطاء صلاحيات للخدمة
sc config AIChatbotService obj= "LocalSystem"
```

### 4. مشاكل الشبكة

**الأعراض:**
- لا يمكن الوصول من أجهزة أخرى
- Connection refused

**الحلول:**
```batch
# فحص جدار الحماية
netsh advfirewall firewall show rule name="AI Chatbot"

# فحص إعدادات الشبكة
ipconfig /all

# اختبار الاتصال
telnet localhost 80
```

## 🔧 أوامر الإدارة المفيدة

### إدارة الخدمة
```batch
# بدء الخدمة
net start AIChatbotService

# إيقاف الخدمة
net stop AIChatbotService

# إعادة تشغيل الخدمة
net stop AIChatbotService && net start AIChatbotService

# حالة الخدمة
sc query AIChatbotService
```

### مراقبة الأداء
```batch
# مراقبة استخدام الذاكرة
tasklist | findstr python

# مراقبة الاتصالات
netstat -an | findstr :80

# مراقبة السجلات في الوقت الفعلي
powershell Get-Content logs\service_output.log -Wait
```

## 📊 معلومات الخدمة

| المعلومة | القيمة |
|----------|---------|
| اسم الخدمة | AIChatbotService |
| المنفذ | 80 (HTTP الافتراضي) |
| المجلد | مجلد المشروع الحالي |
| السجلات | `logs/service_*.log` |
| البيانات | `data/` |
| العنوان المحلي | http://localhost |
| عنوان الشبكة | http://[IP] |

## 🔐 ملاحظات الأمان

### للوصول المحلي فقط:
- استخدم `127.0.0.1` بدلاً من `0.0.0.0`
- أغلق المنفذ في جدار الحماية

### للوصول من الشبكة:
- تأكد من أمان الشبكة المحلية
- استخدم كلمات مرور قوية
- راقب السجلات بانتظام

### للوصول من الإنترنت:
⚠️ **تحذير**: اقرأ `SECURITY_WARNING.md` أولاً!

## 📞 الدعم الفني

إذا واجهت مشاكل:

1. **فحص السجلات**: `logs/service_error.log`
2. **تشغيل الاختبارات**: `test_service.bat`
3. **استخدام أداة الإدارة**: `service_manager.bat`
4. **إعادة التثبيت**: `uninstall_service.bat` ثم `install_service.bat`

---

**💡 نصيحة**: احتفظ بنسخة احتياطية من إعداداتك قبل إجراء تغييرات كبيرة!