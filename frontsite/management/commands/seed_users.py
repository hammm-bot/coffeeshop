from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Seed initial user data'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('✅ Admin user created.'))

        for i in range(1, 2):
            username = f'user{i}'
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username, f'{username}@example.com', 'password')
                self.stdout.write(self.style.SUCCESS(f'✅ {username} created.'))
