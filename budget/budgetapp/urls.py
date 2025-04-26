from django.urls import path
from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("treatment_login", views.treatment_login, name="treatment_login"),
    path("manager", views.dept_manager, name="manager"),
    path("previsions/<str:deptno>/<str:month>/<str:year>/<str:type_categorie>/<str:table_type>", views.get_list,
         name="get_list"),
    path("update/<str:element_id>/<str:table_id>", views.find_update_element, name="find_update_element"),
    path("submit_update", views.submit_update, name="submit_update"),
    # path('budget/<str:emp_no>/<str:year>', views.budget_form, name='budget_form'),
    path('budget/<str:dept_no>/<str:year>', views.res_budget, name='res_budget'),
    path('insert', views.insert_libelle, name='insert_libelle'),
    path('waiting/<str:deptno>', views.get_waiting_list, name='waiting'),
    path('accept/<str:table_id>/<str:element_id>', views.accept, name='accept'),
    path('budget/pdf/<str:dept_no>/<str:year>/', views.budget_pdf_view, name='budget_pdf'),
    path('budget/export/csv/', views.export_budget_csv, name='export_budget_csv'),
    path('disconnect', views.disconnect, name='disconnect'),
    path('categories-et-comportements/', views.page_categorie_et_comportement, name='categories_et_comportements'),
    path('graphe/', views.graphe_realisations, name='graphe_realisations'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),
]
