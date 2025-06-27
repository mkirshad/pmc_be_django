"""
WSGI config for pmc_be project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""


import os
import sys

# Add your project and virtualenv paths to sys.path
sys.path.append('/var/www/vhosts/staging/pmc_be')
sys.path.append('/var/www/vhosts/staging/myenv2/lib/python3.12/site-packages')

# Set the environment variable for Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pmc_be.settings")

# Import WSGI application
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

# Use StaticFilesHandler in production if serving static files through WSGI
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'pmc_be.settings':
    application = StaticFilesHandler(get_wsgi_application())
else:
    application = get_wsgi_application()


