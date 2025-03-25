from django.urls import path
from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("treatment_login", views.treatment_login, name="treatment_login"),
    path("manager", views.dept_manager, name="manager"),
    path("previsions/<str:deptno>/<str:year>/<str:type_categorie>/<str:table_type>", views.get_list, name="get_list"),
    path("update/<str:element_id>/<str:table_id>", views.find_update_element, name="find_update_element"),
    path("submit_update", views.submit_update, name="submit_update"),
]
