__all__ = ()

from django.contrib import admin, auth

from users.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile

    can_delete = False


class UserAdmin(auth.admin.UserAdmin):

    inlines = [ProfileInline]


admin.site.unregister(auth.models.User)
admin.site.register(auth.models.User, UserAdmin)
