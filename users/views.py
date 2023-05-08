import json
import os
import subprocess

import cv2
from asgiref.sync import sync_to_async
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators import gzip

from .face_recognition import dataset, training, recognition
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
import re
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
from django.views.decorators.csrf import csrf_exempt
from users.models import Wallet, Doctor
from django.http import HttpResponse
import asyncio

BS = 16
pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
unpad = lambda s: s[0:-ord(s[-1:])]


def encrypt(id, plain_text, key):
    private_key = hashlib.sha256(key.encode("utf-8")).digest()
    plain_text = pad(plain_text)
    print("After padding:", plain_text)
    iv = Random.new().read(AES.block_size)
    print("iv", iv)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(plain_text)
    print("encrypted", encrypted)
    result = encrypted[0:(id % 16)] + iv + encrypted[id % 16:]
    print("result", result)
    return base64.b64encode(result)


# After padding: b'Tata_1\n\n\n\n\n\n\n\n\n\n'
# iv b'\x9a\xfc\xb5\xf6\xd0\xf22k\x9b\xebdH?\x1b6\xb7'
# encrypted b'\xec5J[\xcbE\xcd[G\xaah\xdb\xa2\x02w\x0f'
# result b'\xec5J[\xcbE\x9a\xfc\xb5\xf6\xd0\xf22k\x9b\xebdH?\x1b6\xb7\xcd[G\xaah\xdb\xa2\x02w\x0f'
# After padding: b'\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10'
# iv b'\xa9\xae6}4|^\xe6f<p\xa7\xcb\x16ry'
# encrypted b'\x82(I)\xb5\x9a\x14\x02\x95\x898\x90\x87\x1az\xa9'
# result b'\x82(I)\xb5\x9a\xa9\xae6}4|^\xe6f<p\xa7\xcb\x16ry\x14\x02\x95\x898\x90\x87\x1az\xa9'

def decrypt(id, cipher_text, key):
    private_key = hashlib.sha256(key.encode("utf-8")).digest()
    cipher_text = base64.b64decode(cipher_text)
    encrypted = cipher_text[0:(id % 16)]
    iv = cipher_text[(id % 16): (id % 16 + 16)]
    encrypted += cipher_text[(id % 16 + 16):]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted))


def get_iv_from_cipher(id, cipher_text):
    print(cipher_text)
    cipher_text = base64.b64decode(cipher_text)
    iv = cipher_text[(id % 16): (id % 16 + 16)]
    print("cipher_text", cipher_text)
    print('iv', iv)
    return iv


def encrypt_with_iv(iv, id, plain_text, key):
    private_key = hashlib.sha256(key.encode("utf-8")).digest()
    plain_text = pad(plain_text)
    print("After padding:", plain_text)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(plain_text)
    print("encrypted", encrypted)
    result = encrypted[0:(id % 16)] + iv + encrypted[id % 16:]
    print("result", result)
    return base64.b64encode(result)


def get_user_money(user):
    money = Wallet.objects.get(user=user).money.encode('ascii')
    print(money)
    username = user.username
    id = user.id
    user_money = 0
    try:
        user_money = (decrypt(id, money, username)).decode('ascii')
        if len(user_money) < 1:
            user_money = 0
    except:
        user_money = 0
    print('in get user money', user_money)
    return float(user_money)


def get_user_first_name(user):
    first_name = user.first_name.encode('ascii')
    username = user.username
    id = user.id
    user_first_name = (decrypt(id, first_name, username)).decode('ascii')
    print(user_first_name)
    return user_first_name


def get_user_last_name(user):
    last_name = user.last_name.encode('ascii')
    username = user.username
    id = user.id
    user_last_name = (decrypt(id, last_name, username)).decode('ascii')
    print(user_last_name)
    return user_last_name


def get_user_email(user):
    print("in email")
    email = user.email.encode('ascii')
    print(email)
    username = user.username
    id = user.id
    user_email = (decrypt(id, email, username)).decode('ascii')
    print(user_email)
    return user_email


