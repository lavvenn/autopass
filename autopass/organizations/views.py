__all__ = [
    "GroupCreateView",
    "GroupDetailView",
    "GroupListView",
    "InstitutionCreateView",
]

import django.contrib.auth.mixins
import django.core.exceptions
import django.urls
import django.views.generic

import organizations.forms
import organizations.models


class InstitutionCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    """Создание учебного заведения"""

    model = organizations.models.Institution
    form_class = organizations.forms.CreateInstitutionForm
    template_name = "organizations/institution_form.html"
    success_url = django.urls.reverse_lazy("organizations:create_institution")

    def form_valid(self, form):
        institution = form.save(commit=False)
        institution.admin = self.request.user
        institution.save()

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class GroupCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    """Создание учебной группы"""

    model = organizations.models.Group
    form_class = organizations.forms.CreateGroupForm
    template_name = "organizations/create_group.html"
    success_url = django.urls.reverse_lazy("organizations:create_group")

    def form_valid(self, form):
        group = form.save(commit=False)
        group.curator = self.request.user
        group.course = 1
        group.save()

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class GroupListView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.ListView,
):
    """Список групп"""

    model = organizations.models.Group
    template_name = "organizations/group_list.html"
    context_object_name = "groups"

    def get_queryset(self):
        user = self.request.user

        if user.profile.role not in ["curator", "administrator"]:
            return self.model.objects.none()

        if user.profile.role == "administrator":
            try:
                institution = organizations.models.Institution.objects.get(admin=user)
                return self.model.objects.filter(
                    institution=institution,
                ).select_related(
                    "institution",
                    "curator",
                )

            except organizations.models.Institution.DoesNotExist:
                return self.model.objects.none()

        elif user.profile.role == "curator":
            return user.curated_groups.all().select_related(
                "institution",
                "curator",
            )

        return self.model.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_role"] = self.request.user.profile.role
        return context


class GroupDetailView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.DetailView,
):
    """Просмотр группы"""

    model = organizations.models.Group
    template_name = "organizations/group_detail.html"
    context_object_name = "group"

    def dispatch(self, request, *args, **kwargs):
        group = self.get_object()
        user = request.user

        if not (
            group.curator == user
            or (user.profile.role == "admin" and group.institution.admin == user)
        ):
            raise django.core.exceptions.PermissionDenied(
                "У вас недостаточно прав для просмотра этой страницы",
            )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = context["group"]

        # Используем свойство students из модели
        context["students"] = group.students

        return context
