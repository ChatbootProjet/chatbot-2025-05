# 🤖 AI Chatbot Windows Service

## نظرة عامة شاملة

هذا المشروع يوفر نظام AI Chatbot متكامل يعمل كخدمة Windows تلقائية، مع دعم للوصول العالمي والشبكات المحلية. يستخدم Flask كخادم ويب و Gemini API للذكاء الاصطناعي.

## 🚀 الميزات الرئيسية

### الذكاء الاصطناعي
- 🧠 **Gemini 2.0 Flash**: أحدث نموذج من Google
- 🖼️ **تحليل الصور**: دعم كامل للصور والملفات
- 🌍 **متعدد اللغات**: عربي وإنجليزي وأكثر
- 💬 **ذاكرة المحادثة**: يتذكر السياق والمحادثات السابقة

### الخدمة والنشر
- ⚙️ **Windows Service**: يعمل تلقائياً مع Windows
- 📅 **Task Scheduler**: جدولة تلقائية للمهام
- 🔄 **إعادة التشغيل التلقائي**: في حالة الأخطاء
- 📊 **السجلات المفصلة**: مراقبة شاملة للأداء

### الشبكة والأمان
- 🌐 **الوصول العالمي**: `host="0.0.0.0"`
- 🔒 **جدار الحماية**: إعداد تلقائي للمنفذ 80
- 🛡️ **أمان معزز**: إعدادات إنتاج آمنة
- 📡 **اختبار الشبكة**: أدوات فحص الاتصال

## 🔧 الإعداد السريع

### المتطلبات
- Windows 10/11 أو Server 2016+
- Python 3.8+
- صلاحيات Administrator (للمنفذ 80)

### التثبيت (دقيقتان)
```batch
# 1. تحميل NSSM من https://nssm.cc/download
# 2. وضع nssm.exe في مجلد المشروع
# 3. تشغيل كـ Administrator
install_service.bat
```

### الوصول الفوري
```
افتح المتصفح: http://localhost
```

## 📁 هيكل المشروع

```
chatbot-2025-05/
├── 🤖 الملفات الأساسية
│   ├── app.py                 # التطبيق الرئيسي
│   ├── run.py                 # نقطة الدخول
│   ├── config.py              # الإعدادات الأساسية
│   └── production_config.py   # إعدادات الإنتاج
│
├── ⚙️ ملفات الخدمة
│   ├── service_manager.bat    # 🎛️ أداة الإدارة الشاملة
│   ├── install_service.bat    # تثبيت NSSM Service
│   ├── uninstall_service.bat  # إلغاء تثبيت الخدمة
│   ├── start_service.bat      # تشغيل مباشر
│   └── test_service.bat       # اختبار النظام
│
├── 📅 ملفات Task Scheduler
│   ├── create_task_scheduler.bat
│   └── remove_task_scheduler.bat
│
├── 🌐 ملفات الشبكة
│   ├── setup_firewall.bat     # إعداد جدار الحماية
│   ├── network_test.bat       # اختبار الشبكة
│   └── start_global_access.bat # ⚠️ وصول عالمي
│
├── 📚 التوثيق
│   ├── QUICK_START.md         # دليل البدء السريع
│   ├── SERVICE_SETUP_GUIDE.md# دليل الإعداد المفصل
│   ├── SERVICE_README.md      # هذا الملف
│   └── SECURITY_WARNING.md    # تحذيرات الأمان
│
├── 📊 البيانات والسجلات
│   ├── data/                  # بيانات المحادثات
│   ├── logs/                  # سجلات الخدمة
│   └── uploads/               # الملفات المرفوعة
│
└── 🎨 الواجهة
    ├── templates/             # صفحات HTML
    └── static/                # CSS, JS, الصور
```

## 🎛️ أداة الإدارة الشاملة

استخدم `service_manager.bat` للوصول لجميع الوظائف:

```
========================================
        AI Chatbot Service Manager
========================================

1. Install Service (NSSM)
2. Uninstall Service
3. Start Service
4. Stop Service
5. Restart Service
6. Check Service Status
7. View Service Logs
8. Setup Task Scheduler
9. Configure Firewall
10. Test Network Access
11. Start Global Access
0. Exit
```

## 🌐 طرق الوصول

### المحلي
```
http://localhost
```

### الشبكة المحلية (آمن)
```
http://192.168.1.100
http://10.0.0.50
```

### الإنترنت العام (⚠️ يتطلب إعدادات أمان)
```
http://YOUR-PUBLIC-IP
```

## 🔒 مستويات الأمان

### 🟢 آمن - الوصول المحلي
- العنوان: `127.0.0.1`
- المنفذ: 80
- الوصول: الجهاز نفسه فقط

### 🟡 متوسط - الشبكة المحلية
- العنوان: `0.0.0.0`
- المنفذ: 80
- الوصول: الأجهزة في نفس الشبكة
- **الإعداد الحالي**

### 🔴 خطير - الوصول العالمي
- العنوان: `0.0.0.0`
- المنفذ: 80
- الوصول: من أي مكان في العالم
- **يتطلب**: إعدادات أمان متقدمة

