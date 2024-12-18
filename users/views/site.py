from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from users.forms import LoginForm, RegisterForm


def profile(request):
    if not request.user.is_authenticated:
        return redirect('users:login_view')

    return render(request, "home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect('users:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Usuário Criado!")
            return redirect("users:login_view")
        else:
            messages.error(request, "Falha no Cadastro")
            return render(request, "auth/register.html", {
                "form": form,
                "form_action": reverse("users:register"),
                "auth_page": True
            })

    form = RegisterForm()

    return render(request, "auth/register.html", {
        "form": form,
        "form_action": reverse("users:register"),
        "auth_page": True
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:profile')

    form = LoginForm()
    return render(request, "auth/login.html", {
        "form": form,
        "form_action": reverse("users:login_create"),
        "auth_page": True
    })


def login_create(request):
    if not request.POST:
        raise Http404

    form = LoginForm(request.POST)

    if form.is_valid():
        authenticated_user = authenticate(
            email=form.data.get('email', ''),
            password=form.data.get('password', ''),
        )

        if authenticated_user is not None:
            messages.success(request, "Usuário Logado")
            login(request, authenticated_user)
            return redirect("users:profile")

    messages.error(request, "Erro no Login")
    return redirect("users:login_view")


@login_required(login_url="users:login_view", redirect_field_name="next")
def logout_execute(request):
    if not request.POST:
        raise Http404

    if request.POST.get('email') != request.user.email:
        messages.error(request, "Falha no Logout")
        return redirect("users:home")

    logout(request)
    messages.success(request, "Logout realizado")
    return redirect("users:login_view")
