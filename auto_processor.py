"""
وحدة المعالجة التلقائية للقنوات
تقوم بمراقبة القناة المحددة ومعالجة الملفات الصوتية تلقائياً
"""
import os
import re
import logging
import tempfile
from typing import Dict, Optional
from telebot import TeleBot
from config import Config
from tag_handler import get_audio_tags, set_audio_tags, extract_album_art
import datetime  # Import the datetime module

logger = logging.getLogger('auto_processor')

def setup_channel_handlers(bot: TeleBot):
    """
    إعداد معالجات رسائل القنوات
    Args:
        bot: كائن البوت
    """
    if not Config.AUTO_PROCESSING_ENABLED:
        logger.info("المعالجة التلقائية غير مفعلة")
        return

    if not Config.SOURCE_CHANNEL:
        logger.warning("لم يتم تحديد قناة المصدر للمعالجة التلقائية")
        return

    logger.info(f"تم تفعيل المعالجة التلقائية للقناة: {Config.SOURCE_CHANNEL}")

    @bot.channel_post_handler(content_types=['audio', 'document'])
    def handle_channel_audio(message):
        """معالجة الملفات الصوتية في القناة"""
        try:
            # التحقق من أن الرسالة من قناة المصدر
            if str(message.chat.id) != str(Config.SOURCE_CHANNEL):
                return

            # التحقق من نوع الملف
            logger.info(f"نوع المحتوى المستلم: {message.content_type}")

            if str(message.chat.id) == str(Config.SOURCE_CHANNEL):
                print("="*50)
                print(f"📢 تم استلام محتوى جديد من قناة المصدر: {message.chat.title}")
                print(f"⏰ الوقت: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"🎯 [SOURCE] منشور من قناة المصدر المستهدفة!")

                if message.content_type in ['audio', 'document']:
                    file_name = getattr(message.audio, 'file_name', None) or getattr(message.document, 'file_name', 'ملف غير معروف')
                    print(f"🎵 تم استلام ملف صوتي: {file_name}")
                    print(f"📁 نوع الملف: {message.content_type}")
                    logger.info(f"🎵 [AUDIO] ملف صوتي اكتُشف! بدء المعالجة...")
                    print("="*50)

            if message.content_type == 'audio':
                file_id = message.audio.file_id
                file_name = message.audio.file_name or f"audio_{file_id}.mp3"
                logger.info(f"تم اكتشاف ملف صوتي: {file_name}")
            elif message.content_type == 'document':
                # التحقق من نوع الملف بشكل أكثر شمولاً
                if (hasattr(message.document, 'mime_type') and 
                    (message.document.mime_type and message.document.mime_type.startswith('audio/') or
                     message.document.file_name.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a', '.flac')))):
                    file_id = message.document.file_id
                    file_name = message.document.file_name or f"audio_{file_id}"
                    logger.info(f"تم اكتشاف مستند صوتي: {file_name}")
                else:
                    logger.info(f"تم تجاهل مستند غير صوتي: {message.document.file_name if hasattr(message.document, 'file_name') else 'unknown'}")
                    return
            else:
                logger.info(f"تم تجاهل محتوى غير صوتي: {message.content_type}")
                return

            logger.info(f"معالجة ملف صوتي جديد في قناة المصدر: {file_id}")

            # تنزيل الملف
            file_info = bot.get_file(file_id)
            if not file_info.file_path:
                logger.error("لم يتم العثور على مسار الملف")
                return

            downloaded_file = bot.download_file(file_info.file_path)
            if not downloaded_file:
                logger.error("فشل تنزيل الملف")
                return

            # حفظ الملف مؤقتاً
            temp_dir = os.path.join(Config.TEMP_DIR, "auto_channel")
            os.makedirs(temp_dir, exist_ok=True)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', dir=temp_dir) as temp_file:
                temp_file.write(downloaded_file)
                temp_file_path = temp_file.name

            # قراءة القالب من الإعدادات
            template_tags = {
                'title': os.getenv('DEFAULT_TITLE', ''),
                'artist': os.getenv('DEFAULT_ARTIST', ''),
                'album': os.getenv('DEFAULT_ALBUM', ''),
                'album_artist': os.getenv('DEFAULT_ALBUM_ARTIST', ''),
                'year': os.getenv('DEFAULT_YEAR', ''),
                'genre': os.getenv('DEFAULT_GENRE', ''),
                'composer': os.getenv('DEFAULT_COMPOSER', ''),
                'comment': os.getenv('DEFAULT_COMMENT', ''),
                'track': os.getenv('DEFAULT_TRACK', ''),
                'lyrics': os.getenv('DEFAULT_LYRICS', '')
            }

            # تطبيق القالب
            output_path = process_audio_file(temp_file_path, template_tags, message.caption)

            if output_path:
                # إرسال الملف المعالج
                target_chat = Config.TARGET_CHANNEL or message.chat.id
                caption = prepare_caption(message.caption)

                try:
                    with open(output_path, 'rb') as audio_file:
                        sent_message = bot.send_audio(
                            target_chat,
                            audio_file,
                            caption=caption,
                            parse_mode='HTML'
                        )

                        if Config.AUTO_PUBLISH and str(target_chat).startswith('-100'):
                            bot.forward_message(target_chat, target_chat, sent_message.message_id)

                    # حذف الرسالة الأصلية إذا كان مطلوباً
                    if Config.DELETE_ORIGINAL and Config.TARGET_CHANNEL:
                        bot.delete_message(message.chat.id, message.message_id)

                except Exception as e:
                    logger.error(f"خطأ في إرسال الملف: {e}")

                finally:
                    cleanup_files(temp_file_path, output_path)

        except Exception as e:
            logger.error(f"خطأ في المعالجة التلقائية: {e}")

def prepare_caption(caption: Optional[str]) -> Optional[str]:
    """تحضير النص المرافق للملف"""
    if not caption:
        return None

    if Config.REMOVE_LINKS:
        caption = remove_links(caption)

    if Config.TAG_FOOTER_ENABLED and Config.TAG_FOOTER_TEXT:
        caption = f"{caption}\n\n{Config.TAG_FOOTER_TEXT}"

    return caption

def remove_links(text: str) -> str:
    """إزالة الروابط من النص"""
    if not text:
        return text
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r't\.me/\S+', '', text)
    text = re.sub(r'telegram\.me/\S+', '', text)
    return text.strip()

def process_audio_file(file_path: str, template_tags: Dict[str, str], caption: Optional[str]) -> Optional[str]:
    """معالجة ملف صوتي وتطبيق القالب"""
    try:
        current_tags = get_audio_tags(file_path)
        if not current_tags:
            current_tags = {}

        # دمج الوسوم الحالية مع القالب
        merged_tags = current_tags.copy()
        for tag, value in template_tags.items():
            if value:
                merged_tags[tag] = value

        # حفظ الملف المعدل
        output_dir = os.path.join(Config.TEMP_DIR, "auto_channel_output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, os.path.basename(file_path))

        # تطبيق الوسوم
        set_audio_tags(file_path, merged_tags, output_path)
        return output_path

    except Exception as e:
        logger.error(f"خطأ في معالجة الملف: {e}")
        return None

def cleanup_files(*file_paths: str) -> None:
    """تنظيف الملفات المؤقتة"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"خطأ في حذف الملف {file_path}: {e}")