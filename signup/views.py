from django.shortcuts import render
from django.http import HttpResponseRedirect
# from django.contrib.auth import login, authenticate
# from django.contrib.auth.forms import UserCreationForm

from .forms import RegisterForm

# Create your views here.
def register(response):
    if response.method == "POST":
        newUser = RegisterForm(response.POST)
        if newUser.is_valid():
            newUser.save()
            return HttpResponseRedirect('/login/')
    else:
        newUser = RegisterForm()

    return render(response, "signup/sign_up.html", {'registry_form': newUser})  