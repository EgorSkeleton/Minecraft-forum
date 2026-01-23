from django.urls import path
from . import views

urlpatterns = [
    path('', views.inp_home, name='inp_home'),
]