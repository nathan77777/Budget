from django import forms
from budgetapp.models import Previsions, Realisations, Categories, CategorieProduit, CategorieClient

class LibelleForm(forms.Form):
    TYPE_CHOICES = [
        ('prevision', 'Prévision'),
        ('realisation', 'Réalisation'),
        ('crm', 'CRM'),
    ]

    type_libelle = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label="Type de Libellé",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_type_libelle'})
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

        # ==== Catégories dynamiques : Produits ====
        produit_choices = [('', 'Choisir une catégorie de produit')] + [
            (str(cat.idCategorie), cat.Libelle) for cat in CategorieProduit.objects.all()
        ]
        self.fields['id_product_category'] = forms.ChoiceField(
            choices=produit_choices,
            label="Catégorie produits",
            required=False,
            widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_product_category'})
        )

        # ==== Catégories dynamiques : Clients ====
        client_choices = [('', 'Choisir une catégorie de client')] + [
            (str(cat.idClient), cat.Libelle) for cat in CategorieClient.objects.all()
        ]
        self.fields['id_client_category'] = forms.ChoiceField(
            choices=client_choices,
            label="Catégorie client",
            required=False,
            widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_client_category'})
        )

        # ==== Catégories standards Dépenses/Recettes ====
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
            required=False,
            widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_category'})
        )

    def clean(self):
        cleaned_data = super().clean()
        type_libelle = cleaned_data.get("type_libelle")

        # Validation conditionnelle selon le type de libellé
        if type_libelle == 'crm':
            # Pour CRM, vérifier les catégories produit et client
            if not cleaned_data.get("id_product_category"):
                self.add_error('id_product_category', "Ce champ est obligatoire pour le type CRM.")
            if not cleaned_data.get("id_client_category"):
                self.add_error('id_client_category', "Ce champ est obligatoire pour le type CRM.")
        else:
            # Pour les autres types, vérifier la catégorie standard
            if not cleaned_data.get("id_category"):
                self.add_error('id_category', "Ce champ est obligatoire.")

        return cleaned_data
