import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.files.storage import FileSystemStorage
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from users.forms import (LoginForm, RegisterForm, UpdatePasswordForm,
                         UpdateUserForm)


def profile(request):
    if not request.user.is_authenticated:
        return redirect('users:login')

    return render(request, "home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect('users:profile')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Usuário Criado!")
            return redirect("users:login")
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


def login_(request):
    if request.user.is_authenticated:
        return redirect('users:profile')

    if request.method == "POST":
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

        else:
            messages.error(request, "Erro no Login")
            return render(request, "auth/login.html", {
                "form": form,
                "form_action": reverse("users:login"),
                "auth_page": True
            })

    form = LoginForm()
    return render(request, "auth/login.html", {
        "form": form,
        "form_action": reverse("users:login"),
        "auth_page": True
    })


@login_required(login_url="users:login", redirect_field_name="next")
def logout_execute(request):
    if not request.POST:
        raise Http404

    if request.POST.get('email') != request.user.email:
        messages.error(request, "Falha no Logout")
        return redirect("users:profile")

    logout(request)
    messages.success(request, "Logout realizado")
    return redirect("users:login")


@login_required(login_url="users:login", redirect_field_name="next")
def update_profile(request):
    if request.method == "POST":
        form = UpdateUserForm(
            data=request.POST or None,
            files=request.FILES or None,
            instance=request.user
        )

        if form.is_valid():

            storage = FileSystemStorage(
                settings.MEDIA_ROOT / "users/avatars",
                settings.MEDIA_URL + "users/avatars"
            )

            user = form.save(commit=False)
            avatar = request.FILES.get('avatar')

            if avatar:
                extension = avatar.name.split('.')[-1]

                file = storage.save(f"{uuid.uuid4()}.{extension}", avatar)
                avatar = storage.url(file)

                if avatar and request.user.avatar != \
                        "/media/users/avatars/default_avatar.png":
                    storage.delete(request.user.avatar.split("/")[-1])

                user.avatar = avatar

            messages.success(request, "Dados editados com sucesso")
            user.save()
            return redirect("users:profile")
        else:
            messages.error(request, "Erro na edição dos dados")
            return render(request, "user/update_user.html", {
                "form": form,
                "form_action": reverse("users:update_profile")
            })

    form = UpdateUserForm(
        instance=request.user
    )

    return render(request, "user/update_user.html", {
        "form": form,
        "form_action": reverse("users:update_profile")
    })


@login_required(login_url="users:login", redirect_field_name="next")
def update_password(request):
    if request.method == "POST":
        form = UpdatePasswordForm(request.POST)

        if form.is_valid():
            user = request.user
            old_password = form.data.get('old_password')
            new_password = form.data.get('new_password')

            if user and check_password(old_password, user.password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Senha alterada")
                return redirect(reverse("users:profile"))
            else:
                messages.error(request, "Senha incorreta")
                return redirect(reverse("users:update_password"))
        else:
            return render(request, "user/update_password.html", {
                'form': form,
                'form_action': reverse("users:update_password")
            })

    form = UpdatePasswordForm()
    return render(request, "user/update_password.html", {
        'form': form,
        'form_action': reverse("users:update_password")
    })
