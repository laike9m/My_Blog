# choose settings between Developement and Deploy
import os
import platform

node = platform.node()

if node == "dell-PC":
    # Dev specific
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    # common
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    STATIC_ROOT = 'C:/ZY/EverythingandNothing/Python/Django/my_blog/static'
    STATIC_URL = '/static/'
    STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
    TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
    MEDIA_ROOT = 'C:/ZY/EverythingandNothing/Python/Django/my_blog/media'
    MEDIA_URL = '/media/'
    ALLOWED_HOSTS = ['*']
elif node == 'laike9mdeMacBook-Pro.local':
    # Dev specific
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    # common
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    STATIC_ROOT = '/Users/laike9m/Dev/Python/Envs/Blog/static'
    STATIC_URL = '/static/'
    STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
    TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
    MEDIA_ROOT = '/Users/laike9m/Dev/Python/Envs/Blog/media'
    MEDIA_URL = '/media/'
    ALLOWED_HOSTS = ['*']
else:
    DEBUG = False
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'database1',
            'USER': 'laike9m',
            'PASSWORD': os.environ["DJANGO_DB_PASSWORD"],
            'HOST': '',
            'PORT': '',
        }
    }
    MEDIA_ROOT = '/home/laike9m/webapps/media/'
    MEDIA_URL = '/media/'
    STATIC_ROOT = '/home/laike9m/webapps/static/'
    STATIC_URL = '/static/'
    STATICFILES_DIRS = (
        '/home/laike9m/webapps/my_blog/My_Blog/static/',
    )
    TEMPLATE_DIRS = (
        '/home/laike9m/webapps/my_blog/My_Blog/templates',
    )
    ALLOWED_HOSTS = ['.laike9m.com', '.laike9m.webfactional.com']

