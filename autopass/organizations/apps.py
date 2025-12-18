__all__ = ["OrganizationsConfig"]

import django.apps


class OrganizationsConfig(django.apps.AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organizations"
