__all__ = []
import django.contrib.auth.views
from django.urls import path

import users.forms
import users.views

app_name = "users"

urlpatterns = [
    path(
        "login/student",
        django.contrib.auth.views.LoginView.as_view(
            template_name="users/login-student.html",
            authentication_form=users.forms.LoginCode,
        ),
        name="login-student",
    ),
    path(
        "login/curator",
        django.contrib.auth.views.LoginView.as_view(
            template_name="users/login-curator.html",
            authentication_form=users.forms.LoginForm,
        ),
        name="login-curator",
    ),
    path(
        "logout/",
        django.contrib.auth.views.LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
    path(
        "signup/",
        users.views.SignUpView.as_view(),
        name="signup",
    ),
    path(
        "activate/<str:username>/",
        users.views.ActivateUserView.as_view(),
        name="activate",
    ),
    path("profile/avatar/", users.views.UploadAvatarPageView.as_view(), name="profile"),
    path(
        "avatar/upload/api/",
        users.views.UploadAvatarApiView.as_view(),
        name="upload-avatar-api",
    ),
]
