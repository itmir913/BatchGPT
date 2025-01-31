from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


# Usage:
# python manage.py set_balance <username> <amount>
#
# Example:
# python manage.py set_balance itmir913 100.00
# This will set the balance of 'itmir913' to 100.00.
class Command(BaseCommand):
    help = 'Set balance for an existing user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('amount', type=float)

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        amount = kwargs['amount']
        User = get_user_model()

        try:
            user = User.objects.get(username=username)
            user.balance += Decimal(amount)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'{username}\'s balance has been set to {amount}.'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist.'))
