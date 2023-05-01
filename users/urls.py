from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.index, name='index'),
    path('learn/doctor/<int:id>/', views.learn_doctor, name='learn_doctor'),
    path('login/', views.login, name='login'),
    path('login/doctor/pass/', views.login_doctor_pass, name='login_doctor_pass'),
    path('login/doctor/face/', views.login_doctor_face, name='login_doctor_face'),
    path('logout/', views.logout, name='logout'),
    path('crypto/', views.crypto, name='crypto'),
    path('add_doctor/', views.add_doctor, name='add doctor'),
    path('remove_doctor/<user_id>/', views.remove_doctor, name='remove doctor'),
]