@csrf_exempt
def register(request):
    if request.method == "POST":
        print("here")
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        username = request.POST.get('username_up', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password1', '')
        email = request.POST.get('email_up', '')

        value = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email
        }
        usernames = list(User.objects.all().values_list('username', flat=True))
        emails = list(User.objects.all().values_list('email', flat=True))
        email_hash = hashlib.sha256(email.encode('ascii')).hexdigest()
        error_message = None
        if len(first_name) == 0:
            error_message = "Please Enter your First Name !!"
        elif len(first_name) < 3:
            error_message = 'First Name must be 3 char long or more'
        elif len(last_name) == 0:
            error_message = 'Please Enter your Last Name'
        elif len(last_name) < 3:
            error_message = 'Last Name must be 3 char long or more'
        elif len(username) == 0:
            error_message = 'Enter your username'
        elif len(username) < 3:
            error_message = 'Username must be 3 char Long or more'
        elif usernames.__contains__(username):
            error_message = 'This username exists'
        elif len(email) == 0:
            error_message = 'Please Enter your Email'
        elif len(email) < 5:
            error_message = 'Email must be 5 char long'
        elif not re.search("[@.]", email):
            error_message = 'Email must be nnn@n.n'
        elif len(password1) < 5:
            error_message = 'Password must be 8 char long'
        elif not re.search("[a-z]", password1):
            error_message = 'Password must contains letters'
        elif not re.search("[A-Z]", password1):
            error_message = 'Password must contains Upper letters'
        elif not re.search("[0-9]", password1):
            error_message = 'Password must contains numbers'
        elif not re.search("[_@$#]", password1):
            error_message = 'Password must contains at least one of these _,@,$,#,@ symbols'
        elif not (password1 == password2):
            error_message = 'Password is not matching'

        if not error_message:

            # user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name,
            #                                 last_name=last_name)
            user = User.objects.create_user(username=username, password=password1, email=email,
                                            first_name=first_name,
                                            last_name=last_name)
            user.save()
            user_id = user.id
            user.first_name = (encrypt(user_id, first_name, username)).decode('ascii')
            user.last_name = (encrypt(user_id, last_name, username)).decode('ascii')
            user.email = (encrypt(user_id, email, username)).decode('ascii')
            user.password = (encrypt(user_id, hashlib.sha256(password1.encode('ascii')).hexdigest(), username)).decode(
                'ascii')
            # print(user.id, user.username, user.password, user.first_name, user.last_name, user.email)
            user.save()
            wallet = Wallet(user=user)
            wallet.save()
            wallet.money = (encrypt(user_id, wallet.money, username)).decode('ascii')
            wallet.save()
            print('user created')
            messages.success(request, "user created")

            return redirect('/users/login', value)
        else:
            messages.warning(request, error_message)
            return render(request, 'login.html', value)
    else:
        print("lal")
        return render(request, 'login.html')


def index(request):
    pass


def logout(request):
    auth.logout(request)
    return redirect('/')


# def crypto(request):
#     user = User.objects.get(id=5)
#     user.email = (encrypt(user.id, user.email, user.username)).decode('ascii')
#     user.first_name = (encrypt(user.id, user.first_name, user.username)).decode('ascii')
#     user.last_name = (encrypt(user.id, user.last_name, user.username)).decode('ascii')
#     user.password = (encrypt(user.id, hashlib.sha256("admin".encode('ascii')).hexdigest(), user.username)).decode(
#         'ascii')
#     print(user.id, user.username, user.password, user.first_name, user.last_name, user.email)
#     user.save()
#     return redirect('/')

@csrf_exempt
def crypto(request):
    user_id = 5
    username = "admin2"
    password = "admin2"
    email = "admin2@admin.com"
    first_name = "Admin"
    last_name = "Admin"
    user = User.objects.get(id=user_id)

    user.email = (encrypt(user_id, email, username)).decode('ascii')
    user.first_name = (encrypt(user_id, first_name, username)).decode('ascii')
    user.last_name = (encrypt(user_id, last_name, username)).decode('ascii')
    user.password = (encrypt(user_id, hashlib.sha256(password.encode('ascii')).hexdigest(), username)).decode(
        'ascii')
    print(user.id)
    print(user.username)
    print(user.password)
    print(user.first_name)
    print(user.last_name)
    print(user.email)
    user.save()
    return redirect('/')


@csrf_exempt
def login(request):
    user_first_name = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
        print(user_first_name)
    print("login page")
    print(request)
    if request.method == "POST":
        print("POST")
        username = request.POST.get("username_in", '')
        password = request.POST.get("password_in", '')
        print("username", username)
        user = check_user(username, password)
        if type(user) == User:
            try:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth.login(request, user)
                first_name = get_user_first_name(user)
                message = "Hello, " + first_name
                messages.success(request, message)
                return redirect('/',
                  {"user_first_name": user_first_name})
            except Exception:
                value = {'username': username}
                redirect('/users/login',
                  {"user_first_name": user_first_name})
        else:
            value = {'username': username}
            redirect('/users/login',
                  {"user_first_name": user_first_name})

    else:
        return render(request, 'login.html',
                  {"user_first_name": user_first_name})


