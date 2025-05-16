from django.urls import path
from . import views

urlpatterns = [
    path('dashboard_view/', views.dashboard_view, name='dashboard_view'),  # Página inicial do dashboard
   
]
