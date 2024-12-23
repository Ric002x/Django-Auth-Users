from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("", views.profile, name="profile"),

    path("register", views.register, name="register"),
    path("login", views.login_, name="login"),
    path("logout", views.logout_execute, name="logout"),

    path("update", views.update_profile, name="update_profile"),
    path('password', views.update_password, name="update_password"),


    path('api/v1/register', views.CreateUserAPIView.as_view()),
    path('api/v1/login', views.LoginUserAPIView.as_view()),

    path("api/v1/me", views.UserAPIView.as_view()),
    path('api/v1/me/password', views.UserChangePasswordAPIView.as_view())
]
