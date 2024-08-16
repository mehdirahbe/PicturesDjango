from django import forms

class SearchForm(forms.Form):
    search_term = forms.CharField(label='Mot à chercher', max_length=100)
