from django.urls import path
from . import auth

urlpatterns = [
    #加载页面
    path('login/', auth.loadAuthPage, name='loadAuthPage'),

    #创建用户
    path('login/createUser', auth.createUser, name='createUser'),

    #创建用户
    path('login/getUserData', auth.getUserData, name='getUserData')
]
