from django.urls import path
from .views import LoginView, RegisterView, LogoutView, ActivationView, AccountInfoView, ConfirmMailChangeView, ForgotPasswordView, PasswordResetView

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>', ActivationView.as_view(), name='activate'),
    path('accountInfo', AccountInfoView.as_view(), name='accountInfo'),
    path('confirmMailChange/<uidb64>/<token>/<newEmail>', ConfirmMailChangeView.as_view(), name='confirmMailChange'),
    path('forgotPassword', ForgotPasswordView.as_view(), name='forgotPassword'),
    path('passwordReset/<uidb64>/<token>', PasswordResetView.as_view(), name='passwordReset'),
]