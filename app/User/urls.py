"""
Mapeo de URL para el API User
"""

from django.urls import path

from User import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
]
