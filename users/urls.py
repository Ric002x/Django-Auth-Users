from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path('api/v1/register', views.CreateUserAPIView.as_view()),
    path('api/v1/login', views.LoginUserAPIView.as_view()),

    path("api/v1/me", views.UserAPIView.as_view()),
    path('api/v1/me/password', views.UserChangePasswordAPIView.as_view())
]
