import os
import sys
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newscraper.settings')

# Import Django
import django
from django.core.wsgi import get_wsgi_application

# Setup Django
django.setup()

# Create the WSGI application
application = get_wsgi_application()

# Vercel compatibility
app = application
handler = application
