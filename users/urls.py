from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("", views.profile, name="profile"),

    path("cadastro", views.register, name="register"),

    path('entrar', views.login_, name="login"),

    path("sair", views.logout_execute, name="logout"),

    path("atualizar", views.update_profile, name="update_profile"),
]
