from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Handles GET and POST to /api/
]