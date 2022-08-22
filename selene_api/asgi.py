"""
ASGI config for selene_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selene_api.settings')

# application = get_asgi_application()


# import os

# import django
# from channels.http import AsgiHandler
# from channels.routing import ProtocolTypeRouter,get_default_application


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selene_api.settings')
# django.setup()


application=get_default_application()

import os
import django
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selene_api.settings')

django.setup()

application = get_default_application()