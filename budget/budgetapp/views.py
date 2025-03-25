from django.shortcuts import render
from pyexpat.errors import messages

from .models import Employes, Departements, Previsions, Realisations
from .services.Checker import Checker


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


def get_list(request, deptno, year, type_categorie, table_type):
    if int(table_type) == 1:
        data = Checker.get_previsions_by_type(deptno, year, type_categorie)

    else:
        data = Checker.get_realisations_by_type(deptno, year, type_categorie)

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
                isValid = True
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



