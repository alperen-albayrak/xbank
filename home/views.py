import datetime

from django import db
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, F, OuterRef, Subquery
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from transactions.models import Wallet, Transaction, CurrencyRates
from transactions.stats import Stats


# Create your views here.


# Pages
class HeroView(View):
    def get(self, request):
        context = {'segment': 'hero'}
        return render(request, 'pages/hero.html', context)


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        #db.reset_queries()
        person = request.user.person

        stats = Stats(person)

        context = {
            'segment': 'index',
            'transactions': stats.transaction_list,

            'wallet1': stats.calculate_wallet(0),
            'wallet2': stats.calculate_wallet(1),
            'wallet3': stats.calculate_wallet(2),
            'wallet4': stats.calculate_wallet(3),

            'balance_diff_percent_weekly': stats.calculate_balance_diff_percent_weekly(),
            'balance_diff_percent_monthly': stats.calculate_transaction_diff_percent_monthly(),
            'last_month': stats.get_month(-1),

            'month0': stats.get_month(0),
            'month1': stats.get_month(-1),
            'month2': stats.get_month(-2),
            'month3': stats.get_month(-3),
            'month4': stats.get_month(-4),
            'month5': stats.get_month(-5),
            'month6': stats.get_month(-6),
            'month7': stats.get_month(-7),
            'month8': stats.get_month(-8),

            'month0_income': stats.calculate_total_income_monthly(0),
            'month1_income': stats.calculate_total_income_monthly(-1),
            'month2_income': stats.calculate_total_income_monthly(-2),
            'month3_income': stats.calculate_total_income_monthly(-3),
            'month4_income': stats.calculate_total_income_monthly(-4),
            'month5_income': stats.calculate_total_income_monthly(-5),
            'month6_income': stats.calculate_total_income_monthly(-6),
            'month7_income': stats.calculate_total_income_monthly(-7),
            'month8_income': stats.calculate_total_income_monthly(-8),

            'month0_expense': stats.calculate_total_expense_monthly(0),
            'month1_expense': stats.calculate_total_expense_monthly(-1),
            'month2_expense': stats.calculate_total_expense_monthly(-2),
            'month3_expense': stats.calculate_total_expense_monthly(-3),
            'month4_expense': stats.calculate_total_expense_monthly(-4),
            'month5_expense': stats.calculate_total_expense_monthly(-5),
            'month6_expense': stats.calculate_total_expense_monthly(-6),
            'month7_expense': stats.calculate_total_expense_monthly(-7),
            'month8_expense': stats.calculate_total_expense_monthly(-8),
        }
        # 28 Queries
        # print(len(db.connection.queries))

        return render(request, 'pages/index.html', context)


"""class BillingView(LoginRequiredMixin, View):
    def get(self, request):
        context = {'segment': 'billing'}
        return render(request, 'pages/billing.html', context)


class TablesView(LoginRequiredMixin, View):
    def get(self, request):
        context = {'segment': 'tables'}
        return render(request, 'pages/tables.html', context)"""



