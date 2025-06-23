import csv
import json

from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.template.loader import render_to_string
from django.urls import reverse

from django.contrib import messages
from django.shortcuts import redirect, render


from .models import Departements, Previsions, Realisations, Categories, CRM, CategorieProduit, CategorieClient, \
    RecetteCRM
from .services.Checker import Checker
from .services.form import LibelleForm
from .utils.Utilities import dept_budget

from xhtml2pdf import pisa

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from io import BytesIO
import re


# Create your views here.
def login(request):
    return render(request, 'login.html')

def home(request):
    emp = request.session['employee']
    roles = request.session['role']

    return render(request, 'home.html', {'emp': emp, 'role': roles})

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


def page_categorie_et_comportement(request):
    produits = CategorieProduit.objects.all()
    clients = CategorieClient.objects.all()
    comportements = CRM.objects.all()


    context = {
        'produits': produits,
        'clients': clients,
        'comportements': comportements,
    }

    return render(request, 'categorie_et_comportement.html', context)


def graphe_realisations(request):
    # Données des réalisations
    real_data = (
        Realisations.objects.filter(isValid=0)
        .annotate(mois=ExtractMonth('date_operation'))
        .values('mois')
        .annotate(total=Sum('montant'))
        .order_by('mois')
    )

    realisations_par_mois = [0] * 12
    for item in real_data:
        realisations_par_mois[item['mois'] - 1] = float(item['total'])

    # Données des recettes CRM (tu peux filtrer par année ici si tu veux)
    recette_data = (
        RecetteCRM.objects.values('mois')
        .annotate(total=Sum('montant'))
        .order_by('mois')
    )

    recettes_par_mois = [0] * 12
    for item in recette_data:
        recettes_par_mois[item['mois'] - 1] = float(item['total'])

    context = {
        'realisations': realisations_par_mois,
        'recettes': recettes_par_mois
    }
    return render(request, 'graphe.html', context)


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
    crm = None
    if int(table_type) == 1:
        data = Checker.get_previsions_by_type(deptno, month, year, type_categorie)

    else:
        data = Checker.get_realisations_by_type(deptno, month, year, type_categorie)
        crm = CRM.get_crms_by_month_year(month, year)

    context = {
        'table_type': table_type,
        'table': data,
        'crm_table': crm,
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
            libelle = form.cleaned_data["libelle"]
            montant = form.cleaned_data["montant"]
            date_operation = form.cleaned_data["date_operation"]

            if type_libelle == "crm":
                id_produit_category = form.cleaned_data["id_product_category"]
                id_client_category = form.cleaned_data["id_client_category"]
                comportement = form.cleaned_data["comportement_client"]
                is_valid = False

                roles = request.session.get('role')
                emp = request.session.get('employee')
                montant_crm = (CRM.get_total_valid_by_month_year(date_operation.month, date_operation.year)
                                + Realisations.get_total_valid_by_month_year(emp['deptno'], date_operation.month, date_operation.year))

                if roles['execute'] or montant_crm > montant:
                    is_valid = True


                CRM.objects.create(
                    idClient=id_client_category,
                    idProduct=id_produit_category,
                    dateCRM=date_operation,
                    montant=montant,
                    libelle=libelle,
                    isValid=is_valid,
                    descComportement=comportement
                )

            else:
                id_category = Categories.objects.get(id_category=form.cleaned_data["id_category"])
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
    crm = CRM.get_all_invalid()

    context = {
        'deptno': deptno,
        'recette_previsions_waiting': recette_previsions_waiting,
        'expense_previsions_waiting': expense_previsions_waiting,
        'recette_realisations_waiting': recette_realisations_waiting,
        'expense_realisations_waiting': expense_realisations_waiting,
        'crm': crm
    }
    return render(request, 'waiting.html', context)


def accept(request, table_id, element_id):
    # Récupérer l'élément concerné en fonction de table_id
    global deptno
    if table_id == "1":
        spec_element = Previsions.objects.filter(id_prevision=element_id)
    elif table_id == "2":
        spec_element = Realisations.objects.filter(id_realisation=element_id)
    else:
        spec_element = CRM.objects.filter(idCRM=element_id)

    # Mettre à jour l'élément pour qu'il soit validé
    spec_element.update(isValid=True)

    # Ajouter le message de succès
    messages.success(request, 'Successfully Accepted')

    if table_id == "1" or table_id == "2":

        # Récupérer le deptno à partir de l'élément mis à jour (en supposant que l'élément possède un attribut deptno)
        deptno = spec_element.first().deptno if spec_element.exists() else None

        # Rediriger vers la vue get_waiting_list en passant le deptno
        return redirect(reverse('waiting', kwargs={'deptno': deptno.deptno}))

    else:
        emp = request.session.get("employee")

        if emp:
            # Récupérer le deptno à partir de l'élément mis à jour (en supposant que l'élément possède un attribut deptno)
            deptno = emp['deptno']


        # Rediriger vers la vue get_waiting_list en passant le deptno
        return redirect(reverse('waiting', kwargs={'deptno': deptno}))




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


def render_to_pdf(template_src, context_dict=None):
    if context_dict is None:
        context_dict = {}
    result = BytesIO()
    pisa_status = pisa.CreatePDF(BytesIO(template_src.encode('utf-8')), dest=result)
    if not pisa_status.err:
        return result
    return None


@csrf_exempt  # Vous pouvez supprimer ceci si vous gérez le CSRF correctement
def export_pdf(request):
    if request.method == 'POST':
        try:
            # Récupérer l'image du graphique et les données
            chart_image = request.POST.get('chartImage')
            titre = request.POST.get('titre', 'Comparaison : Réalisations vs Recettes CRM')

            # Récupérer les données pour éventuellement ajouter un tableau
            try:
                realisations = json.loads(request.POST.get('realisations', '[]'))
                recettes = json.loads(request.POST.get('recettes', '[]'))
            except:
                realisations = []
                recettes = []

            # Nettoyer l'image base64
            if chart_image and chart_image.startswith('data:image'):
                # Extraire la partie base64 après la virgule
                chart_image = re.sub('^data:image/[^;]*;base64,', '', chart_image)

            # Générer le tableau de données
            table_rows = ''
            months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                      'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

            for i in range(min(len(months), len(realisations), len(recettes))):
                table_rows += f'''
                <tr>
                    <td>{months[i]}</td>
                    <td>{realisations[i]:,.2f} €</td>
                    <td>{recettes[i]:,.2f} €</td>
                </tr>
                '''

            # Créer le HTML pour le PDF
            html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{titre}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    .header {{ text-align: center; margin-bottom: 20px; }}
                    .chart-container {{ text-align: center; margin-bottom: 30px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
                    table, th, td {{ border: 1px solid #ddd; }}
                    th, td {{ padding: 8px; text-align: right; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    .footer {{ margin-top: 30px; text-align: center; font-size: 0.8em; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{titre}</h1>
                    <p>Généré le {timezone.now().strftime('%d/%m/%Y')}</p>
                </div>

                <div class="chart-container">
                    <img src="data:image/png;base64,{chart_image}" width="700">
                </div>

                <h2>Données détaillées</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Mois</th>
                            <th>Réalisations (€)</th>
                            <th>Recettes CRM (€)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>

                <div class="footer">
                    <p>Ce document est généré automatiquement et contient des informations confidentielles.</p>
                </div>
            </body>
            </html>
            '''

            # Générer le PDF
            pdf = render_to_pdf(html)
            if pdf:
                response = HttpResponse(pdf.getvalue(), content_type='application/pdf')
                filename = f"rapport_{timezone.now().strftime('%Y%m%d')}.pdf"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

            return HttpResponse("Erreur lors de la génération du PDF", status=500)

        except Exception as e:
            import traceback
            print(f"Erreur: {str(e)}")
            print(traceback.format_exc())
            return HttpResponse(f"Erreur: {str(e)}", status=500)

    return HttpResponse("Méthode non autorisée", status=405)

#------------------------------------------------------------------------------

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg
from .models import CRM, CategorieClient, CategorieProduit
from django.db import connection


def dashboard(request):
    """Vue principale du tableau de bord pour visualiser les comportements clients"""

    # Récupérer les stats générales
    client_categories = CategorieClient.objects.all()
    product_categories = CategorieProduit.objects.all()

    # Récupérer les 5 derniers comportements clients
    recent_behaviors = CRM.objects.filter(isValid=True).order_by('-dateCRM')[:5]

    # Nombre total de comportements clients par catégorie de client
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT cc.idClient, cc.Libelle, COUNT(crm.idCRM) as count
            FROM categorie_client cc
            LEFT JOIN CRM crm ON cc.idClient = crm.idClient
            WHERE crm.isValid = TRUE
            GROUP BY cc.idClient, cc.Libelle
            ORDER BY count DESC
        """)
        client_behavior_counts = cursor.fetchall()

    # Nombre total de comportements clients par catégorie de produit
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT cp.idCategorie, cp.Libelle, COUNT(crm.idCRM) as count
            FROM categorie_produit cp
            LEFT JOIN CRM crm ON cp.idCategorie = crm.idProduct
            WHERE crm.isValid = TRUE
            GROUP BY cp.idCategorie, cp.Libelle
            ORDER BY count DESC
        """)
        product_behavior_counts = cursor.fetchall()

    # Types de comportements les plus courants (basés sur le libelle CRM)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT libelle, COUNT(*) as count
            FROM CRM
            WHERE isValid = TRUE
            GROUP BY libelle
            ORDER BY count DESC
            LIMIT 5
        """)
        common_behaviors = cursor.fetchall()

    context = {
        'client_categories': client_categories,
        'product_categories': product_categories,
        'recent_behaviors': recent_behaviors,
        'client_behavior_counts': client_behavior_counts,
        'product_behavior_counts': product_behavior_counts,
        'common_behaviors': common_behaviors,
    }

    return render(request, 'dash/dashboard.html', context)


def client_category_detail(request, category_id):
    """Vue détaillée pour une catégorie client spécifique"""
    category = get_object_or_404(CategorieClient, idClient=category_id)

    # Récupérer les comportements pour cette catégorie client
    behaviors = CRM.objects.filter(idClient=category_id, isValid=True)

    # Regrouper par catégorie de produit
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT cp.idCategorie, cp.Libelle, COUNT(crm.idCRM) as count
            FROM categorie_produit cp
            JOIN CRM crm ON cp.idCategorie = crm.idProduct
            WHERE crm.idClient = %s AND crm.isValid = TRUE
            GROUP BY cp.idCategorie, cp.Libelle
            ORDER BY count DESC
        """, [category_id])
        product_distribution = cursor.fetchall()

    # Regrouper par type de comportement
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT libelle, COUNT(*) as count
            FROM CRM
            WHERE idClient = %s AND isValid = TRUE
            GROUP BY libelle
            ORDER BY count DESC
        """, [category_id])
        behavior_types = cursor.fetchall()

    context = {
        'category': category,
        'behaviors': behaviors,
        'product_distribution': product_distribution,
        'behavior_types': behavior_types,
    }

    return render(request, 'dash/client_category_detail.html', context)


def product_category_detail(request, category_id):
    """Vue détaillée pour une catégorie produit spécifique"""
    category = get_object_or_404(CategorieProduit, idCategorie=category_id)

    # Récupérer les comportements pour cette catégorie de produit
    behaviors = CRM.objects.filter(idProduct=category_id, isValid=True)

    # Regrouper par catégorie client
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT cc.idClient, cc.Libelle, COUNT(crm.idCRM) as count
            FROM categorie_client cc
            JOIN CRM crm ON cc.idClient = crm.idClient
            WHERE crm.idProduct = %s AND crm.isValid = TRUE
            GROUP BY cc.idClient, cc.Libelle
            ORDER BY count DESC
        """, [category_id])
        client_distribution = cursor.fetchall()

    # Regrouper par type de comportement
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT libelle, COUNT(*) as count
            FROM CRM
            WHERE idProduct = %s AND isValid = TRUE
            GROUP BY libelle
            ORDER BY count DESC
        """, [category_id])
        behavior_types = cursor.fetchall()

    context = {
        'category': category,
        'behaviors': behaviors,
        'client_distribution': client_distribution,
        'behavior_types': behavior_types,
    }

    return render(request, 'dash/product_category_detail.html', context)


def behavior_detail(request, crm_id):
    """Vue détaillée pour un comportement client spécifique"""
    behavior = get_object_or_404(CRM, idCRM=crm_id)

    # Récupérer la catégorie client
    try:
        client_category = CategorieClient.objects.get(idClient=behavior.idClient)
    except CategorieClient.DoesNotExist:
        client_category = None

    # Récupérer la catégorie produit
    try:
        product_category = CategorieProduit.objects.get(idCategorie=behavior.idProduct)
    except CategorieProduit.DoesNotExist:
        product_category = None

    # Comportements similaires (même catégorie client et produit)
    similar_behaviors = CRM.objects.filter(
        idClient=behavior.idClient,
        idProduct=behavior.idProduct,
        isValid=True
    ).exclude(idCRM=crm_id)[:5]

    context = {
        'behavior': behavior,
        'client_category': client_category,
        'product_category': product_category,
        'similar_behaviors': similar_behaviors,
    }

    return render(request, 'dash/behavior_detail.html', context)


def behavior_data_api(request):
    """API pour récupérer des données pour les graphiques JavaScript"""

    # Matrice des comportements par catégorie client/produit
    matrix_data = []

    client_categories = CategorieClient.objects.all()
    product_categories = CategorieProduit.objects.all()

    for client in client_categories:
        row = {
            'client_id': client.idClient,
            'client_name': client.Libelle,
            'products': []
        }

        for product in product_categories:
            # Compter les comportements pour cette combinaison client/produit
            count = CRM.objects.filter(
                idClient=client.idClient,
                idProduct=product.idCategorie,
                isValid=True
            ).count()

            # Identifier le comportement le plus courant
            most_common = CRM.objects.filter(
                idClient=client.idClient,
                idProduct=product.idCategorie,
                isValid=True
            ).values('libelle').annotate(count=Count('libelle')).order_by('-count').first()

            common_behavior = most_common['libelle'] if most_common else None

            row['products'].append({
                'product_id': product.idCategorie,
                'product_name': product.Libelle,
                'count': count,
                'common_behavior': common_behavior
            })

        matrix_data.append(row)

    return JsonResponse({'matrix_data': matrix_data})


# Dans views.py, ajoutez cette fonction pour gérer l'acceptation multiple
def accept_multiple(request, type, cat_type):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')

        if type == 1:  # Prévisions
            for item_id in selected_items:
                prevision = Previsions.objects.get(id_prevision=item_id)
                prevision.isValid = True
                prevision.save()

        elif type == 2:  # Réalisations
            for item_id in selected_items:
                realisation = Realisations.objects.get(id_realisation=item_id)
                realisation.isValid = True
                realisation.save()

        elif type == 3:  # CRM
            for item_id in selected_items:
                crm_item = CRM.objects.get(idCRM=item_id)
                crm_item.isValid = True
                crm_item.save()

        messages.success(request, f"{len(selected_items)} éléments ont été acceptés avec succès.")

    return redirect('waiting', deptno=request.session.get('deptno', 1))



import csv
import io
from django.contrib import messages
from django.shortcuts import render, redirect
from .services.form import UploadCSVForm


# def import_form(request):
#     return render(request, 'import_csv.html')


def import_csv_view(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            fichier = request.FILES['fichier_csv']
            try:
                fichier.read().decode('utf-8')
                messages.success(request, "Fichier CSV charge avec success ✅")
                # Tu peux traiter le contenu ici si tu veux
            except Exception as e:
                messages.error(request, f"Erreur lors de la lecture : {e}")
            return redirect('import')
    else:
        form = UploadCSVForm()

    return render(request, 'import_csv.html', {'form': form})
