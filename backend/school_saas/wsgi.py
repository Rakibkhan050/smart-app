import os
from django.core.wsgi import get_wsgi_application

# Use production settings if in Railway environment
if os.environ.get('RAILWAY_ENVIRONMENT'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_saas.production_settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_saas.settings')

application = get_wsgi_application()
