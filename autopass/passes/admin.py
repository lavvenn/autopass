__all__ = ()

import django.contrib.admin

import passes.models


@django.contrib.admin.register(passes.models.Pass)
class PassAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        "user",
        "status",
    )
