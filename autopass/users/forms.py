__all__ = (
    "AvatarUploadForm",
    "LoginCode",
    "LoginForm",
    "SignupForm",
)
import django.contrib.auth
import django.contrib.auth.forms
import django.contrib.auth.models
import django.core.exceptions
import django.forms

import users.models


class LoginCode(django.contrib.auth.forms.AuthenticationForm):
    code = django.forms.CharField(
        label="Код",
        max_length=100,
        widget=django.forms.TextInput(attrs={"autofocus": True}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)
        self.fields.pop("password", None)

        self.fields = {"code": self.fields["code"]}

    def clean(self):
        code = self.cleaned_data.get("code")
        if code is not None:
            self.user_cache = django.contrib.auth.authenticate(
                self.request,
                username=code,
                password=code,
            )
            if self.user_cache is None:
                raise django.core.exceptions.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                    params={"code": code},
                )

            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class LoginForm(django.contrib.auth.forms.AuthenticationForm):
    username = django.forms.CharField(
        label="Логин или почта",
    )
    password = django.forms.CharField(
        widget=django.forms.PasswordInput(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs.update({"class": "form-control"})


class SignupForm(django.contrib.auth.forms.UserCreationForm):

    class Meta(django.contrib.auth.forms.UserCreationForm.Meta):
        model = users.models.User
        fields = ("username", "email", "password1", "password2")
        labels = {
            "username": "Никнейм",
            "email": "Почта",
            "password1": "Пароль",
            "password2": "Повторите пароль",
        }
        help_texts = {
            "name": "Введите ваш никнейм",
            "email": "Введите почту, к которой вы имеете доступ",
            "password1": "Придумайте пароль",
            "password2": "Повторите пароль",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        for field in self.visible_fields():
            field.field.widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password1")

        if username and password and username == password:
            raise django.forms.ValidationError("Логин и пароль не могут совпадать.")

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            normalized_email = users.models.User.objects.normalize_email(email)
            if (
                normalized_email
                and users.models.User.objects.filter(email=normalized_email).exists()
            ):
                raise django.forms.ValidationError(
                    "Пользователь с такой почтой уже существует.",
                )

            self.cleaned_data["email"] = normalized_email or email

        return self.cleaned_data.get("email")


class AvatarUploadForm(django.forms.Form):
    avatar = django.forms.ImageField(
        label="Выберите фото",
        widget=django.forms.FileInput(
            attrs={"accept": "image/*", "class": "form-control", "id": "photo-input"},
        ),
    )


class UploadFileForm(django.forms.Form):
    group_name = django.forms.CharField(
        label="Название группы",
        max_length=100,
        required=True,
        widget=django.forms.TextInput(
            attrs={"placeholder": "Курс 2025 1"},
        ),
    )
    file = django.forms.FileField(
        label="Файл с данными учеников",
        required=True,
        widget=django.forms.FileInput(
            attrs={"accept": ".csv,.xls,.xlsx,.ods"},
        ),
    )
    delimiter = django.forms.CharField(
        label="Разделитель CSV (если применимо)",
        max_length=10,
        required=False,
        initial=",",
        widget=django.forms.TextInput(
            attrs={"placeholder": ","},
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        for field in self.visible_fields():
            field.field.widget.attrs.update({"class": "form-control"})


class ResetStudent(django.forms.Form):
    token = django.forms.CharField(
        label="Уникальный код",
        max_length=150,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs.update({"class": "form-control"})
