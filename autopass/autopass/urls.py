__all__ = ()

import django.contrib
import django.urls

urlpatterns = [
    django.urls.path("admin/", django.contrib.admin.site.urls),
    django.urls.path("organization/", django.urls.include("organizations.urls")),
    django.urls.path("pass/", django.urls.include("passes.urls")),
    django.urls.path("users/", django.urls.include("users.urls")),
]
