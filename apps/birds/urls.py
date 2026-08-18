from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('o-serwisie/', views.o_serwisie, name='o_serwisie'),
    path('gatunek/<int:pk>/', views.gatunek_szczegoly, name='gatunek_szczegoly'),
]