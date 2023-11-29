from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.views import View

from transactions.models import Wallet
from users.forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth import logout

from users.models import Person


# Create your views here.


# Authentication
class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm


class RegisterView(View):
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            person = Person()
            person.user = user
            wallet = Wallet()
            wallet.name = "Başlangıç TRY"
            wallet.balance = 1000
            wallet.expendable_balance = 1000
            wallet.currency = 'TRY'
            wallet.person = person
            person.save()
            wallet.save()
            print('Account created successfully!')
            return redirect('/accounts/login/')
        else:
            print("Register failed!")
        context = {'form': form}
        return render(request, 'accounts/register.html', context)

    def get(self, request):
        form = RegistrationForm()
        context = {'form': form}
        return render(request, 'accounts/register.html', context)


class LogoutView(View, LoginRequiredMixin):
    def get(self, request):
        logout(request)
        return redirect('/accounts/login/')


class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = UserPasswordResetForm


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = UserSetPasswordForm


class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = UserPasswordChangeForm


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        context = {'segment': 'profile'}
        return render(request, 'pages/profile.html', context)


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'First Name'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Last Name'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Email'
                }
            ),
        }


class EditProfileView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user

        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            if request.user.person.is_active:
                user.save()
                user.person.save()
                send_mail(
                    subject="Profile Info Changed!",
                    message="Your profile info changed.",
                    from_email="xbank@alperenalbayrak.dev",
                    recipient_list=[user.email],
                    fail_silently=False
                )
                print('Profile edited successfully!')
            return redirect('/accounts/profile/')
        else:
            print("Process failed!")
        context = {'form': form,
                   "form_name": "Edit Profile",
                   }
        return render(request, 'pages/form.html', context)

    def get(self, request):
        person = request.user.person
        form = EditProfileForm(initial={
            'first_name': person.user.first_name,
            'last_name': person.user.last_name,
            'email': person.user.email,
        })
        context = {
            'form': form,
            "form_name": "Edit Profile"
        }
        return render(request, 'pages/form.html', context)