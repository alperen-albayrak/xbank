from django import forms

from transactions.models import Wallet, Transaction
from users.models import Person


class AddWalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ('name', 'currency',)

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Name'
                }
            ),
            'currency': forms.Select(

                attrs={
                    'class': 'form-control',
                    'placeholder': 'Currency'
                }
            ),
        }


class EditWalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ('name',)

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Name'
                }
            ),
        }


class DeleteWalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ()


class AddRecordForm(forms.Form):
    id = forms.IntegerField(label="Wallet Id")


class DeleteRecordForm(forms.Form):
    pass


"""class CustomFromWalletModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        ans = str(obj) + " || " + str(obj.expendable_balance) +"/"+ str(obj.balance)+ "|| " + str(obj.currency)
        return ans


class CustomToWalletModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        ans = ((str(obj.person.user.first_name) + " " +
               str(obj.person.user.first_name) + " || Wallet Id: " + str(obj.id)) +
               " || " + str(obj.currency))
        return ans"""


"""class MakeTransactionForm(forms.Form):
    amount = forms.IntegerField(label="Amount", min_value=0)
    from_wallet = forms.ChoiceField()
    to_wallet = forms.ChoiceField()
    description = forms.CharField(max_length=50)

    person = Person.objects.get(user_id=1)

    amount = forms.IntegerField(label="Amount", min_value=0)
    from_wallet = CustomFromWalletModelChoiceField(
        queryset=person.wallets,

    )
    to_wallet = CustomToWalletModelChoiceField(
        queryset=person.recorded_wallets
    )
    description = forms.CharField(
        max_length=50
    )"""


class CancelTransactionForm(forms.Form):
    pass