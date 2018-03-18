"""
WSGI config for loverelay project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application 

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loverelay.settings")
sys.path.append('/usr/local/itl/python/LoveRelay/')
sys.path.append('/usr/local/itl/python/LoveRelay/loverelay/')
sys.path.append('/usr/local/lib/python3.5/dist-packages/django')
application = get_wsgi_application()

