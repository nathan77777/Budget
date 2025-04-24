from django.db import models

# Create your models here.
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
    montant = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'CRM'


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


class SoldeDebut(models.Model):
    id_departement = models.ForeignKey(Departements, on_delete=models.CASCADE, db_column='idDepartement')
    anne = models.IntegerField()
    montant = models.FloatField()

    def __str__(self):
        return f"Solde {self.anne} - Département {self.id_departement}"

    class Meta:
        db_table = 'soldeDebut'