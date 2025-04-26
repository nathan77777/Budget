from django.db import models
from django.db.models import Sum


class CRMManager(models.Manager):
    def get_crm_by_month_year(self, month, year):
        queryset = self.filter(dateCRM__month=month, dateCRM__year=year)
        total = queryset.aggregate(total_montant=Sum('montant'))['total_montant'] or 0.0
        return queryset, total


# utilisation:
# from myapp.models import CRM
#
# # Supposons que tu veux récupérer les CRM de mars 2025 :
# mois = 3
# annee = 2025
# liste_crm, total_montant = CRM.objects.get_by_month_year(mois, annee)
#
# print("Total montant en mars 2025:", total_montant)
# for crm in liste_crm:
#     print(f"CRM {crm.idCRM} - Montant : {crm.montant}")
