import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_summarizer_api.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.utils import IntegrityError

# Get environment variables or use defaults
DJANGO_SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'tanvir')
DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'tanvir@example.com')
DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'tanvir')

try:
    superuser = User.objects.create_superuser(
        username=DJANGO_SUPERUSER_USERNAME,
        email=DJANGO_SUPERUSER_EMAIL,
        password=DJANGO_SUPERUSER_PASSWORD
    )
    superuser.save()
    print(f"Superuser {DJANGO_SUPERUSER_USERNAME} created successfully!")
except IntegrityError:
    print(f"Superuser {DJANGO_SUPERUSER_USERNAME} already exists!")
except Exception as e:
    print(e) 