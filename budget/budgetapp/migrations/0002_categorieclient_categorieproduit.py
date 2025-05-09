# Generated by Django 5.2 on 2025-04-24 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgetapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategorieClient',
            fields=[
                ('idClient', models.IntegerField(primary_key=True, serialize=False)),
                ('Libelle', models.CharField(max_length=30)),
                ('Description', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'categorie_client',
            },
        ),
        migrations.CreateModel(
            name='CategorieProduit',
            fields=[
                ('idCategorie', models.IntegerField(primary_key=True, serialize=False)),
                ('Libelle', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'categorie_produit',
            },
        ),
    ]
