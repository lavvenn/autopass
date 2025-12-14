__all__ = ["InstitutionCreateView"]

import datetime

import django.contrib.auth.mixins
import django.core.exceptions
import django.http
import django.urls
import django.views.generic

import forms

import models


class InstitutionCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    """Создание учебного заведения"""

    model = models.Institution
    form_class = forms.CreateInstitutionForm
    template_name = "institution_form.html"
    success_url = django.urls.reverse_lazy("")

    def form_valid(self, form):
        institution = form.save(commit=False)
        institution.admin = self.request.user
        institution.save()

        return django.http.HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class GroupCreateView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.CreateView,
):
    """Создание учебной группы"""

    model = models.Group
    form_class = forms.CreateGroupForm
    template_name = "create_group.html"
    success_url = django.urls.reverse_lazy("")

    def form_valid(self, form):
        group = form.save(commit=False)
        group.curator = self.request.user
        group.course = 1
        group.year = datetime.datetime.now().year
        group.save()

        return django.http.HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["course"] = 1
        kwargs["year"] = datetime.datetime.now().year
        return kwargs


class GroupListView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.ListView,
):
    """Список групп"""

    model = models.Group
    template_name = "group_list.html"
    context_object_name = "groups"

    def get_queryset(self):
        user = self.request.user

        if user.role not in ["curator", "administrator"]:
            return self.model.objects.none()

        if user.role == "administrator":
            try:
                institution = models.Institution.objects.get(admin=user)
                return self.model.objects.filter(
                    institution=institution,
                ).select_related(
                    "institution",
                    "curator",
                )

            except models.Institution.DoesNotExist:
                return self.model.objects.none()

        elif user.role == "curator":
            return user.curated_groups.all().select_related(
                "institution",
                "curator",
            )

        return self.model.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_role"] = self.request.user.role
        return context


class GroupDetailView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.DetailView,
):
    """Просмотр группы"""

    model = models.Group
    template_name = "group_detail.html"
    context_object_name = "group"

    def dispatch(self, request, *args, **kwargs):
        group = self.get_object()
        user = request.user

        if not (
            group.curator == user
            or (user.role == "admin" and group.institution.admin == user)
        ):
            raise django.core.exceptions.PermissionDenied(
                "У вас недостаточно прав для просмотра этой страницы",
            )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = context["group"]

        try:
            context["students"] = group.students.all().select_related("user")
        except AttributeError:
            context["students"] = []

        return context
