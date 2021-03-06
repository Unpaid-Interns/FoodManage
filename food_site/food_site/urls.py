"""food_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from sku_manage.admin import admin_site
from django.urls import path
from django.conf.urls import include

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('home.urls')),
    path('importer/', include('importer.urls')),
    path('reporting/', include('dep_report.urls')),
    path('reporting/', include('sales.urls')),
    path('search/', include('sku_manage.urls')),
    path('manufacturing/', include('manufacturing_goals.urls')),
    path('mfglinemap/', include('mfg_map.urls')),
]
