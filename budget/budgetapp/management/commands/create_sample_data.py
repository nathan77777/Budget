from django.core.management.base import BaseCommand
from datetime import date, timedelta
import random
from budgetapp.models import Departements, Employes, Roles, Categories, Previsions, Realisations, SoldeDebut

class Command(BaseCommand):
    help = 'Populate database with sample data for Budget application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Vider toutes les tables pour éviter les doublons
        self.stdout.write('Clearing existing data...')
        SoldeDebut.objects.all().delete()
        Previsions.objects.all().delete()
        Realisations.objects.all().delete()
        Categories.objects.all().delete()
        Roles.objects.all().delete()
        Employes.objects.all().delete()
        Departements.objects.all().delete()
        
        # Créer les départements
        self.stdout.write('Creating Departements...')
        departments = [
            'Finance',
            'Ressources Humaines',
            'Marketing',
            'Informatique',
            'Juridique',
            'Recherche & Développement',
            'Commercial',
            'Production'
        ]
        
        dept_objects = []
        for dept_name in departments:
            dept = Departements.objects.create(name_dept=dept_name)
            dept_objects.append(dept)
            self.stdout.write(f'Created department: {dept_name}')
        
        # Créer les employés
        self.stdout.write('Creating Employes...')
        employees = [
            'Jean Dupont',
            'Marie Martin',
            'Sophie Dubois',
            'Thomas Bernard',
            'Camille Lambert',
            'Nicolas Petit',
            'Julie Lefebvre',
            'Alexandre Moreau',
            'Émilie Girard',
            'Antoine Rousseau',
            'Laura Richard',
            'David Simon',
            'Chloé Leroy',
            'Julien Morel',
            'Aurélie Fournier'
        ]
        
        for emp_name in employees:
            emp = Employes.objects.create(name_emp=emp_name)
            self.stdout.write(f'Created employee: {emp_name}')
        
        # Créer les rôles pour chaque département
        self.stdout.write('Creating Roles...')
        for dept in dept_objects:
            Roles.objects.create(
                deptno=dept.deptno,
                executer=random.choice([True, False]),
                writer=random.choice([True, False]),
                reader=True  # Tous ont au moins les droits de lecture
            )
            self.stdout.write(f'Created roles for department: {dept.name_dept}')
        
        # Créer les catégories
        self.stdout.write('Creating Categories...')
        expense_categories = [
            'Salaires',
            'Fournitures de bureau',
            'Loyer',
            'Électricité',
            'Télécommunications',
            'Déplacements',
            'Formation',
            'Publicité',
            'Assurances',
            'Maintenance'
        ]
        
        income_categories = [
            'Ventes de produits',
            'Services aux clients',
            'Subventions',
            'Intérêts',
            'Licences',
            'Royalties',
            'Événements',
            'Partenariats'
        ]
        
        cat_objects = []
        # Type 0 = Dépenses
        for desc in expense_categories:
            cat = Categories.objects.create(type_categorie=0, descriptions=desc)
            cat_objects.append(cat)
            self.stdout.write(f'Created expense category: {desc}')
        
        # Type 1 = Revenus
        for desc in income_categories:
            cat = Categories.objects.create(type_categorie=1, descriptions=desc)
            cat_objects.append(cat)
            self.stdout.write(f'Created income category: {desc}')
        
        # Créer les prévisions
        self.stdout.write('Creating Previsions...')
        start_date = date(2025, 1, 1)
        
        for i in range(50):
            random_date = start_date + timedelta(days=random.randint(0, 365))
            random_category = random.choice(cat_objects)
            
            if random_category.type_categorie == 0:  # Dépense
                amount = -random.uniform(100, 5000)
            else:  # Revenu
                amount = random.uniform(500, 10000)
                
            Previsions.objects.create(
                libelle=f"Prévision {i+1} - {random_category.descriptions}",
                id_category=random_category,
                date_operation=random_date,
                montant=round(amount, 2)
            )
            self.stdout.write(f'Created prevision {i+1} for {random_category.descriptions}')
        
        # Créer les réalisations
        self.stdout.write('Creating Realisations...')
        for i in range(40):
            random_date = start_date + timedelta(days=random.randint(0, 300))
            random_category = random.choice(cat_objects)
            
            if random_category.type_categorie == 0:  # Dépense
                amount = -random.uniform(100, 5000)
            else:  # Revenu
                amount = random.uniform(500, 10000)
                
            Realisations.objects.create(
                libelle=f"Réalisation {i+1} - {random_category.descriptions}",
                id_category=random_category,
                date_operation=random_date,
                montant=round(amount, 2)
            )
            self.stdout.write(f'Created realisation {i+1} for {random_category.descriptions}')
        
        # Créer les soldes de début
        self.stdout.write('Creating SoldeDebut...')
        years = [2024, 2025]
        
        for dept in dept_objects:
            for year in years:
                SoldeDebut.objects.create(
                    id_departement=dept,
                    anne=year,
                    montant=round(random.uniform(10000, 100000), 2)
                )
                self.stdout.write(f'Created solde debut for department {dept.name_dept}, year {year}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))