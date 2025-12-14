import django.urls

import views

urlpatterns = [
    django.urls.path(
        "institution/create",
        views.InstitutionCreateView.as_view(),
        name="create_institution",
    ),
    django.urls.path(
        "group/create",
        views.GroupCreateView.as_view(),
        name="create_group",
    ),
    django.urls.path(
        "group/list",
        views.GroupListView.as_view(),
        name="group_list"
    ),
    django.urls.path(
        "group/<int:pk>",
        views.
    )
]
