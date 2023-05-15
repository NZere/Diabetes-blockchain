import datetime

from django.shortcuts import render, redirect, get_object_or_404
from dateutil.relativedelta import relativedelta
from appointment.models import *
from users.models import Doctor
from users.views import get_user_first_name, get_user_last_name, get_user_email
from django.contrib.auth.models import User, auth
from django.views.decorators.csrf import csrf_exempt


def index(request):
    if request.method == "POST":
        pass
    elif request.method == "GET":
        all_doctors = Doctor.objects.all()
        for doctor in all_doctors:
            doctor.first_name = get_user_first_name(doctor.doctor_user)
            doctor.last_name = get_user_first_name(doctor.doctor_user)
        data = {
            "all_doctors": all_doctors,
        }
        return render(request, 'appointment1.html', data)


def doctor_selected(request, slug):
    # item = get_object_or_404(Doctor, slug=slug)
    print("doctor_selected")
    schedules = get_all_open_work_time_of_doctor(slug)
    return render(request, 'appointment2.html', {"schedules": schedules})


def get_all_open_work_time_of_doctor(doctor_slug):
    """"
    1 month
    """
    user_doctor = get_user_doctor(doctor_slug)
    today = datetime.date.today()
    schedules = Schedule.objects.filter(doctor=user_doctor, status='open', work_time__date__gte=today,
                                        work_time__date__lte=today + relativedelta(month=1))
    return schedules


def get_user_doctor(doctor_slug):
    user_doctor = None
    try:
        user_doctor = Doctor.objects.get(slug=doctor_slug)
    except Exception as e:
        print(f"error {e}")
        return redirect('/appointment')
    if not user_doctor:
        print(f"error: User is not found")
        return redirect('/appointment')
    return user_doctor


def date_selected(request, slug, date_schedule):
    print(date_schedule)
    work_times = get_work_time_of_date(slug, date_schedule)
    time_data = []
    time_data_ids = []
    for work_time in work_times:
        time_data.append(work_time.work_time.time.__str__())
        time_data_ids.append(work_time.work_time_id)
    print(time_data)
    zipped_list = zip(time_data, time_data_ids)
    return render(request, 'appointment2.html', {"zip": zipped_list, "doctor_slug": slug})


def get_work_time_of_date(doctor_slug, date_schedule):
    user_doctor = get_user_doctor(doctor_slug)
    work_times = Schedule.objects.filter(doctor=user_doctor, status='open', work_time__date=date_schedule)
    return work_times


@csrf_exempt
def appointment_submit(request):
    user_first_name = None
    user_last_name = None
    user_email = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
        user_last_name = get_user_last_name(request.user)
        user_email = get_user_email(request.user)
    doctor_slug = request.POST.get("doctor_slug", '')
    time_sel = request.POST.get("time__select", '')
    data = {
        "doctor_slug": doctor_slug,
        "time_sel": time_sel,
        "first_name": user_first_name,
        "last_name": user_last_name,
        "email": user_email
    }
    return render(request, 'appointment3.html', data)
    pass


def appointment_end(request):
    user_first_name = None
    user_last_name = None
    user_email = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
        user_last_name = get_user_last_name(request.user)
        user_email = get_user_email(request.user)
    doctor_slug = request.POST.get("doctor_slug", '')
    time_sel = request.POST.get("time_sel", '')
    print(doctor_slug)
    print(time_sel)
    try:
        doctor = Doctor.objects.get(slug=doctor_slug)
        time = All_work_times.objects.get(id=time_sel)
        schedule = Schedule.objects.get(doctor=doctor, work_time=time)
        schedule.status = 'not-yet'
        schedule.patient = request.user
        schedule.save()
        return redirect('/')
    except Exception as e:
        print(f"error: {e}")
        return redirect('/appointment')


