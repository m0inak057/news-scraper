"""
WSGI config for newscraper project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newscraper.settings')

application = get_wsgi_application()

# Vercel expects either 'app' or 'handler' variable
app = application
handler = application
