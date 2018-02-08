from django.urls import path
from . import views

urlpatterns = [
    #加载页面
    path('taskList/', views.TaskList.as_view(), name='taskList'),
]
