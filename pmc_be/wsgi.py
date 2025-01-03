"""
WSGI config for pmc_be project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""
from pmc_be import settings

"""
WSGI config for pmc_be project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append('/var/www/vhosts/pmc/pmc_be')
sys.path.append('/var/www/vhosts/pmc/myenv2/lib/python3.12/site-packages')

from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.wsgi import get_wsgi_application

#
# # add the virtualenv site-packages path to the sys.path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pmc_be.settings")

if settings.DEBUG:
    application = StaticFilesHandler(get_wsgi_application())
else:
    application = get_wsgi_application()
