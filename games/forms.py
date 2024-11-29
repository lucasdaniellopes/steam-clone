from django import forms
from .models import Games

class GameForm(forms.ModelForm):
    class Meta:
        model = Games
        fields = ['name', 'category', 'description', 'price', 'img_cover', 'img_1', 'img_2', 'img_3', 'trailer', 'requirements']

        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
        }