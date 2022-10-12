"""
Mapeo de URL para el API Receta
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from receta import views

router = DefaultRouter()
router.register('recetas', views.RecetaViewSet)
app_name = 'receta'

urlpatterns = [
    path('', include(router.urls)),
]
