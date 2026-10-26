from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("reports/", views.report_list, name="report_list"),
    path("reports/create/", views.create_report, name="create_report"),
    path("reports/<int:pk>/", views.report_detail, name="report_detail"),
    path("reports/<int:pk>/edit/", views.edit_report, name="edit_report"),
    path("reports/<int:pk>/delete/", views.delete_report, name="delete_report"),
    path("reports/<int:pk>/claim/", views.create_claim, name="create_claim"),
    path("reports/<int:pk>/claims/<int:claim_id>/decide/", views.decide_claim, name="decide_claim"),
    path("signup/", views.signup, name="signup"),
]
