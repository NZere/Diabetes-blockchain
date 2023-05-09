from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('main/contact/', views.contact, name='contact')

]
