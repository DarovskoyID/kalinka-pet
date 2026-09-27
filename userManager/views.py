from django.conf import settings
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from userManager.forms import RegisterForm, LoginForm


def landing(request):
    return render(request, "landing.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/app")
    if request.method == "POST":
        form = LoginForm(request, data=request.POST or None)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("/app")
    else:
        form = LoginForm()


    context = {
        'form': form,
    }

    return render(request, "auth/login.html", context)


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()


    context = {
        'form': form,
    }

    return render(request, "auth/register.html", context)


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect("landing")
