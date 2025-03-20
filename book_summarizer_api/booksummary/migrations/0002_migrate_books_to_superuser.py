# Generated migration to associate existing books with superuser

from django.db import migrations
from django.contrib.auth import get_user_model

def transfer_books_to_superuser(apps, schema_editor):
    """
    Transfer all existing books to the superuser (username: tanvir1, password: tanvir)
    If the superuser doesn't exist, create it.
    """
    # Get the models
    Book = apps.get_model('booksummary', 'Book')
    User = apps.get_model('auth', 'User')  # Use the User model from apps
    
    # Check if superuser exists
    try:
        superuser = User.objects.get(username='tanvir1')
    except User.DoesNotExist:
        # Create superuser if it doesn't exist
        # For migration use create() instead of create_superuser
        superuser = User.objects.create(
            username='tanvir1',
            email='tanvir@example.com',
            is_staff=True,
            is_superuser=True,
        )
        superuser.set_password('tanvir')
        superuser.save()
        print(f"Created superuser: {superuser.username}")
    
    # Count books before migration
    total_books = Book.objects.count()
    
    # Associate all books with the superuser
    Book.objects.filter(owner__isnull=True).update(owner=superuser)
    
    # Count books after migration
    updated_books = Book.objects.filter(owner=superuser).count()
    
    print(f"Migrated {updated_books} out of {total_books} books to superuser {superuser.username}")


class Migration(migrations.Migration):

    dependencies = [
        # Update to depend on the migration that added the owner field
        ('booksummary', '0001_book_owner'),
    ]

    operations = [
        migrations.RunPython(transfer_books_to_superuser),
    ] 