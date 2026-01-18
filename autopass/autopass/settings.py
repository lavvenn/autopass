__all__ = ()

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

MAX_AUTH_ATTEMPTS = 5


load_dotenv()


def is_true(value):
    return value.lower() in {"true", "t", "1", "yes", "y", "on", ""}


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fake-key")

DEBUG = is_true(os.getenv("DJANGO_DEBUG", "true"))

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # created apps
    "curator.apps.CuratorConfig",
    "passes.apps.PassConfig",
    "users.apps.UsersConfig",
    "homepage.apps.HomepageConfig",
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

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

    INTERNAL_IPS = ["127.0.0.1"]


ROOT_URLCONF = "autopass.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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


LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [BASE_DIR / "static_dev"]
STATIC_URL = "/static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/users/login/student"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/users/login/student"

AUTHENTICATION_BACKENDS = [
    "users.backends.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

DEFAULT_USER_IS_ACTIVE = is_true(os.getenv("DJANGO_DEFAULT_USER_IS_ACTIVE", "false"))

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "send_mail"

DEFAULT_FROM_EMAIL = os.getenv("DJANGO_MAIL", "example@example.com")
APPEND_SLASH = True


MEDIA_URL = "/media/"


MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


MAIL = os.getenv(
    "DJANGO_MAIL",
    "fake_email@django.com",
)
