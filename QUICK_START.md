# 🚀 دليل البدء السريع - AI Chatbot Service

## البدء السريع (5 دقائق)

### الطريقة الأولى: NSSM Service (موصى بها)

1. **تحميل NSSM**
   ```
   - اذهب إلى: https://nssm.cc/download
   - حمل nssm.exe وضعه في مجلد المشروع
   ```

2. **تثبيت الخدمة**
   ```batch
   # انقر بالزر الأيمن على install_service.bat
   # اختر "Run as administrator"
   install_service.bat
   ```

3. **الوصول للتطبيق**
   ```
   افتح المتصفح واذهب إلى: http://localhost
   ```

### الطريقة الثانية: Task Scheduler

1. **إنشاء مهمة مجدولة**
   ```batch
   # انقر بالزر الأيمن على create_task_scheduler.bat
   # اختر "Run as administrator"
   create_task_scheduler.bat
   ```

2. **إعادة تشغيل الكمبيوتر**
   ```
   سيبدأ التطبيق تلقائياً بعد إعادة التشغيل
   ```

## 🎛️ إدارة الخدمة

### استخدام أداة الإدارة الشاملة
```batch
service_manager.bat
```

### الأوامر المباشرة
```batch
net start AIChatbotService      # تشغيل
net stop AIChatbotService       # إيقاف
net restart AIChatbotService    # إعادة تشغيل
```

## 🔧 استكشاف الأخطاء السريع

### 1. الخدمة لا تعمل؟
```batch
# فحص الحالة
sc query AIChatbotService

# عرض السجلات
type logs\service_error.log
```

### 2. المنفذ مستخدم؟
```batch
# فحص المنفذ 80
netstat -an | findstr :80

# أو غير المنفذ في config.py
```

### 3. مشاكل الصلاحيات؟
```
- تأكد من تشغيل الأوامر كـ Administrator
- تأكد من صلاحيات الكتابة في مجلد المشروع
- المنفذ 80 يتطلب صلاحيات إدارية
```

## 📂 الملفات المهمة

| الملف | الغرض |
|-------|--------|
| `service_manager.bat` | 🎛️ أداة الإدارة الشاملة |
| `install_service.bat` | ⚙️ تثبيت خدمة NSSM |
| `create_task_scheduler.bat` | 📅 إنشاء مهمة مجدولة |
| `start_service.bat` | ▶️ تشغيل مباشر |
| `start_global_access.bat` | 🌍 تشغيل مع وصول عالمي (⚠️) |
| `setup_firewall.bat` | 🔥 إعداد جدار الحماية |
| `network_test.bat` | 🌐 اختبار الوصول من الشبكة |

## 🌐 الوصول للتطبيق

- **المحلي**: http://localhost
- **الشبكة**: http://[IP-ADDRESS]

### 🔧 للوصول من أجهزة أخرى في الشبكة:
```batch
# إعداد جدار الحماية (Run as Administrator)
setup_firewall.bat

# اختبار الوصول من الشبكة
network_test.bat
```

## 📊 معلومات الخدمة

- **اسم الخدمة**: AIChatbotService
- **المنفذ**: 80 (HTTP الافتراضي)
- **السجلات**: `logs/` folder
- **البيانات**: `data/` folder

## ⚡ نصائح سريعة

1. **للاستخدام الشخصي**: استخدم Task Scheduler
2. **للخوادم**: استخدم NSSM Service
3. **للتطوير**: استخدم `python run.py`
4. **للإنتاج**: استخدم `production_config.py`
5. **للوصول العالمي**: `start_global_access.bat` (⚠️ اقرأ تحذيرات الأمان)

## 🆘 المساعدة السريعة

```batch
# إلغاء تثبيت الخدمة
uninstall_service.bat

# إزالة مهمة Task Scheduler
remove_task_scheduler.bat

# تشغيل مباشر للاختبار
python run.py
```

---

**💡 نصيحة**: استخدم `service_manager.bat` لإدارة كل شيء من مكان واحد!

**⚠️ تحذير**: قبل استخدام الوصول العالمي، اقرأ `SECURITY_WARNING.md`

**🔒 ملاحظة مهمة**: المنفذ 80 يتطلب صلاحيات إدارية ويمكن الوصول إليه بدون تحديد رقم المنفذ 