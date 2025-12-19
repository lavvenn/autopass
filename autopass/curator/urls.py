__all__ = []
import django.urls

import curator.views

app_name = "curator"


urlpatterns = [
    django.urls.path(
        "requests/",
        curator.views.PassRequestsView.as_view(),
        name="pass-requests",
    ),
]
