from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('pokemon/', views.pokemonAll),
    path('pokemon/<str:name>/', views.pokemonBio)
]