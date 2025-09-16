from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("pacientes/", views.patient_list, name="patient_list"),
    path("pacientes/nuevo/", views.patient_create, name="patient_create"),
    path("pacientes/<int:pk>/", views.patient_detail, name="patient_detail"),

    path("pacientes/<int:patient_pk>/anamnesis/nueva/", views.anamnesis_create, name="anamnesis_create"),
    path("pacientes/<int:patient_pk>/audiometria/nueva/", views.audiogram_create, name="audiogram_create"),
    path("pacientes/<int:patient_pk>/vocal/nueva/", views.speech_create, name="speech_create"),
    path("pacientes/<int:patient_pk>/ldl/nueva/", views.ldl_create, name="ldl_create"),
]
