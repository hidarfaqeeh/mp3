import logging
import flask
import os
import threading
import traceback
import sys
from datetime import datetime

# استيراد نظام السجلات
from logger_setup import init_all_loggers, setup_exception_handler, log_error

# استيراد الإعدادات
from config import Config

# استيراد قاعدة البيانات
from models import db, User, UserLog

# Create a minimal Flask app (لكن لن نستخدمها حقًا)
app = flask.Flask(__name__)

# تكوين قاعدة البيانات
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# تهيئة قاعدة البيانات
db.init_app(app)

# إنشاء المجلدات المطلوبة
for directory in ['instance', 'logs', 'temp_audio_files', 'templates']:
    if not os.path.exists(directory):
        os.makedirs(directory)

# إنشاء جميع الجداول
with app.app_context():
    db.create_all()

# تم تعطيل واجهة الويب كما طلب المستخدم

# Flag to track if the bot is already running
bot_is_running = False
bot_thread = None

def run_bot():
    try:
        from bot import start_bot
        global bot_is_running
        bot_is_running = True
        logger = logging.getLogger('main')
        logger.info("بدء تشغيل البوت في خيط منفصل")
        start_bot()
    except Exception as e:
        bot_is_running = False
        log_error(e, "تشغيل البوت في خيط منفصل")

# إعداد نظام السجلات
logger = init_all_loggers()
setup_exception_handler()

if __name__ == '__main__':
    try:
        from bot import start_bot
        start_bot()
    except Exception as e:
        log_error(e, "تشغيل البوت المباشر")