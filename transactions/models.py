from django.db import models

from users.models import Person

CURRENCIES = [
    ("TRY", "TRY"),
    ("USD", "USD"),
    ("EUR", "EUR"),
]


# Create your models here.
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class AbstractBaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True


class Wallet(AbstractBaseModel):
    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="wallets"
    )
    name = models.CharField(max_length=50)
    currency = models.CharField(max_length=3, choices=CURRENCIES, default="TRY")
    balance = models.IntegerField(default=0)
    expendable_balance = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    to_wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="incoming_transactions")
    from_wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="outgoing_transactions")
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=50)
    status = models.CharField(max_length=3, default="WAT")


class CurrencyRates(models.Model):
    from_currency = models.CharField(max_length=3, choices=CURRENCIES)
    to_currency = models.CharField(max_length=3, choices=CURRENCIES)
    ratio = models.DecimalField(decimal_places=4, max_digits=8)

    class Meta:
        unique_together = ('from_currency', 'to_currency',)


""""
Status Symbols

WAITING     WAT
CANCELED    CCL
COMPLETED   CMT
"""
