from django.urls import path
from . import auth

urlpatterns = [
    #加载页面
    path('login/', auth.loadAuthPage, name='loadAuthPage'),
]
