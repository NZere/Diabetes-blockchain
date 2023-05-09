from django.shortcuts import render

from users.views import get_user_first_name


# Create your views here.
def index(request):
    user_first_name = None
    if request.user.is_authenticated:
        print("fn", request.user.first_name)
        print("un", request.user.username)
        user_first_name = get_user_first_name(request.user)
        print(user_first_name)
    return render(request, 'index.html',
                  {"user_first_name": user_first_name})


def contact(request):
    user_first_name = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
    return render(request, 'contact.html',
                  {"user_first_name": user_first_name})
