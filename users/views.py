from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
import re
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
from django.views.decorators.csrf import csrf_exempt

from users.models import Wallet

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
        username = request.POST.get('username', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password1', '')
        email = request.POST.get('email', '')

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
            return render(request, 'users/register.html', value)
    else:
        print("lal")
        return render(request, 'users/register.html')


def index(request):
    pass


def logout(request):
    auth.logout(request)
    return redirect('/')


def crypto(request):
    user = User.objects.get(id=1)
    user.email = (encrypt(user.id, user.email, user.username)).decode('ascii')
    user.first_name = (encrypt(user.id, user.first_name, user.username)).decode('ascii')
    user.last_name = (encrypt(user.id, user.last_name, user.username)).decode('ascii')
    user.password = (encrypt(user.id, hashlib.sha256("admin".encode('ascii')).hexdigest(), user.username)).decode(
        'ascii')
    print(user.id, user.username, user.password, user.first_name, user.last_name, user.email)
    user.save()
    return redirect('/')


@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get("username", '')
        password = request.POST.get("password", '')

        user = None
        try:
            print("here")
            user = User.objects.get(username=username)
        except():
            user = None
        value = {'username': username}
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
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    auth.login(request, user)
                    first_name = get_user_first_name(user)
                    message = "Hello, " + first_name
                    messages.success(request, message)
                    return redirect('/')
                except():
                    messages.warning(request, 'Invalid password')
                    return redirect('/users/login', value)
            else:
                messages.warning(request, 'Invalid password')
                return redirect('/users/login', value)
        else:
            messages.info(request, 'This user is not exists')
            return redirect('/users/login', value)
    else:
        return HttpResponse("Error")
