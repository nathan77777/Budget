import csv


from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse

from django.contrib import messages
from django.shortcuts import redirect, render


from .models import Departements, Previsions, Realisations, Categories
from .services.Checker import Checker
from .services.form import LibelleForm
from .utils.Utilities import dept_budget

from xhtml2pdf import pisa


# Create your views here.
def login(request):
    return render(request, 'login.html')


def treatment_login(request):
    if request.method == "POST":
        emp_no = request.POST['emp_no']
        emp = Checker.login(emp_no)

        if not emp:
            return render(request, 'login.html', {'error': 'Employee not found'})

        role = Checker.get_role(emp['empno'])

        request.session['employee'] = emp
        request.session['role'] = {'execute': bool(role.executer), 'write': bool(role.writer),
                                   'read': bool(role.reader)}

        return render(request, 'home.html', {'emp': emp, })


def dept_manager(request):
    emp = request.session.get('employee')
    role = request.session.get('role')
    if role['execute']:
        dept = Departements.objects.all()
    else:
        dept = Departements.objects.filter(deptno=emp['deptno'])
    data = [{'dept_no': d.deptno, 'name_dept': d.name_dept} for d in dept]
    return render(request, 'dept_list.html', {'dept_list': data})


def get_list(request, deptno, month, year, type_categorie, table_type):
    if int(table_type) == 1:
        data = Checker.get_previsions_by_type(deptno, month, year, type_categorie)

    else:
        data = Checker.get_realisations_by_type(deptno, month, year, type_categorie)

    context = {
        'table_type': table_type,
        'table': data,
        'deptno': deptno,
        'year': year,
        'type_categorie': type_categorie,
    }
    return render(request, 'listing.html', context)


def find_update_element(request, element_id, table_id):
    if table_id == 1:
        table = 'Previsions'
        element = Previsions.objects.filter(id_prevision=element_id).first()
    else:
        table = 'Realisations'
        element = Realisations.objects.filter(id_realisation=element_id).first()
    data = {'date_operation': element.date_operation, 'montant': element.montant, 'libelle': element.libelle}

    return render(request, 'update_element.html',
                  {'data': data, 'table_name': table, 'element_id': element_id, 'table_id': table_id})


def submit_update(request):
    if request.method == "POST":
        element_id = request.POST['element_id']
        table_id = request.POST['table_id']
        date = request.POST['date_operation']
        montant = request.POST['montant']
        libelle = request.POST['libelle']

        if table_id == 1:
            element = Previsions.objects.filter(id_prevision=element_id)
        else:
            element = Realisations.objects.filter(id_realisation=element_id)

        roles = request.session.get('role')

        if roles['execute']:
            element.update(
                montant=montant,
                libelle=libelle,
                date_operation=date,
                isValid=True
            )
            message = 'Successfully Updated'
        else:
            element.update(
                montant=montant,
                libelle=libelle,
                date_operation=date,
                isValid=False
            )
            message = 'Waiting for the execute to accept.'

        return render(request, 'update_element.html', {'message': message})


def budget_form(request):
    # Cette vue affiche simplement le formulaire
    return render(request, 'budget_form.html')


def res_budget(request, dept_no, year):
    # dept_no = request.GET.get('dept_no')
    # year = request.GET.get('year')
    # Assure-toi de convertir en entier si nécessaire
    try:
        dept_no = int(dept_no)
        year = int(year)
    except (ValueError, TypeError):
        # Gérer l'erreur ou rediriger vers le formulaire avec un message d'erreur
        return render(request, 'budget_form.html', {'error': 'Veuillez saisir des valeurs numériques valides.'})

    budget = dept_budget(dept_no, year)
    return render(request, 'budget.html', {'budget': budget, 'dept_no': dept_no, 'year': year})


