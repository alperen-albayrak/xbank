from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404

from transactions.models import Wallet, Transaction


class ThisPersonWalletMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            wallet = request.user.person.wallets.get(id=kwargs.get("wallet_id"))
            return super().dispatch(request, *args, **kwargs)
        except Wallet.DoesNotExist:
            return self.handle_no_permission()


class ThisPersonTransactionMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            transaction = Transaction.objects.filter(
                Q(from_wallet__in=request.user.person.wallets.all()),
                Q(id=kwargs.get("transaction_id"))
            )
            return super().dispatch(request, *args, **kwargs)
        except Transaction.DoesNotExist:
            return self.handle_no_permission()
