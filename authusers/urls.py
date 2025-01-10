from django.urls import path
from . import views

urlpatterns = [
    path('create-company/', views.create_company, name='create_company'),
    path('add-user/', views.add_user, name='add_user'),
]
