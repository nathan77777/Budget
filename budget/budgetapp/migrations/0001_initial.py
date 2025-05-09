# Generated by Django 5.2 on 2025-04-24 09:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id_category', models.AutoField(primary_key=True, serialize=False)),
                ('type_categorie', models.IntegerField(choices=[(0, 'Depense'), (1, 'Recette')])),
                ('descriptions', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='CRM',
            fields=[
                ('idCRM', models.AutoField(primary_key=True, serialize=False)),
                ('idClient', models.IntegerField()),
                ('idProduct', models.IntegerField()),
                ('dateCRM', models.DateField(blank=True, null=True)),
                ('libelle', models.CharField(max_length=50)),
                ('montant', models.FloatField(blank=True, null=True)),
                ('isValid', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'CRM',
            },
        ),
        migrations.CreateModel(
            name='Departements',
            fields=[
                ('deptno', models.AutoField(primary_key=True, serialize=False)),
                ('name_dept', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'Departements',
            },
        ),
        migrations.CreateModel(
            name='Roles',
            fields=[
                ('deptno', models.AutoField(primary_key=True, serialize=False)),
                ('executer', models.BooleanField(default=False)),
                ('writer', models.BooleanField(default=False)),
                ('reader', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Roles',
            },
        ),
        migrations.CreateModel(
            name='Employes',
            fields=[
                ('empno', models.AutoField(primary_key=True, serialize=False)),
                ('name_emp', models.CharField(max_length=50)),
                ('deptno', models.ForeignKey(db_column='deptno', default=1, on_delete=django.db.models.deletion.CASCADE, to='budgetapp.departements')),
            ],
            options={
                'db_table': 'Employes',
            },
        ),
        migrations.CreateModel(
            name='Previsions',
            fields=[
                ('isValid', models.BooleanField(default=False)),
                ('id_prevision', models.AutoField(primary_key=True, serialize=False)),
                ('libelle', models.CharField(max_length=100)),
                ('date_operation', models.DateField()),
                ('montant', models.FloatField()),
                ('deptno', models.ForeignKey(db_column='deptno', default=1, on_delete=django.db.models.deletion.CASCADE, to='budgetapp.departements')),
                ('id_category', models.ForeignKey(db_column='idCategory', on_delete=django.db.models.deletion.CASCADE, to='budgetapp.categories')),
            ],
            options={
                'db_table': 'Previsions',
            },
        ),
        migrations.CreateModel(
            name='Realisations',
            fields=[
                ('isValid', models.BooleanField(default=False)),
                ('id_realisation', models.AutoField(primary_key=True, serialize=False)),
                ('libelle', models.CharField(max_length=100)),
                ('date_operation', models.DateField()),
                ('montant', models.FloatField()),
                ('deptno', models.ForeignKey(db_column='deptno', default=1, on_delete=django.db.models.deletion.CASCADE, to='budgetapp.departements')),
                ('id_category', models.ForeignKey(db_column='idCategory', on_delete=django.db.models.deletion.CASCADE, to='budgetapp.categories')),
            ],
            options={
                'db_table': 'Realisations',
            },
        ),
        migrations.CreateModel(
            name='SoldeDebut',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anne', models.IntegerField()),
                ('montant', models.FloatField()),
                ('id_departement', models.ForeignKey(db_column='idDepartement', on_delete=django.db.models.deletion.CASCADE, to='budgetapp.departements')),
            ],
            options={
                'db_table': 'soldeDebut',
            },
        ),
    ]
