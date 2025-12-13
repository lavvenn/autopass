import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-pbqa4ecco@!fdglq$rcwib*cth*jiwq96@8(73=$n&sjdx=6k6"

DEBUG = True

ALLOWED_HOSTS = []

TRUE_VALUE = {
    "true",
    "yes",
    "1",
    "t",
    "y",
    "",
    "True",
    "YES",
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # users apps
    "users.apps.UsersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "autopass.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "autopass.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}


name = "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": name,
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [BASE_DIR / "static_dev"]
STATIC_URL = "/static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/users/login/student"
LOGIN_REDIRECT_URL = "/users/login/student"
LOGOUT_REDIRECT_URL = "/users/login/student"

AUTHENTICATION_BACKENDS = [
    "users.backends.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

DEFAULT_USER_IS_ACTIVE = os.getenv("DJANGO_DEFAULT_USER_IS_ACTIVE", 0) in TRUE_VALUE

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "send_mail"

DEFAULT_FROM_EMAIL = os.getenv("DJANGO_MAIL", "example@example.com")
APPEND_SLASH = True


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
