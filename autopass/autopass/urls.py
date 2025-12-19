__all__ = ()

import django.conf
from django.conf.urls.static import static
import django.contrib
import django.urls

urlpatterns = [
    django.urls.path("", django.urls.include("homepage.urls")),
    django.urls.path("admin/", django.contrib.admin.site.urls),
    django.urls.path("pass/", django.urls.include("passes.urls")),
    django.urls.path("users/", django.urls.include("users.urls")),
    django.urls.path("curator/", django.urls.include("curator.urls")),
]


if django.conf.settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()

    urlpatterns += static(
        django.conf.settings.MEDIA_URL,
        document_root=django.conf.settings.MEDIA_ROOT,
    )

    urlpatterns += static(
        django.conf.settings.STATIC_URL,
        document_root=django.conf.settings.STATICFILES_DIRS[0],
    )
