from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("", views.profile, name="profile"),

    path("cadastro", views.register, name="register"),

    path('logar', views.login_view, name="login_view"),
    path('logar/criar', views.login_create, name="login_create"),

    path("logout/", views.logout_execute, name="logout"),

    path("atualizar", views.update_profile, name="update_profile"),
]
