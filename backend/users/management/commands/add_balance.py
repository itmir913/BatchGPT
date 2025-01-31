from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


# Usage:
# python manage.py add_balance <username> <amount>
#
# Example:
# python manage.py add_balance itmir913 50.75
# This will add 50.75 to the balance of the user 'itmir913', if the user exists.
class Command(BaseCommand):
    help = 'Add balance to an existing user'

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
            self.stdout.write(
                self.style.SUCCESS(f'{amount} has been added to {username}\'s balance. New balance: {user.balance}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist.'))