def insert_libelle(request):
    if request.method == "POST":
        form = LibelleForm(request.POST)
        if form.is_valid():
            type_libelle = form.cleaned_data["type_libelle"]
            id_category = Categories.objects.get(id_category=form.cleaned_data["id_category"])
            libelle = form.cleaned_data["libelle"]
            montant = form.cleaned_data["montant"]
            date_operation = form.cleaned_data["date_operation"]

            if type_libelle == "prevision":
                Previsions.objects.create(
                    id_category=id_category,
                    libelle=libelle,
                    montant=montant,
                    date_operation=date_operation,
                    isValid=False
                )
            else:
                Realisations.objects.create(
                    id_category=id_category,
                    libelle=libelle,
                    montant=montant,
                    date_operation=date_operation,
                    isValid=False
                )

            return redirect('insert_libelle')  # Redirection après succès

    else:
        form = LibelleForm()

    return render(request, 'insert_libelle.html', {'form': form})





def get_waiting_list(request, deptno):
    recette_previsions_waiting = Checker.get_non_previsions_by_type(deptno, 1)
    expense_previsions_waiting = Checker.get_non_previsions_by_type(deptno, 0)
    recette_realisations_waiting = Checker.get_non_realisations_by_type(deptno, 1)
    expense_realisations_waiting = Checker.get_non_realisations_by_type(deptno, 0)

    context = {
        'deptno': deptno,
        'recette_previsions_waiting': recette_previsions_waiting,
        'expense_previsions_waiting': expense_previsions_waiting,
        'recette_realisations_waiting': recette_realisations_waiting,
        'expense_realisations_waiting': expense_realisations_waiting,
    }
    return render(request, 'waiting.html', context)


def accept(request, table_id, element_id):
    # Récupérer l'élément concerné en fonction de table_id
    if table_id == "1":
        spec_element = Previsions.objects.filter(id_prevision=element_id)
    else:
        spec_element = Realisations.objects.filter(id_realisation=element_id)

    # Mettre à jour l'élément pour qu'il soit validé
    spec_element.update(isValid=True)

    # Ajouter le message de succès
    messages.success(request, 'Successfully Accepted')

    # Récupérer le deptno à partir de l'élément mis à jour (en supposant que l'élément possède un attribut deptno)
    deptno = spec_element.first().deptno if spec_element.exists() else None

    # Rediriger vers la vue get_waiting_list en passant le deptno
    return redirect(reverse('waiting', kwargs={'deptno': deptno.deptno}))


def budget_pdf_view(request, dept_no, year):
    # Récupérer les données du budget en appelant dept_budget
    budgets = dept_budget(dept_no, year)

    # Charger le fichier HTML avec le bon contexte
    html_string = render_to_string('budget.html', {
        "dept_no": dept_no,
        "year": year,
        "budget": budgets  # Passer le budget au template
    })

    # Création de la réponse en PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="budget.pdf"'

    # Génération du PDF avec xhtml2pdf
    pisa_status = pisa.CreatePDF(html_string, dest=response)

    # Vérifier si une erreur s'est produite
    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    return response


def export_budget_csv(request):
    # Récupérer les paramètres dept_no et year depuis la requête GET
    dept_no = request.GET.get('dept_no')
    year = request.GET.get('year')

    if not dept_no or not year:
        return HttpResponse("Paramètres manquants", status=400)

    # Récupérer les données du budget
    budgets = dept_budget(dept_no, year)

    # Créer une réponse avec le type MIME pour un fichier CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="budget.csv"'

    # Créer l'écrivain CSV
    writer = csv.writer(response)

    # Écrire l'en-tête (titres de colonnes)
    writer.writerow(['Mois', 'Solde Début', 'Prévisions Dépenses', 'Prévisions Recettes',
                     'Réalisations Dépenses', 'Réalisations Recettes',
                     'Marge Dépenses', 'Marge Recettes', 'Solde Final'])

    # Remplir les données ligne par ligne
    for mois in budgets:
        writer.writerow([
            mois['mois'], mois['solde_debut'],
            mois['previsions']['depenses'], mois['previsions']['recettes'],
            mois['realisations']['depenses'], mois['realisations']['recettes'],
            mois['marge']['depenses'], mois['marge']['recettes'],
            mois['soldefin']
        ])

    return response



def disconnect(request):
    request.session.flush()
    return render(request, 'login.html')
