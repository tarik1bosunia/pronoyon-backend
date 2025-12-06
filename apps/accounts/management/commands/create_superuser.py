from django.core.management.base import BaseCommand
from django.db.utils import ProgrammingError, OperationalError
from apps.accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create a default superuser for development'

    def handle(self, *args, **options):
        email = 't@t.com'
        password = 't'
        
        try:
            if CustomUser.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'Superuser with email {email} already exists')
                )
                return
            
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
        except (ProgrammingError, OperationalError) as e:
            self.stdout.write(
                self.style.WARNING(
                    f'Superuser creation skipped - database tables may not exist yet: {str(e)}'
                )
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )
