from django.urls import path
from . import views

app_name = 'appointment'
urlpatterns = [
    path('', views.index, name='index'),
    path('doctor/<slug:slug>/', views.doctor_selected, name='doctor_selected'),
    path('doctor/<slug:slug>/date/<str:date_schedule>', views.date_selected, name='date_selected'),
    # path('doctor/<slug:slug>/date/<str:date_schedule>/time/<str:time_schedule>', views.time_selected,
    #      name='time_selected'),
    path('appointment_submit/', views.appointment_submit, name='appointment_submit'),
    path('appointment_end/', views.appointment_end, name='appointment_end'),

    # path('add_doctor/<slug>', views.add_doctor_url, name='add-doctor-url')
]
