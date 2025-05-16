from django.urls import path
from . import views



urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup,name='signup'),
    path('logout/', views.signout,name='logout'),


    # Adicionando as rotas de reset de senha
    path('password_reset/', views.password_reset_form, name='password_reset_form'),
    path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
]
