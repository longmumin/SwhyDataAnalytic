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
from django.urls import path, include

from . import navigation
from . import publicMethod
from userAuth import auth

urlpatterns = [
    path('admin/', admin.site.urls),
    #期权报价
    path('quotes/', include('OptionQuotes.urls')),
    #债券量化
    path('FixedIncome/', include('FixedIncomeQuantPlatform.urls')),
    #测试restful接口
    path('Restful/', include('testRestfulApi.urls')),
    #权限管理
    path('userAuth/', include('userAuth.urls')),
    #导航页面
    path('index/', navigation.loadnavigationPage, name='loadnavigationPage'),
    #公共方法
    path('publicMethod/getSYSCode', publicMethod.getSysCode, name='getSysCode'),

]
