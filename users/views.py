from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, FormView
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .models import User
from .forms import registerForm
from .tokens import mail_change_token, password_reset_token
from random import randrange
from django.conf import settings
from games.models import Games
from .models import User
from django.template.loader import render_to_string


class ChangeEmailView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        new_email = request.POST.get('newEmail')
        subject = 'Confirm Email Change'
        message = render_to_string('forms/mailChangeMail.html', {
            'user': request.user.name,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(request.user.pk)),
            'newEmail': urlsafe_base64_encode(force_bytes(new_email)),
            'token': mail_change_token.make_token(request.user),
            'protocol': 'https' if request.is_secure() else 'http'
        })
        email = EmailMessage(subject=subject, body=message, to=[request.user.email])
        if email.send():
            messages.success(request, f'Confirmation email sent to {request.user.email}.')
        else:
            messages.error(request, f'Problem sending email to {request.user.email}.')
        return redirect('users:account_info')


class ConfirmMailChangeView(View):
    def get(self, request, uidb64, token, newEmail, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and mail_change_token.check_token(user, token):
            user.email = force_str(urlsafe_base64_decode(newEmail))
            user.save()
            messages.success(request, 'Email changed successfully.')
            return redirect('users:account_info')
        messages.error(request, 'Invalid or expired link.')
        return redirect('pages:home')


class RegisterView(FormView):
    template_name = 'forms/register.html'
    form_class = registerForm

    def form_valid(self, form):
        
        if User.objects.filter(name=form.cleaned_data['name']).exists():
            print("Nome já existe!")  
            form.add_error('name', 'Esse nome ja está em uso. Por favor, escolha um diferente.')
            return self.form_invalid(form)
        
        
        user = User(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            phone=form.cleaned_data['phone'],
            password=make_password(form.cleaned_data['password']),
            is_active=True  
        )
        user.save()  

       
        messages.success(self.request, 'Conta criada com sucesso, agora você pode fazer Login.')

        
        return redirect('users:login')


    def form_invalid(self, form):
        print("Formulário inválido:", form.errors)  
        return self.render_to_response({'form': form})


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'forms/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, name=username, password=password)
        if user and user.is_active:
            auth_login(request, user)
            return redirect('pages:home')
        if not user:
            messages.error(request, 'Nome ou senha inválidos.')
        elif not user.is_active:
            messages.error(request, 'A conta não está ativa')
        return redirect('users:login')


class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        messages.success(request, 'Você foi desconectado.')
        return redirect('pages:home')


class AccountInfoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'forms/accountInfo.html', {
            'username': request.user.name,
            'phone': request.user.phone,
            'email': request.user.email
        })

    def post(self, request, *args, **kwargs):
        if 'passwordSubmit' in request.POST:
            self.change_password(request)
        elif 'emailSubmit' in request.POST:
            new_email = request.POST.get('newEmail')
            ChangeEmailView().post(request, new_email=new_email)
        return redirect('users:account_info')

    def change_password(self, request):
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        if check_password(current_password, request.user.password):
            user = request.user
            user.password = make_password(new_password)
            user.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('users:login')
        messages.error(request, 'Current password is incorrect.')


class ForgotPasswordView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'forms/forgotPassword.html')

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            self.send_password_reset_email(request, user)
        return redirect('users:forgot_password')

    def send_password_reset_email(self, request, user):
        subject = 'Reset your password'
        message = render_to_string('forms/forgotPasswordMail.html', {
            'user': user.name,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': password_reset_token.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http'
        })
        email = EmailMessage(subject=subject, body=message, to=[user.email])
        email.send()


class PasswordResetView(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and password_reset_token.check_token(user, token):
            return render(request, 'forms/passwordReset.html', {'validlink': True})
        return render(request, 'forms/passwordReset.html', {'validlink': False})

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and password_reset_token.check_token(user, token):
            new_password = request.POST.get('newPassword')
            confirm_password = request.POST.get('newPasswordConfirm')
            if new_password == confirm_password:
                user.password = make_password(new_password)
                user.save()
                messages.success(request, 'Password reset successful. Please login.')
                return redirect('users:login')
            messages.error(request, 'Passwords do not match.')
        return redirect('users:password_reset', uidb64=uidb64, token=token)