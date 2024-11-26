from django.urls import path
from .views import CheckoutView, PaymentSuccessView, PaymentFailedView

urlpatterns = [
    path('checkout/<int:game_id>/', CheckoutView.as_view(), name='checkout'),
    path('paymentSuccess/<int:game_id>/', PaymentSuccessView.as_view(), name='paymentSuccess'),
    path('paymentFailed/<int:game_id>/', PaymentFailedView.as_view(), name='paymentFailed'),
]
