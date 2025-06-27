"""
WSGI config for pmc_be project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""


import os
import sys
from django.core.wsgi import get_wsgi_application

# Add your project and virtualenv paths to sys.path
sys.path.append('/var/www/vhosts/pmc/pmc_be')
sys.path.append('/var/www/vhosts/pmc/myenv2/lib/python3.12/site-packages')

# Set the environment variable for Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pmc_be.settings")

application = get_wsgi_application()