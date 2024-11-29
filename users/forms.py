
from django import forms
class registerForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=50)
    password = forms.CharField(label='Senha', max_length=50)
    email = forms.EmailField(label='Email', max_length=254)
    phone = forms.CharField(label='Telefone', max_length=14)        