## ⚙️ إعدادات الخدمة

### معلومات أساسية
| المعلومة | القيمة |
|----------|---------|
| **اسم الخدمة** | AIChatbotService |
| **المنفذ** | 80 (HTTP الافتراضي) |
| **النوع** | Windows Service |
| **بدء التشغيل** | تلقائي مع Windows |
| **المستخدم** | LocalSystem |

### مسارات مهمة
| النوع | المسار |
|-------|--------|
| **السجلات** | `logs/service_*.log` |
| **البيانات** | `data/` |
| **الرفع** | `uploads/` |
| **التكوين** | `config.py` |

## 🛠️ استكشاف الأخطاء

### المشاكل الشائعة

#### 1. الخدمة لا تبدأ
```batch
# فحص السجلات
type logs\service_error.log

# اختبار يدوي
python run.py

# إعادة تثبيت
uninstall_service.bat
install_service.bat
```

#### 2. المنفذ 80 مستخدم
```batch
# فحص من يستخدم المنفذ
netstat -ano | findstr :80

# إيقاف IIS إذا كان مثبتاً
net stop w3svc

# أو تغيير المنفذ في config.py
```

#### 3. مشاكل الصلاحيات
```batch
# تشغيل كـ Administrator
# إعطاء صلاحيات للمجلد
icacls . /grant Users:F

# تحقق من صلاحيات الخدمة
sc qc AIChatbotService
```

#### 4. لا يمكن الوصول من الشبكة
```batch
# فحص جدار الحماية
setup_firewall.bat

# اختبار الشبكة
network_test.bat

# فحص إعدادات الـ Router
```

### أدوات التشخيص

```batch
# اختبار شامل للنظام
test_service.bat

# فحص حالة الخدمة
sc query AIChatbotService

# مراقبة السجلات المباشرة
powershell Get-Content logs\service_output.log -Wait

# فحص الاتصالات النشطة
netstat -an | findstr :80
```

## 📊 مراقبة الأداء

### مراقبة الذاكرة
```batch
tasklist | findstr python
```

### مراقبة الشبكة
```batch
netstat -an | findstr :80
```

### مراقبة السجلات
```batch
# عرض آخر 50 سطر
powershell Get-Content logs\service_output.log -Tail 50

# مراقبة مباشرة
powershell Get-Content logs\service_output.log -Wait
```

## 🔄 إدارة النسخ الاحتياطية

### نسخ احتياطي يدوي
```batch
# نسخ البيانات
xcopy data backup\data /E /I

# نسخ الإعدادات
copy config.py backup\
copy production_config.py backup\
```

### استعادة النسخ الاحتياطية
```batch
# استعادة البيانات
xcopy backup\data data /E /I /Y

# استعادة الإعدادات
copy backup\config.py .
copy backup\production_config.py .
```

## 🌟 الميزات المتقدمة

### إعدادات الإنتاج
- استخدم `production_config.py` للإعدادات المحسنة
- تفعيل السجلات المفصلة
- تحسين الأداء والأمان

### التكامل مع Firebase
- حفظ المحادثات في السحابة
- مزامنة البيانات بين الأجهزة
- نسخ احتياطية تلقائية

### دعم الملفات والصور
- رفع وتحليل الصور
- دعم المستندات المختلفة
- معالجة ذكية للمحتوى

## 🚀 التحسينات المستقبلية

### قيد التطوير
- [ ] واجهة إدارة ويب
- [ ] API للتطبيقات الخارجية
- [ ] دعم المزيد من نماذج الذكاء الاصطناعي
- [ ] نظام المصادقة المتقدم

### الميزات المخططة
- [ ] كاش ذكي للاستجابات
- [ ] تحليلات الاستخدام
- [ ] إشعارات النظام
- [ ] تحديثات تلقائية

## 📞 الدعم والمساعدة

### الموارد المفيدة
- **دليل البدء السريع**: `QUICK_START.md`
- **دليل الإعداد المفصل**: `SERVICE_SETUP_GUIDE.md`
- **تحذيرات الأمان**: `SECURITY_WARNING.md`

### اختبار النظام
```batch
# اختبار شامل
test_service.bat

# أداة الإدارة
service_manager.bat

# اختبار الشبكة
network_test.bat
```

### الحصول على المساعدة
1. فحص السجلات أولاً
2. تشغيل أدوات التشخيص
3. مراجعة دليل استكشاف الأخطاء
4. إعادة التثبيت إذا لزم الأمر

---

## 🎯 الخلاصة

هذا النظام يوفر حل شامل لتشغيل AI Chatbot كخدمة Windows مع:
- ✅ إعداد سهل وسريع
- ✅ إدارة متقدمة
- ✅ مراقبة شاملة
- ✅ أمان قابل للتخصيص
- ✅ دعم فني كامل

**🚀 ابدأ الآن**: `service_manager.bat`

**⚠️ تذكر**: المنفذ 80 يتطلب صلاحيات إدارية ويسمح بالوصول بدون تحديد رقم المنفذ!