from django.views.generic import DetailView, View
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.utils import timezone
from .models import Games, Review
from checkout.models import Order


class GameDetailView(DetailView):
    model = Games
    template_name = 'games/gameTemplate.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.object
        context['reviews'] = game.review_set.all()
        context['user_review'] = game.review_set.filter(user=self.request.user)
        context['isOwned'] = Order.objects.filter(user_id=self.request.user, game=game).exists()
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
