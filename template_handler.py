# هذا الملف يحتوي على وظائف وهمية بديلة لتجنب أخطاء الاستيراد
# تم تعطيل ميزة القوالب

def save_template(*args, **kwargs):
    """وظيفة وهمية لحفظ القالب"""
    return False

def get_template(*args, **kwargs):
    """وظيفة وهمية للحصول على القالب"""
    return {}

def list_templates(*args, **kwargs):
    """وظيفة وهمية لسرد القوالب"""
    return []

def delete_template(*args, **kwargs):
    """وظيفة وهمية لحذف القالب"""
    return False

def extract_artist_from_tags(*args, **kwargs):
    """وظيفة وهمية لاستخراج اسم الفنان من الوسوم"""
    return ""

def get_artists_with_templates(*args, **kwargs):
    """وظيفة وهمية للحصول على الفنانين الذين لهم قوالب"""
    return []