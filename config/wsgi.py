import os
import sys

sys.path.insert(0, '/home/epi/21_niemiec/bird-app')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()