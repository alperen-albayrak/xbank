from django.core.mail import send_mail
from django.core.management import BaseCommand, CommandError
from django.db.models import F, Subquery, OuterRef

from transactions.models import Transaction, Wallet


class Command(BaseCommand):
    def handle(self, *args, **options):

        waiting_transactions = Transaction.objects.filter(status="WAT")
        for t in waiting_transactions:
            t.from_wallet.balance -= t.amount
            t.from_wallet.save()

            t.to_wallet.expendable_balance += t.amount
            t.to_wallet.save()

            t.status = "CMT"
            t.save()

            # Email to sender
            send_mail(
                subject="A {amount:.2f}{currency} transaction completed!".format(
                    amount=t.amount,
                    currency=t.from_wallet.currency,
                ),
                message="""
A {amount:.2f}{currency} transaction from {from_wallet_name} to {to_wallet_holder} completed.
Your balance is updated.""".format(
                    amount=t.amount,
                    currency=t.from_wallet.currency,
                    from_wallet_name=t.from_wallet.name,
                    to_wallet_holder=t.to_wallet.person.user.first_name + " " + t.to_wallet.person.user.last_name,
                ),
                from_email="xbank@alperenalbayrak.dev",
                recipient_list=[t.from_wallet.person.user.email],
                fail_silently=False
            )

            # Email to receiver
            send_mail(
                subject="A {amount:.2f}{currency} transaction completed!".format(
                    amount=t.amount,
                    currency=t.from_wallet.currency,
                ),
                message="""
A {amount:.2f}{currency} transaction from {from_wallet_holder} to {to_wallet_name} was completed.
Your expendable balance is updated.""".format(
                    amount=t.amount,
                    currency=t.from_wallet.currency,
                    from_wallet_holder=t.from_wallet.person.user.first_name + " " + t.from_wallet.person.user.last_name,
                    to_wallet_name=t.to_wallet.name,
                ),
                from_email="xbank@alperenalbayrak.dev",
                recipient_list=[t.to_wallet.person.user.email],
                fail_silently=False
            )
