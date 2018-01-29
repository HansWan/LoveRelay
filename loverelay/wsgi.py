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
sys.path.append('C:/Users/Administrator/Documents/Files/ITL/Python/python_work/LoveRelay/')
sys.path.append('C:/Users/Administrator/Documents/Files/ITL/Python/python_work/LoveRelay/loverelay/')
sys.path.append('C:/Users/Administrator/Documents/Files/ITL/Python/python_work/LoveRelay/loverelay/lib/site-packages/')

application = get_wsgi_application()
