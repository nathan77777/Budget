from django.db.models.expressions import result

from budgetapp.models import Employes, Roles, Previsions, Realisations


class Checker:

    @staticmethod
    def login(empno:int):
        res = None
        emp = Employes.objects.filter(empno=empno).first()
        if emp:
            res = {'empno': emp.empno, 'deptno':emp.deptno.deptno, 'name_emp': emp.name_emp}
        return res


    @staticmethod
    def get_role(empno:int):
        emp = Employes.objects.filter(empno=empno).first()
        if emp:
            dept = emp.deptno
            role = Roles.objects.filter(deptno=dept.deptno).first()
            return role
        return None


    @staticmethod
    def get_previsions_by_type(deptno, month, year, type_categorie):
        # Récupérer uniquement les prévisions du type demandé (0 = dépenses, 1 = recettes)
        previsions = Previsions.objects.filter(
            deptno=deptno,
            date_operation__month=month,
            date_operation__year=year,
            id_category__type_categorie=type_categorie,
            isValid=True  # On filtre uniquement les prévisions validées
        ).select_related('id_category')  # Précharge les catégories pour optimiser la requête
        return previsions



    @staticmethod
    def get_realisations_by_type(deptno, month, year, type_categorie):
        # Récupérer uniquement les prévisions du type demandé (0 = dépenses, 1 = recettes)
        realisations = Realisations.objects.filter(
            deptno=deptno,
            date_operation__month=month,
            date_operation__year=year,
            id_category__type_categorie=type_categorie,
            isValid=True  # On filtre uniquement les prévisions validées
        ).select_related('id_category')  # Précharge les catégories pour optimiser la requête
        return realisations


    @staticmethod
    def get_non_previsions_by_type(deptno, type_categorie):
        # Récupérer uniquement les prévisions du type demandé (0 = dépenses, 1 = recettes)
        previsions = Previsions.objects.filter(
            deptno=deptno,
            id_category__type_categorie=type_categorie,
            isValid=False  # On filtre uniquement les prévisions validées
        ).select_related('id_category')  # Précharge les catégories pour optimiser la requête
        return previsions



    @staticmethod
    def get_non_realisations_by_type(deptno, type_categorie):
        # Récupérer uniquement les prévisions du type demandé (0 = dépenses, 1 = recettes)
        realisations = Realisations.objects.filter(
            deptno=deptno,
            id_category__type_categorie=type_categorie,

            isValid=False  # On filtre uniquement les prévisions validées
        ).select_related('id_category')  # Précharge les catégories pour optimiser la requête
        return realisations