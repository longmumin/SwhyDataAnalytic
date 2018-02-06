from django.urls import path
from . import views

urlpatterns = [
    #加载页面
    path('snippets/', views.snippet_list, name='loadYTMAnalytic'),
]
