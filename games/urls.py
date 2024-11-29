from django.urls import path
from . import views
from .views import GameDetailView, GameUpdateView, SubmitReviewView

urlpatterns = [
    path('submitReview/<int:game_id>/', SubmitReviewView.as_view(), name='submitReview'),
    path('gameTemplate/<int:pk>', GameDetailView.as_view(), name='game'),
    path('game/<int:pk>/edit/', GameUpdateView.as_view(), name='updateGameInfo'),
]

