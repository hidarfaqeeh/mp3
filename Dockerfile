# استخدم صورة Python الرسمية كأساس
FROM python:3.11-slim

# تعيين مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملفات المشروع إلى الحاوية
COPY . /app

# تثبيت المتطلبات إذا كان هناك requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || true

# الأمر الافتراضي لتشغيل التطبيق (عدله حسب حالتك)
CMD ["python", "bot.py"]
