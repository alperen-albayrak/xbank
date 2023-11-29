import calendar
import datetime

from django.db.models import Q, Sum, F, Subquery, OuterRef
from django.utils import timezone

from transactions.models import Wallet, Transaction, CurrencyRates


class Stats:
    def __init__(self, person):
        self.person = person
        self.wallet_list = Wallet.objects.filter(person=person).order_by("-balance")[:4]
        wallets = person.wallets.all()
        self.transaction_list = Transaction.objects.filter(
            Q(from_wallet__in=wallets) | Q(to_wallet__in=wallets)
        ).order_by("-timestamp")[:7]

    # get relative month
    def monthdelta(self, date, delta):
        m, y = (date.month + delta) % 12, date.year + (date.month + delta - 1) // 12
        if not m: m = 12
        d = min(date.day, [31,
                           29 if y % 4 == 0 and (not y % 100 == 0 or y % 400 == 0) else 28,
                           31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
        return date.replace(day=d, month=m, year=y)

    def get_month(self, i):
        now = timezone.now()
        month = self.monthdelta(now, i)
        return calendar.month_name[month.month]

    def calculate_total_balance(self):
        return Wallet.objects.filter(person=self.person).aggregate(
            total_balance=Sum(
                F("balance") * Subquery(CurrencyRates.objects.filter(
                    from_currency=OuterRef("currency"),
                    to_currency="TRY"
                ).values("ratio")[:1])
            )
        ).get("total_balance")

    def calculate_wallet(self, i):
        if self.wallet_list:
            if len(self.wallet_list) > i:
                return self.wallet_list[i]
        return None

    def calculate_total_transactions(self, start_time, end_time, from_wallet=False, to_wallet=False):
        total_transactions = Transaction.objects.filter(
            status="CMT",
            timestamp__gte=start_time,
            timestamp__lte=end_time,
        )

        wallet_ids = self.person.wallets.values_list("id", flat=True)

        if from_wallet and not to_wallet:
            total_transactions = total_transactions.filter(
                from_wallet_id__in=wallet_ids
            )
        elif to_wallet and not from_wallet:
            total_transactions = total_transactions.filter(
                to_wallet_id__in=wallet_ids
            )
        elif from_wallet and to_wallet:
            total_transactions = total_transactions.filter(
                Q(to_wallet_id__in=wallet_ids) | Q(from_wallet_id__in=wallet_ids)
            )

        return total_transactions.aggregate(
            total_transactions=Sum(
                F("amount") *
                Subquery(
                    CurrencyRates.objects.filter(
                        from_currency=
                        OuterRef("from_wallet__currency"),
                        to_currency="TRY"
                    ).values("ratio")[:1]
                )
            )
        )

    def calculate_balance_diff_percent_weekly(self):
        date = datetime.date.today()
        now = timezone.now()

        this_week = now - datetime.timedelta(date.weekday())

        this_week_transactions_in = self.calculate_total_transactions(this_week, now, to_wallet=True)
        this_week_transactions_out = self.calculate_total_transactions(this_week, now, from_wallet=True)

        if this_week_transactions_in.get("total_transactions") and this_week_transactions_out.get("total_transactions"):
            this_week_transactions_diff = this_week_transactions_in.get(
                "total_transactions") - this_week_transactions_out.get("total_transactions")
        else:
            this_week_transactions_diff = 0

        total_balance = self.calculate_total_balance()

        if total_balance is None: total_balance = 0
        try:
            return "{:.2f}".format((((float(total_balance)) / (
                    float(total_balance) - float(
                this_week_transactions_diff))) - 1) * 100)
        except ZeroDivisionError:
            return 0

    def calculate_transaction_diff_percent_monthly(self):
        date = datetime.date.today()
        now = timezone.now()

        this_month = now.replace(day=1, hour=0, minute=0, second=0)

        # db.reset_queries()
        this_month_transactions_in = self.calculate_total_transactions(this_month, now, to_wallet=True)
        this_month_transactions_out = self.calculate_total_transactions(this_month, now, from_wallet=True)

        if this_month_transactions_in.get("total_transactions") and this_month_transactions_out.get(
                "total_transactions"):
            this_month_transactions_diff = this_month_transactions_in.get(
                "total_transactions") - this_month_transactions_out.get("total_transactions")
        else:
            this_month_transactions_diff = 0

        # print(db.connection.queries)

        total_balance = self.calculate_total_balance()

        if total_balance is None: total_balance = 0
        try:
            return "{:.2f}".format((((float(total_balance)) / (
                    float(total_balance) - float(
                this_month_transactions_diff))) - 1) * 100)
        except ZeroDivisionError:
            return 0

    def calculate_total_income_monthly(self, month_delta):
        now = timezone.now()
        month = self.monthdelta(now, month_delta)
        (_, last_day_index) = calendar.monthrange(year=month.year, month=month.month)
        first_day = month.replace(day=1, hour=0, minute=0, second=0)
        last_day = month.replace(day=last_day_index, hour=23, minute=59, second=59)
        ans = (self.calculate_total_transactions(start_time=first_day, end_time=last_day, to_wallet=True)
               .get("total_transactions"))
        if ans is None:
            return 0
        return ans

    def calculate_total_expense_monthly(self, month_delta):
        now = timezone.now()
        month = self.monthdelta(now, month_delta)
        (_, last_day_index) = calendar.monthrange(year=month.year, month=month.month)
        first_day = month.replace(day=1, hour=0, minute=0, second=0)
        last_day = month.replace(day=last_day_index, hour=23, minute=59, second=59)
        ans = (self.calculate_total_transactions(start_time=first_day, end_time=last_day, from_wallet=True)
               .get("total_transactions"))
        if ans is None:
            return 0
        return ans

