from django.views.generic import DetailView, View
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.utils import timezone
from .models import Games, Review
from checkout.models import Order
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from .models import Games
from .forms import GameForm


class GameDetailView(LoginRequiredMixin, DetailView):
    model = Games
    template_name = 'games/gameTemplate.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['games'] = user.games.all()
        return context


class SubmitReviewView(View):
    def get(self, request, game_id):
        user = request.user
        game = get_object_or_404(Games, pk=game_id)

        if Review.objects.filter(user=user, game=game).exists():
            return UpdateReviewView.as_view()(request, game_id)

        user_review = request.GET.get('review')
        is_recommended = 1 if request.GET.get('isRecommended') == 'on' else 0
        Review.objects.create(user=user, game=game, verdict=is_recommended, review=user_review)

        reviews = game.review_set.all()
        user_review = game.review_set.filter(user=user)
        return render(request, 'games/gameTemplate.html', context={"game": game, "reviews": reviews, "user_review": user_review})


class UpdateReviewView(View):
    def get(self, request, game_id):
        user = request.user
        game = get_object_or_404(Games, pk=game_id)
        old_review = get_object_or_404(Review, user=user, game=game)

        new_review = request.GET.get('review')
        new_verdict = 1 if request.GET.get('isRecommended') == 'on' else 0

        old_review.review = new_review
        old_review.verdict = new_verdict
        old_review.review_date = timezone.now()
        old_review.save()

        reviews = game.review_set.all()
        user_review = game.review_set.filter(user=user)
        return render(request, 'games/gameTemplate.html', context={"game": game, "reviews": reviews, "user_review": user_review})
    
class GameUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Games
    form_class = GameForm
    template_name = 'games/gameTemplate.html'  
    context_object_name = 'game'

    def get_success_url(self):
        return reverse_lazy('game', kwargs={'pk': self.object.pk})

    def test_func(self):
        game = self.get_object()
        return game.user.id == self.request.user.id
