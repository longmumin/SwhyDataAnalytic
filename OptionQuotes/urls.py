"""SwhyDataAnalytic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from . import get_data, quotes, TQuotes
from django.conf.urls import url

urlpatterns = [
    #主报价页面
    path('', quotes.loadPage, name='quotes'),
    #主报价POST
    path('updateQuotes/', quotes.loadData, name='updateQuotes'),
    path('loadQuotes/', quotes.loadData, name='loadQuotes'),
    #T型报价页面
    path('TQuotes/<str:instrument>', TQuotes.loadPage, name='TQuotes'),
    #T型报价 POST
    path('TQuotes/loadTQuotes/<str:instrument>', TQuotes.loadData, name='loadTQuotes'),
    path('TQuotes/updateTQuotes/<str:instrument>', TQuotes.loadData, name='loadTQuotes'),

]
