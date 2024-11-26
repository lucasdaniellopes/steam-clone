from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, View
from games.models import Games


class HomeView(ListView):
    model = Games
    template_name = 'pages/home.html'
    context_object_name = 'games'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['n'] = range(1, 4)
        return context


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class SearchView(View):
    template_name = 'pages/searchResult.html'

    def get(self, request, *args, **kwargs):
        searched_game = request.GET.get('searched', '')
        games = Games.objects.filter(name__icontains=searched_game)
        categories = Games.objects.values_list('category', flat=True).distinct()
        return render(request, self.template_name, {
            'searched': searched_game,
            'games': games,
            'categories': categories,
        })


class SearchByCategoryView(View):
    template_name = 'pages/searchResult.html'

    def get(self, request, *args, **kwargs):
        searched_game = request.GET.get('searched', '')
        category = request.GET.get('category', None)
        if category:
            categories = Games.objects.values_list('category', flat=True).distinct()
            filtered_games = Games.objects.filter(category=category)
        else:
            return SearchView.as_view()(request)
        return render(request, self.template_name, {
            'searched': searched_game,
            'games': filtered_games,
            'categories': categories,
        })
