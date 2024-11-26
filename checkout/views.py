from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.views.generic import View, TemplateView
from django.http import HttpResponse
from games.models import Games
from checkout.models import Order
from users.models import User
from paypal.standard.forms import PayPalPaymentsForm
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from random import randrange


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, game_id):
        req_game = get_object_or_404(Games, pk=game_id)
        if Order.objects.filter(user_id=request.user, game=req_game).exists():
            isOwned = True
            return render(request, 'checkoutForms/checkout.html', {'game': req_game, 'isOwned': isOwned})

        if Order.objects.exists():
            invoice_id = Order.objects.latest('id').id + 100
        else:
            invoice_id = randrange(100, 1000)

        host = request.get_host()
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': str(req_game.price),
            'item_name': str(req_game.name),
            'invoice': f'INVOICE-NO-{invoice_id}',
            'currency_code': 'USD',
            'notify_url': f'http://{host}{reverse("paypal-ipn")}',
            'return_url': f'http://{host}{reverse("checkout:paymentSuccess", kwargs={"game_id": game_id})}',
            'cancel_url': f'http://{host}{reverse("checkout:paymentFailed", kwargs={"game_id": game_id})}',
        }

        paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

        return render(request, 'checkoutForms/checkout.html', {'game': req_game, 'paypal_payment_button': paypal_payment_button})


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'checkoutForms/paymentSuccess.html'

    def get(self, request, game_id):
        req_game = get_object_or_404(Games, pk=game_id)
        newOrder = Order(user_id=request.user, game=req_game, cost=req_game.price)
        newOrder.save()

        send_mail(
            subject="Your game purchase was successful",
            message=f"Thank you {request.user.name} for your purchase of {req_game.name}.\nWe hope you will enjoy it.",
            fail_silently=False,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
        )
        return render(request, self.template_name)


class PaymentFailedView(TemplateView):
    template_name = 'checkoutForms/paymentFailed.html'
