import os
import sys

# Add the Django project directory ('analysis') to the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(current_dir, 'analysis')
sys.path.append(project_dir)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analysis.settings')

# Import and expose the WSGI application for Vercel
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
