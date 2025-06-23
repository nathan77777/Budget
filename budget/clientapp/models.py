from django.db import models
from django.db.models import Sum

# Create your models here.


class RecetteCRM(models.Model):
    idRecette = models.AutoField(primary_key=True)
    mois = models.IntegerField()
    annee = models.IntegerField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'recette_crm'

    def __str__(self):
        return f"{self.mois}/{self.annee} - {self.montant} €"


class CategorieClient(models.Model):
    idClient = models.IntegerField(primary_key=True)
    Libelle = models.CharField(max_length=30)
    Description = models.CharField(max_length=50)

    def __str__(self):
        return self.Libelle
    class Meta:
        db_table = 'categorie_client'


class CategorieProduit(models.Model):
    idCategorie = models.IntegerField(primary_key=True)
    Libelle = models.CharField(max_length=20)

    def __str__(self):
        return self.Libelle
    class Meta:
        db_table = 'categorie_produit'


class Departements(models.Model):
    deptno = models.AutoField(primary_key=True)
    name_dept = models.CharField(max_length=50)

    def __str__(self):
        return self.name_dept

    class Meta:
        db_table = 'Departements'


class Employes(models.Model):
    empno = models.AutoField(primary_key=True)
    name_emp = models.CharField(max_length=50)
    deptno = models.ForeignKey(Departements, on_delete=models.CASCADE, db_column='deptno', default=1)

    def __str__(self):
        return self.name_emp

    class Meta:
        db_table = 'Employes'



class CRM(models.Model):
    idCRM = models.AutoField(primary_key=True)
    idClient = models.IntegerField()
    idProduct = models.IntegerField()
    dateCRM = models.DateField(null=True, blank=True)
    libelle = models.CharField(max_length=50)
    descComportement = models.CharField(max_length=100, default="Comportement")
    montant = models.FloatField(null=True, blank=True)
    isValid = models.BooleanField(default=False)

    class Meta:
        db_table = 'CRM'

    @staticmethod
    def get_crms_by_month_year(month, year):
        """
        Retourne la liste des CRM pour un mois et une année donnés.

        Args:
            month (int): Le mois (1-12)
                year (int): L'année (ex: 2025)

        Returns:
            QuerySet: Liste des CRM pour le mois et l'année spécifiés
        """
        return CRM.objects.filter(
            dateCRM__month=month,
            dateCRM__year=year,
            isValid=True
        )

    @staticmethod
    def get_total_valid_by_month_year(month, year):
        """
        Calcule le total des montants des CRM pour un mois et une année donnés.

        Args:
            month (int): Le mois (1-12)
            year (int): L'année (ex: 2025)

        Returns:
            float: Le total des montants ou 0 si aucun CRM trouvé
        """
        result = CRM.objects.filter(
            dateCRM__month=month,
            dateCRM__year=year,
            isValid=True
        ).aggregate(total=Sum('montant'))

        return result['total'] or 0.0


    @staticmethod
    def get_all_invalid():
        return CRM.objects.filter(
            isValid=False
        )



class Roles(models.Model):
    deptno = models.AutoField(primary_key=True)
    executer = models.BooleanField(default=False)
    writer = models.BooleanField(default=False)
    reader = models.BooleanField(default=False)

    def __str__(self):
        return f"Roles pour département {self.deptno}"

    class Meta:
        db_table = 'Roles'


class Categories(models.Model):
    TYPE_CHOICES = (
        (0, 'Depense'),
        (1, 'Recette'),
    )
    
    id_category = models.AutoField(primary_key=True)
    type_categorie = models.IntegerField(choices=TYPE_CHOICES)
    descriptions = models.CharField(max_length=100)

    def __str__(self):
        return self.descriptions

    class Meta:
        db_table = 'Categories'


class Previsions(models.Model):
    deptno = models.ForeignKey(Departements, on_delete=models.CASCADE, db_column='deptno', default=1)
    isValid = models.BooleanField(default=False)
    id_prevision = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=100)
    id_category = models.ForeignKey(Categories, on_delete=models.CASCADE, db_column='idCategory')
    date_operation = models.DateField()
    montant = models.FloatField()

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'Previsions'


class Realisations(models.Model):
    deptno = models.ForeignKey(Departements, on_delete=models.CASCADE, db_column='deptno', default=1)
    isValid = models.BooleanField(default=False)
    id_realisation = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=100)
    id_category = models.ForeignKey(Categories, on_delete=models.CASCADE, db_column='idCategory')
    date_operation = models.DateField()
    montant = models.FloatField()

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'Realisations'


    @staticmethod
    def get_total_valid_by_month_year(deptno, month, year):
        """
        Calcule le total des montants des realisations pour un mois et une année donnés.

        Args:
            month (int): Le mois (1-12)
            year (int): L'année (ex: 2025)

        Returns:
            float: Le total des montants ou 0 si aucun CRM trouvé
        """
        result = Realisations.objects.filter(
            deptno=deptno,
            id_category=0,
            date_operation__month=month,
            date_operation__year=year,
            isValid=True
        ).aggregate(total=Sum('montant'))

        return result['total'] or 0.0


class SoldeDebut(models.Model):
    id_departement = models.ForeignKey(Departements, on_delete=models.CASCADE, db_column='idDepartement')
    anne = models.IntegerField()
    montant = models.FloatField()

    def __str__(self):
        return f"Solde {self.anne} - Département {self.id_departement}"

    class Meta:
        db_table = 'soldeDebut'
        
        
        
    # -------------------------
    
    
class Client(models.Model):
    nom = models.CharField(max_length=20)
    prenoms = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nom} {self.prenoms}"


class CategorieTicket(models.Model):
    descriptions = models.CharField(max_length=20)

    def __str__(self):
        return self.descriptions


class Priorite(models.Model):
    descriptions = models.CharField(max_length=20)

    def __str__(self):
        return self.descriptions


class Ticket(models.Model):
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    priorite = models.ForeignKey(Priorite, on_delete=models.CASCADE)
    categorie_ticket = models.ForeignKey(CategorieTicket, on_delete=models.CASCADE)
    objet = models.CharField(max_length=20)
    date_creation = models.DateTimeField()

    def __str__(self):
        return f"Ticket {self.id} - {self.objet}"


class StatutTicket(models.Model):
    descriptions = models.CharField(max_length=20)

    def __str__(self):
        return self.descriptions


class HistoriqueStatutTicket(models.Model):
    id_ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    id_statuts = models.ForeignKey(StatutTicket, on_delete=models.CASCADE)

    def __str__(self):
        return f"HistoriqueStatutTicket: Ticket {self.id_ticket_id} - Statut {self.id_statuts_id}"


class HistoriqueAffectationTicket(models.Model):
    id_ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    id_employee = models.ForeignKey(Employes, on_delete=models.SET_NULL, null=True, related_name='employee_assignments')
    id_department = models.ForeignKey(Departements, on_delete=models.SET_NULL, null=True)
    id_attributeur = models.ForeignKey(Employes, on_delete=models.CASCADE, related_name='assigned_by')

    def __str__(self):
        return f"Affectation de Ticket {self.id_ticket_id}"