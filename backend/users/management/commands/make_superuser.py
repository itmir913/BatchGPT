from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


# Usage:
# python manage.py upgrade_to_superuser <username>
#
# Example:
# python manage.py upgrade_to_superuser itmir913
# This will upgrade 'itmir913' to a superuser, granting both is_superuser and is_staff permissions.
class Command(BaseCommand):
    help = 'Upgrade an existing user to a superuser'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        User = get_user_model()

        try:
            user = User.objects.get(username=username)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'User {username} has been upgraded to superuser.'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist.'))
