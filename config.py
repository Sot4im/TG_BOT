import os

TOKEN = ""

ADMIN_ID =2141337014

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, 'media')

print(f"✅ Конфигурация загружена")
print(f"👤 Админ ID: {ADMIN_ID}")
