from django.urls import path
from . import views

app_name = 'adminclone'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<str:model_name>/', views.model_list, name='model_list'),
    path('<str:model_name>/create/', views.model_create, name='model_create'),
    path('<str:model_name>/<int:pk>/update/', views.model_update, name='model_update'),
    path('<str:model_name>/<int:pk>/delete/', views.model_delete, name='model_delete'),
]