def user_main_page(request):
    today = request.GET.get('today')
    print(today)
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        user_first_name = get_user_first_name(user)
        try:
            doctor = Doctor.objects.get(doctor_user=user)
            if not doctor:
                return render(request, "patientMain.html", {'user_first_name': user_first_name,
                                                            "data": get_all_appointments_patient(user, today)})
            else:
                return render(request, "doctorMain.html", {'user_first_name': user_first_name,
                                                           "data": get_all_appointments_doctor(doctor, today)})
        except:
            return render(request, "patientMain.html", {'user_first_name': user_first_name,
                                                        "data": get_all_appointments_patient(user, today)})
    else:
        return redirect("/")


def get_all_appointments_doctor(doctor_user, today=False):
    print("id", doctor_user.id)
    print("du", doctor_user)

    if not today:
        appointments = Schedule.objects.filter(doctor=doctor_user.id)
    else:
        today = datetime.date.today()
        appointments = Schedule.objects.filter(doctor=doctor_user.id, work_time__date=today)
    data = []
    for app in appointments:
        if app.patient is not None:
            data.append({
                "id": app.id,
                "patient": app.patient.first_name,
                "date": app.work_time.date,
                "time": app.work_time.time,
                "status": app.status
            })
    print(data)
    return data


def get_all_appointments_patient(patient_user, today=False):
    if not today:
        appointments = Schedule.objects.filter(patient=patient_user)
    else:
        today = datetime.date.today()
        appointments = Schedule.objects.filter(patient=patient_user, work_time__date=today)

    data = []
    for app in appointments:
        print(app)

        data.append({
            "id": app.id,
            "doctor": get_user_first_name(app.doctor.doctor_user),
            "date": app.work_time.date,
            "time": app.work_time.time,
            "status": app.status,
        })
    print(data)
    return data


def appointment_doctor_page(request, id: int):
    appointment = Schedule.objects.get(id=id)

    products = Recommendation_product.objects.filter(schedule=appointment)
    rec_products = []
    for pr in products:
        rec_products.append(pr.id)
    print("rec_prooods", rec_products)
    rec_str = ""
    try:
        rec_str = ', '.join(str(v) for v in rec_products)
    except Exception as e:
        print("error ", e)

    return render(request, "doctorEditPatient.html", {
        "appointment": appointment,
        "products": rec_str})


def appointment_patient_page(request, id: int):
    appointment = Schedule.objects.get(id=id)
    products = Recommendation_product.objects.filter(schedule=appointment)
    doctor = Doctor.objects.get(id=appointment.doctor.id)
    doctor_user = User.objects.get(id=doctor.doctor_user.id)
    rec_products = []
    for pr in products:
        rec_products.append(pr.id)
    print("rec_prooods", rec_products)
    rec_str = ""
    try:
        rec_str = ', '.join(str(v) for v in rec_products)
    except Exception as e:
        print("error ", e)
    return render(request, "patientReport.html", {
        "appointment": appointment,
        "products": rec_str,
        "name_user": get_user_first_name(user=request.user)+" "+get_user_last_name(user=request.user),
        "name_doctor": get_user_first_name(user=doctor_user)+" "+get_user_last_name(user=doctor_user)
    })


@csrf_exempt
def appointment_doctor_save(request, id: int):
    user = User.objects.get(id=request.user.id)
    if request.method == "POST":
        rec_doctor = request.POST.get("recommendation-doctor", '')
        rec_med = request.POST.get("recommendation-medications", '')
        doctor = Doctor.objects.get(doctor_user=user)
        appointment = Schedule.objects.filter(id=id, doctor=doctor).first()
        print("rec_doctor", rec_doctor)
        appointment.info = rec_doctor
        appointment.status = "done"
        appointment.save()
        print("rec_med", rec_med)
        rec_products = str(rec_med).split(',')
        for rec_product_id in rec_products:
            product = Product.objects.get(id=rec_product_id)
            rec_med_object = Recommendation_product.objects.create(
                schedule=appointment,
                doctor=appointment.doctor,
                patient=appointment.patient,
                product=product
            )
            rec_med_object.save()

        return redirect("/appointment/account/")
    else:
        return redirect("/appointment/account/")

# def check_user_data(first_data, second_data):
#     if first_data == second_data:
#         return False
#     if second_data == '':
#         return False
#     return True
