from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create a default superuser for development'

    def handle(self, *args, **options):
        email = 't@t.com'
        password = 't'
        
        if CustomUser.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser with email {email} already exists')
            )
            return
        
        try:
            superuser = CustomUser.objects.create_superuser(
                email=email,
                password=password,
                first_name='Test',
                last_name='Admin'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser: {email} / {password}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )
