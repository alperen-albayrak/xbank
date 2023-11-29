from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Subquery, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View

from transactions.forms import (AddWalletForm, EditWalletForm, DeleteWalletForm, AddRecordForm, DeleteRecordForm,
                                CancelTransactionForm)
from transactions.mixins import ThisPersonWalletMixin, ThisPersonTransactionMixin
from transactions.models import Wallet, Transaction
from users.models import Person
from decimal import Decimal


# Create your views here.

class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        person = request.user.person
        transaction_list = Transaction.objects.filter(
            Q(from_wallet__in=person.wallets.all()) | Q(to_wallet__in=person.wallets.all())
        ).order_by("-timestamp")

        # transaction_list = Wallet.objects.filter(person=request.user.person).filter(is_active=True)
        return render(request, 'pages/transactions.html', {'segment': 'transactions',
                                                           'transactions': transaction_list,

                                                           })


class WalletsView(LoginRequiredMixin, View):
    def get(self, request):
        wallet_list = Wallet.objects.filter(person=request.user.person)
        return render(request, 'pages/wallets.html', {'segment': 'wallets',
                                                      'wallets': wallet_list
                                                      })


class AddWalletView(LoginRequiredMixin, View):
    def post(self, request):
        wallet = Wallet()
        form = AddWalletForm(request.POST, instance=wallet)
        if form.is_valid():
            if request.user.person.is_active:
                wallet.person = request.user.person
                wallet.save()
                # request.user.person.wallets.add(wallet)
            send_mail(
                subject="A wallet created !",
                message="A wallet named  {wallet_name} created.".format(
                    wallet_name=wallet.name,
                ),
                from_email="xbank@alperenalbayrak.dev",
                recipient_list=[wallet.person.user.email],
                fail_silently=False
            )
            print('Wallet created successfully!')
            return redirect('/onlinebank/transactions/wallets/')
        else:
            print("Creation failed!")
        context = {'form': form,
                   "form_name": "Create Wallet"}
        return render(request, 'pages/form.html', context)

    def get(self, request):
        form = AddWalletForm()
        context = {'form': form,
                   "form_name": "Create Wallet"}
        return render(request, 'pages/form.html', context)


class EditWalletView(ThisPersonWalletMixin, View):
    def post(self, request, wallet_id):
        wallet = Wallet.objects.get(id=wallet_id)
        wallet_name = wallet.name

        form = EditWalletForm(request.POST, instance=wallet)
        if form.is_valid():
            if request.user.person.is_active:
                wallet.save()
                send_mail(
                    subject="A wallet's name changed!",
                    message="A wallet named {wallet_name_ex} changed to {wallet_name}.".format(
                        wallet_name_ex=wallet_name,
                        wallet_name=wallet.name,
                    ),
                    from_email="xbank@alperenalbayrak.dev",
                    recipient_list=[wallet.person.user.email],
                    fail_silently=False
                )
                print('Wallet edited successfully!')
            return redirect('/onlinebank/transactions/wallets/')
        else:
            print("Process failed!")
        context = {'form': form,
                   "form_name": "Edit Wallet",
                   }
        return render(request, 'pages/form.html', context)

    def get(self, request, wallet_id):
        wallet = Wallet.objects.get(id=wallet_id)
        form = EditWalletForm(initial={'name': wallet.name})
        context = {
            'form': form,
            "form_name": "Edit Wallet"
        }
        return render(request, 'pages/form.html', context)


class DeleteWalletView(ThisPersonWalletMixin, View):
    def post(self, request, wallet_id):
        wallet = Wallet.objects.get(id=wallet_id)
        form = DeleteWalletForm(request.POST, instance=wallet)
        if form.is_valid():
            if request.user.person.is_active:
                wallet.is_active = False
                wallet.save()
                send_mail(
                    subject="A wallet deleted!",
                    message="A wallet named  {wallet_name} deleted.".format(
                        wallet_name=wallet.name,
                    ),
                    from_email="xbank@alperenalbayrak.dev",
                    recipient_list=[wallet.person.user.email],
                    fail_silently=False
                )
                print('Wallet deleted successfully!')
            return redirect('/onlinebank/transactions/wallets/')
        else:
            print("Process failed!")
        context = {'form': form,
                   "form_name": "Delete Wallet",
                   }
        return render(request, 'pages/form.html', context)

    def get(self, request, wallet_id):
        wallet = Wallet.objects.get(id=wallet_id)
        form = DeleteWalletForm(initial={'name': wallet.name})
        context = {
            'form': form,
            "form_name": "Delete Wallet"
        }
        return render(request, 'pages/form.html', context)


class RecordedWalletView(LoginRequiredMixin, View):
    def get(self, request):
        person = request.user.person
        wallet_list = person.recorded_wallets.all()  # .filter(is_active=True)
        return render(request, 'pages/recorded-wallet.html', {'segment': 'recorded',
                                                              'wallets': wallet_list
                                                              })


class AddRecordView(View):
    def post(self, request):
        form = AddRecordForm(request.POST)
        person = request.user.person
        if form.is_valid():
            if person.is_active:
                wallet = Wallet.objects.get(id=form.cleaned_data["id"])
                if wallet.is_active:
                    person.recorded_wallets.add(wallet)
                    send_mail(
                        subject="A wallet added to recorded wallets!",
                        message="A wallet from  {wallet_holder} added to recorded wallets.".format(
                            wallet_holder=wallet.person.user.first_name + " " + wallet.person.user.last_name,
                        ),
                        from_email="xbank@alperenalbayrak.dev",
                        recipient_list=[wallet.person.user.email],
                        fail_silently=False
                    )
                    print('Wallet recorded successfully!')
                    return redirect('recorded-wallet')

        print("Process failed!")
        context = {'form': form,
                   "form_name": "Record Wallet"}
        return render(request, 'pages/form.html', context)

    def get(self, request):
        form = AddRecordForm()
        context = {'form': form,
                   "form_name": "Record Wallet"}
        return render(request, 'pages/form.html', context)


class DeleteRecordView(View):
    def post(self, request, wallet_id):
        form = DeleteRecordForm(request.POST)
        person = request.user.person
        if form.is_valid():
            if person.is_active:
                wallet = Wallet.objects.get(id=wallet_id)
                person.recorded_wallets.remove(wallet)
                send_mail(
                    subject="A wallet deleted to recorded wallets!",
                    message="A wallet from  {wallet_holder} deleted to recorded wallets.".format(
                        wallet_holder=wallet.person.user.first_name + " " + wallet.person.user.last_name,
                    ),
                    from_email="xbank@alperenalbayrak.dev",
                    recipient_list=[wallet.person.user.email],
                    fail_silently=False
                )
                print('Record deleted successfully!')
                return redirect('recorded-wallet')
        else:
            print("Process failed!")
        context = {'form': form,
                   "form_name": "Delete Record",
                   }
        return render(request, 'pages/form.html', context)

    def get(self, request, wallet_id):
        wallet = Wallet.objects.get(id=wallet_id)
        form = DeleteWalletForm(initial={'name': wallet.name})
        context = {
            'form': form,
            "form_name": "Delete Record"
        }
        return render(request, 'pages/form.html', context)


class MakeTransactionsView(View):
    def post(self, request):
        person = request.user.person

        if person.is_active:
            t = Transaction()
            t.to_wallet = Wallet.objects.get(id=request.POST.get("to_wallet"))
            t.from_wallet = Wallet.objects.get(id=request.POST.get("from_wallet"))
            t.description = request.POST.get("description")
            t.amount = Decimal(request.POST.get("amount"))
            if t.from_wallet.currency == t.to_wallet.currency:
                if t.from_wallet.expendable_balance >= t.amount:

                    t.from_wallet.expendable_balance -= t.amount
                    t.from_wallet.save()

                    t.to_wallet.balance += t.amount
                    t.to_wallet.save()

                    t.save()
                    send_mail(
                        subject="A {amount:.2f}{currency} transaction made to {to_wallet_holder}".format(
                            amount=t.amount,
                            currency=t.from_wallet.currency,
                            to_wallet_holder=t.to_wallet.person.user.first_name+" "+t.to_wallet.person.user.last_name,
                        ),
                        message="""
A {amount:.2f}{currency} transaction made from {from_wallet_name} to {to_wallet_holder} at {timestamp}.
You can cancel at http://127.0.0.1:8000/onlinebank/transactions/{transaction_id}/cancel-transaction.""".format(
                            amount=t.amount,
                            currency=t.from_wallet.currency,
                            from_wallet_name=t.from_wallet.name,
                            to_wallet_holder=t.to_wallet.person.user.first_name+" "+t.to_wallet.person.user.last_name,
                            timestamp=t.timestamp,
                            transaction_id=t.id,
                        ),
                        from_email="xbank@alperenalbayrak.dev",
                        recipient_list=[t.from_wallet.person.user.email],
                        fail_silently=False
                    )
                    # Email to receiver
                    send_mail(
                        subject="A {amount:.2f}{currency} transaction made to you!".format(
                            amount=t.amount,
                            currency=t.from_wallet.currency,
                        ),
                        message="""
A {amount:.2f}{currency} transaction from {from_wallet_holder} to {to_wallet_name} made.
In 1 hour you can spend it!""".format(
                            amount=t.amount,
                            currency=t.from_wallet.currency,
                            from_wallet_holder=t.from_wallet.person.user.first_name + " " + t.from_wallet.person.user.last_name,
                            to_wallet_name=t.to_wallet.name,
                        ),
                        from_email="xbank@alperenalbayrak.dev",
                        recipient_list=[t.to_wallet.person.user.email],
                        fail_silently=False
                    )
                    print('Transaction made successfully!')
                    return redirect('/onlinebank/transactions/')
                else:
                    print("Expendable balance is not enough.")
            else:
                print("Choose same currency wallets.")

        context = {'from_wallet_options': person.wallets.all(),
                   'to_wallet_options': person.recorded_wallets.all(),
                   "form_name": "Make Transaction"}
        return render(request, 'pages/make-transactions.html', context)

    def get(self, request):
        person = request.user.person
        context = {'from_wallet_options': person.wallets.all(),
                   'to_wallet_options': person.recorded_wallets.all(),
                   "form_name": "Make Transaction"}
        return render(request, 'pages/make-transactions.html', context)


class CancelTransactionView(ThisPersonTransactionMixin, View):
    def post(self, request, transaction_id):
        form = CancelTransactionForm(request.POST)
        person = request.user.person
        if form.is_valid():
            if person.is_active:
                t = Transaction.objects.get(id=transaction_id)

                t.from_wallet.expendable_balance += t.amount
                t.from_wallet.save()

                t.to_wallet.balance -= t.amount
                t.to_wallet.save()

                t.status = "CCL"
                t.save()

                # Email to sender
                send_mail(
                    subject="A {amount:.2f}{currency} transaction canceled!".format(
                        amount=t.amount,
                        currency=t.from_wallet.currency,
                    ),
                    message="""
A {amount:.2f}{currency} transaction from {from_wallet_name} to {to_wallet_holder} was canceled.""".format(
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
                    subject="A {amount:.2f}{currency} transaction canceled!".format(
                        amount=t.amount,
                        currency=t.from_wallet.currency,
                    ),
                    message="""
A {amount:.2f}{currency} transaction from {from_wallet_holder} to {to_wallet_name} was canceled.""".format(
                        amount=t.amount,
                        currency=t.from_wallet.currency,
                        from_wallet_holder=t.from_wallet.person.user.first_name + " " + t.from_wallet.person.user.last_name,
                        to_wallet_name=t.to_wallet.name,
                    ),
                    from_email="xbank@alperenalbayrak.dev",
                    recipient_list=[t.to_wallet.person.user.email],
                    fail_silently=False
                )

                print('Process canceled successfully!')
                return redirect('transactions')
        else:
            print("Process failed!")
        context = {'form': form,
                   "form_name": "Cancel Transaction",
                   }
        return render(request, 'pages/form.html', context)

    def get(self, request, transaction_id):
        t = Transaction.objects.get(id=transaction_id)
        form = CancelTransactionForm()
        context = {
            'transaction':t,
            'form': form,
            "form_name": "Cancel Transaction"
        }
        return render(request, 'pages/cancel-transaction.html', context)
