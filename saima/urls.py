"""
URL configuration for saima project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("usuario/", include("usuario.urls")),
    path("usuario_auth/", include("usuario_auth.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("produto/", include("produto.urls")),
    path("grupo/", include("grupo.urls")),
    path("permissao/", include("permissao.urls")),
    path("movimento/", include("movimento.urls")),
    path('', home ,name='home'),
    path('about/', about, name='about'),  # <- Aqui está o caminho do "Sobre"


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Definindo o handler personalizado para erro 403
handler403 = 'usuario.views.erro_403'
