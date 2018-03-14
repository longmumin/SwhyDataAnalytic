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
from django.conf.urls import url
from . import dao
from . import dataAnalytic

urlpatterns = [
    #加载页面
    path('YTMAnalytic/', dataAnalytic.loadPage, name='loadYTMAnalytic'),

    #导入债券到期数据
    #path('YTMAnalytic/insertDataToBondYTM', dao.insertDataToBondYTM, name='insertDataToBondYTM'),
    #导入期货合约数据
    #path('YTMAnalytic/insertDataToFutureInfo', dao.insertDataToFutureInfo, name='insertDataToFutureInfo'),
    #导入期货行情数据
    #path('YTMAnalytic/insertDataToFutureDatabase', dao.insertDataToFutureDatabase, name='insertDataToFutureDatabase'),

    #页面初始化数据
    path('YTMAnalytic/loadData', dataAnalytic.loadData.as_view(), name='loadData'),
    #时序数据分析mi
    path('YTMAnalytic/getBondYTMAnalyicData', dataAnalytic.getBondYTMAnalyicData.as_view(), name='getBondYTMAnalyicData'),
    #获得价差
    path('YTMAnalytic/getBondYTMDiffCacl', dataAnalytic.getBondYTMDiffCacl.as_view(), name='getBondYTMDiffCacl'),
    #获得比价矩阵
    path('YTMAnalytic/generateYTMMatrix', dataAnalytic.getBondYTMMatrix.as_view(), name='getBondYTMMatrix'),
]
