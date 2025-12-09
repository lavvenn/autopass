import django.urls

import views

urlpatterns = [
    django.urls.path(
        "institution/create",
        views.InstitutionCreateView.as_view(),
        name="create_institution",
    ),
]
