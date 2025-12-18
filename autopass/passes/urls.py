import django.urls

import passes.views

app_name = "passes"


urlpatterns = [
    django.urls.path("create/", passes.views.PassFormView.as_view(), name="create"),
]
