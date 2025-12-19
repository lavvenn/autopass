import django.urls

import passes.views

app_name = "passes"


urlpatterns = [
    django.urls.path("groups/", passes.views.GroupsView.as_view(), name="groups"),
    django.urls.path(
        "groups/<int:group_id>/download/",
        passes.views.DownloadAllGroupPassesView.as_view(),
        name="download_group_passes",
    ),
]
