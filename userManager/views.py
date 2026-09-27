from django.shortcuts import redirect, render


def landing(request):
    return render(request, "landing.html")


def login_view(request):
    return render(request, "auth/login.html")


def register_view(request):
    return render(request, "auth/register.html")


def logout_view(request):
    return redirect("landing")
