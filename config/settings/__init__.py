"""
Settings package initialization.
Automatically loads the appropriate settings module based on DJANGO_SETTINGS_MODULE.
"""
import os

# Default to docker settings if not specified
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.docker')
