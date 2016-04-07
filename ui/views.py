from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import UserForm

@login_required(login_url='/accounts/login/')
def index(request):
    return render(request, 'index.html', {'user': request.user})


def register(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            new_user = authenticate(username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password'],)
            login(request, new_user)
            return HttpResponseRedirect('/')
        else:
            print user_form.errors
    return render(request, 'login.html', {})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your account has been disabled.")
        else:
            # print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'login.html', {})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')