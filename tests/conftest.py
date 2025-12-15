import os
from pathlib import Path

import django

# For pytest-django, set the DJANGO_SETTINGS_MODULE to the tests-specific settings.
os.environ['DJANGO_SETTINGS_MODULE'] = 'business_workflow.settings_test'
django.setup()

# Path to your project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ":memory:",
    }
}

pytest_plugins = [
    "tests.fixtures"
]
