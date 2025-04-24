from django import forms
from budgetapp.models import Previsions, Realisations, Categories

class LibelleForm(forms.Form):
    TYPE_CHOICES = [
        ('prevision', 'Prévision'),
        ('realisation', 'Réalisation'),
    ]

    type_libelle = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label="Type de Libellé",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    libelle = forms.CharField(
        max_length=100,
        label="Description",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    montant = forms.FloatField(
        label="Montant",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    date_operation = forms.DateField(
        label="Date de l'opération",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categories = Categories.objects.all()
        options = {
            'Dépenses': [],
            'Recettes': []
        }

        for category in categories:
            if category.type_categorie == 0:
                options['Dépenses'].append((category.id_category, category.descriptions))
            else:
                options['Recettes'].append((category.id_category, category.descriptions))

        self.fields['id_category'] = forms.ChoiceField(
            choices=[
                ('', 'Choisir une catégorie'),
                ('Dépenses', options['Dépenses']),
                ('Recettes', options['Recettes'])
            ],
            label="Catégorie",
            widget=forms.Select(attrs={'class': 'form-control'})
        )
