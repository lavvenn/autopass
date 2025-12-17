import django.urls

import organizations.views

urlpatterns = [
    django.urls.path(
        "institution/create",
        organizations.views.InstitutionCreateView.as_view(),
        name="create_institution",
    ),
    django.urls.path(
        "group/create",
        organizations.views.GroupCreateView.as_view(),
        name="create_group",
    ),
    django.urls.path("group/list", organizations.views.GroupListView.as_view(), name="group_list"),
    django.urls.path(
        "group/<int:pk>",
        organizations.views.GroupDetailView.as_view(),
        name="group_detail",
    ),
]