@csrf_exempt
def login_doctor_pass(request):
    user_first_name = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
        print(user_first_name)
    print("login doctor page")
    print(request)
    if request.method == "POST":
        print("POST")
        username = request.POST.get("username_in", '')
        password = request.POST.get("password_in", '')
        print("username", username)
        user = check_user(username, password)
        if type(user) == User:
            try:
                doctor_user = Doctor.objects.get(doctor_user=user)
                if not doctor_user:
                    return redirect('/users/login/users/doctor/pass')
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth.login(request, user)
                first_name = get_user_first_name(user)
                message = "Hello, " + first_name
                messages.success(request, message)
                return redirect('/',
                  {"user_first_name": user_first_name})
            except Exception:
                value = {'username': username}
                return render(request, 'loginDoctor.html',
                              {"user_first_name": user_first_name})
        else:
            value = {'username': username}
            return render(request, 'loginDoctor.html',
                          {"user_first_name": user_first_name})

    else:
        return render(request, 'loginDoctor.html',
                      {"user_first_name": user_first_name})


@csrf_exempt
def login_doctor_face(request):
    user_first_name = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
        print(user_first_name)
    login_face_id(request)
    return render(request, 'loginDoctor.html',
                  {"user_first_name": user_first_name})


def login_face_id(request):
    user_first_name = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
        print(user_first_name)
    print("here")
    res = subprocess.run(["python3 users/face_recognition/recognition.py"], shell=True, capture_output=True)
    print(res.stdout)
    face_id_result = json.loads(res.stdout)
    print(face_id_result)
    if "error" in face_id_result:
        return redirect('/users/login/users/doctor/pass', {"user_first_name": user_first_name})
    user_id = face_id_result["result"]
    print(user_id[0])
    try:
        user = User.objects.get(id=user_id[0])
        if not user:
            return redirect('/users/login/users/doctor/pass', {"user_first_name": user_first_name})
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth.login(request, user)
        first_name = get_user_first_name(user)
        print("fn", first_name)
        return redirect('/', {"user_first_name": user_first_name})
    except Exception:
        return redirect('/users/login/users/doctor/pass',
                  {"user_first_name": user_first_name})
    return redirect('/',
                  {"user_first_name": user_first_name})


def learn_doctor(request, id):
    user_first_name = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
        print(user_first_name)
    user = User.objects.get(id=id)
    print(user.username)
    try:
        subprocess.run([f"python3 users/face_recognition/dataset.py {id} {user.username}"], shell=True, capture_output=True)
        training_recognition()
    except:
        print("error")
    return render(request, 'loginDoctor.html',
                  {"user_first_name": user_first_name})


def training_recognition():
    subprocess.run(["python3 users/face_recognition/training.py"], shell=True, capture_output=True)

def check_user(username: str, password: str):
    user = None
    try:
        print("here")
        user = User.objects.get(username=username)
    except:
        user = None
        return 'Username is not exist'
    if user is not None:
        user_id = user.id
        iv = get_iv_from_cipher(user.id, (user.password).encode('ascii'))
        user_hashed = hashlib.sha256(password.encode('ascii')).hexdigest()
        print("hashed", user_hashed)
        temp_pass = (encrypt_with_iv(iv, user_id, user_hashed, username)).decode('ascii')
        print('temp_pass', temp_pass)
        print('password', password)
        if temp_pass == user.password:
            print("password matches")
            try:
                user = User.objects.get(username=username, password=temp_pass)
                return user
            except():
                return 'Invalid password'
        else:
            return 'Invalid password'
    else:
        return 'This user is not exists'

@csrf_exempt
def add_doctor(request):
    if request.user.is_superuser and request.method == "POST":
        user_id = int(request.POST.get("user_id", ''))
        experience = request.POST.get("experience", '')
        description = request.POST.get("description", '')
        image = request.POST.get("image", '')
        phone_num = request.POST.get("phone_num", '')
        sex = request.POST.get("sex", '')
        try:
            user = User.objects.get(id=user_id)
            user_doctor, created = Doctor.objects.create(
                doctor_user=user,
                experience=experience,
                description=description,
                image=image,
                first_name=user.first_name,
                last_name=user.last_name,
                phoneNum=phone_num,
                slug=user.username,
                sex=sex
            )
            message = f"Doctor with id {user_id} added" if created else f"Error in adding doctor"
            # return HttpResponse(status=201, messages=message)
            return HttpResponse(status=201)
        except Exception:
            message = f"Error in adding doctor"
            return HttpResponse(status=400)
    elif not request.user.is_superuser:
        return HttpResponse(status=403)


@csrf_exempt
def remove_doctor(request, user_id):
    if request.method == "DELETE":
        user_doctor, deleted = Doctor.objects.filter(doctor_user=User.objects.get(user=user_id)).delete()
        return HttpResponse(status=200)

