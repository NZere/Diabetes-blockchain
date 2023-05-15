from django.conf.urls.static import static
from django.urls import path

from diabetes_project import settings
from . import views

app_name = 'appointment'
urlpatterns = [
    path('', views.index, name='index'),
    path('account/', views.user_main_page, name='user_s_main_page'),
    path('account/doctor/<int:id>', views.appointment_doctor_page, name='user_s_main_page_doctor'),
    path('account/patient/<int:id>', views.appointment_patient_page, name='user_s_main_page_patient'),
    path('account/doctor/<int:id>/save', views.appointment_doctor_save, name='save_appointment'),

    path('doctor/<slug:slug>/', views.doctor_selected, name='doctor_selected'),
    path('doctor/<slug:slug>/date/<str:date_schedule>', views.date_selected, name='date_selected'),
    # path('doctor/<slug:slug>/date/<str:date_schedule>/time/<str:time_schedule>', views.time_selected,
    #      name='time_selected'),
    path('appointment_submit/', views.appointment_submit, name='appointment_submit'),
    path('appointment_end/', views.appointment_end, name='appointment_end'),

    # path('add_doctor/<slug>', views.add_doctor_url, name='add-doctor-url')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
