
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """نموذج بيانات المستخدم"""
    id = db.Column(db.Integer, primary_key=True)  # معرف تيليجرام للمستخدم
    username = db.Column(db.String(128), nullable=True)  # اسم المستخدم في تيليجرام
    first_name = db.Column(db.String(128), nullable=True)  # الاسم الأول
    last_name = db.Column(db.String(128), nullable=True)  # الاسم الأخير
    is_admin = db.Column(db.Boolean, default=False)  # هل المستخدم مشرف؟
    is_blocked = db.Column(db.Boolean, default=False)  # هل المستخدم محظور؟
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # وقت إنشاء الحساب
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)  # آخر نشاط

    # إحصائيات المستخدم
    files_processed = db.Column(db.Integer, default=0)  # عدد الملفات المعالجة
    total_file_size_mb = db.Column(db.Float, default=0.0)  # إجمالي حجم الملفات بالميجابايت
    daily_usage_mb = db.Column(db.Float, default=0.0)  # الاستخدام اليومي بالميجابايت
    daily_reset_date = db.Column(db.Date, nullable=True)  # تاريخ إعادة تعيين الاستخدام اليومي

    # بيانات إضافية (json)
    settings = db.Column(db.Text, default='{}')  # إعدادات المستخدم المخصصة

    # العلاقات
    user_templates = db.relationship('UserTemplate', backref='user', lazy=True, cascade="all, delete-orphan")
    user_logs = db.relationship('UserLog', backref='user', lazy=True, cascade="all, delete-orphan")

class UserTemplate(db.Model):
    """نموذج قوالب المستخدم الخاصة"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template_name = db.Column(db.String(128), nullable=False)  # اسم القالب
    artist_name = db.Column(db.String(128), nullable=False)  # اسم الفنان
    is_public = db.Column(db.Boolean, default=False)  # هل القالب عام؟
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # وقت إنشاء القالب
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # وقت آخر تحديث
    tags = db.Column(db.Text, nullable=False)  # الوسوم بتنسيق JSON
    album_art = db.Column(db.LargeBinary, nullable=True)  # صورة الألبوم
    album_art_mime = db.Column(db.String(50), nullable=True)  # نوع ملف صورة الألبوم

class UserLog(db.Model):
    """نموذج سجلات عمليات المستخدم"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(128), nullable=False)  # نوع العملية
    status = db.Column(db.String(50), default='success')  # حالة العملية
    details = db.Column(db.Text, nullable=True)  # تفاصيل العملية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # وقت العملية
    file_name = db.Column(db.String(256), nullable=True)  # اسم الملف (إن وجد)
    file_size_mb = db.Column(db.Float, default=0.0)  # حجم الملف بالميجابايت (إن وجد)
