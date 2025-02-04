from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path('register', views.CreateUserAPIView.as_view()),
    path('login', views.LoginUserAPIView.as_view()),

    path("me", views.UserAPIView.as_view()),
    path('me/password', views.UserChangePasswordAPIView.as_view()),

    path('auth/google', views.OAuthLogin.as_view()),
]
