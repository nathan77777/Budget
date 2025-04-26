from django.db.models import Sum

from budgetapp.models import SoldeDebut, Previsions, Realisations, CRM


# Ato koa
def dept_budget(dept_no: int, year: int) -> list[dict]:
    # Récupérer le solde initial pour le département et l'année donnés
    solde_initial_qs = SoldeDebut.objects.filter(anne=year, id_departement=dept_no)
    solde_initial = solde_initial_qs.first().montant if solde_initial_qs.exists() else 0

    budgets = []
    solde_debut = solde_initial

    # Pour chaque mois (de 1 à 12)
    for month in range(1, 13):
        # Prévisions : on filtre sur l'année, le mois, le département et isValid True.
        prev_depenses = (
            Previsions.objects.filter(
                date_operation__year=year,
                date_operation__month=month,
                deptno_id=dept_no,
                isValid=True,
                id_category__type_categorie=0  # 0 pour Dépense
            )
            .aggregate(total=Sum('montant'))['total'] or 0
        )
        prev_recettes = (
            Previsions.objects.filter(
                date_operation__year=year,
                date_operation__month=month,
                deptno_id=dept_no,
                isValid=True,
                id_category__type_categorie=1  # 1 pour Recette
            )
            .aggregate(total=Sum('montant'))['total'] or 0
        )
        prev_benefice = prev_recettes - prev_depenses

        # Réalisations : même logique que pour les Prévisions

        var = CRM.get_total_valid_by_month_year(month, year)

        print(f"month: {month}, year: {year}, value: {var}")

        real_depenses = (
            Realisations.objects.filter(
                date_operation__year=year,
                date_operation__month=month,
                deptno_id=dept_no,
                isValid=True,
                id_category__type_categorie=0  # Dépense
            )

            .aggregate(total=Sum('montant'))['total'] or 0
        ) + var

        real_recettes = (
            Realisations.objects.filter(
                date_operation__year=year,
                date_operation__month=month,
                deptno_id=dept_no,
                isValid=True,
                id_category__type_categorie=1  # Recette
            )
            .aggregate(total=Sum('montant'))['total'] or 0
        )
        real_benefice = real_recettes - real_depenses

        # Marge : différence entre les prévisions et les réalisations pour dépenses, recettes et bénéfice
        marge = {
            "depenses": prev_depenses - real_depenses,
            "recettes": prev_recettes - real_recettes,
            "benefice": prev_benefice - real_benefice,
        }

        # Calcul du solde final (soldefin) pour le mois courant
        if real_benefice != 0:
            soldefin = solde_debut + real_benefice
        else:
            soldefin = solde_debut + prev_benefice

        # Constitution du dictionnaire pour le mois courant
        mois_budget = {
            "solde_debut": solde_debut,
            "previsions": {
                "depenses": prev_depenses,
                "recettes": prev_recettes,
                "benefice": prev_benefice,
            },
            "realisations": {
                "depenses": real_depenses,
                "recettes": real_recettes,
                "benefice": real_benefice,
            },
            "marge": marge,
            "soldefin": soldefin,
            # Optionnel : ajouter le numéro du mois pour repérage
            "mois": month
        }

        budgets.append(mois_budget)
        # Pour le mois suivant, le solde de début est le soldefin courant
        solde_debut = soldefin

    return budgets

