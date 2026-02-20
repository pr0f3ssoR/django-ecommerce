"""
WSGI config for ecommerce project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from pprint import pprint

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

def capture_raw_environ(application):
    def wrapper(environ, start_response):
        # Here environ is the raw, untouched WSGI environ
        # You could store it in a global, log it, or attach it to the request later
        # environ['RAW_ENVIRON_COPY'] = environ.copy() 

        # pprint(environ.get('HTTP_COOKIE'))
        return application(environ, start_response)
    return wrapper

application = capture_raw_environ(get_wsgi_application())