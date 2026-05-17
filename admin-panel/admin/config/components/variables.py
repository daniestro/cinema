from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key')
DEBUG = True
ALLOWED_HOSTS = ['*']
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Сервис живёт за gateway под префиксом /admin/movies/
FORCE_SCRIPT_NAME = '/admin/movies/'
STATIC_URL = '/admin/movies/static/'
STATIC_ROOT = '/opt/admin/static'
MEDIA_URL = '/admin/movies/media/'
MEDIA_ROOT = '/opt/admin/media'
LOCALE_PATHS = ['movies/locale']
