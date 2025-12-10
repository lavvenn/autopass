__all__ = ["InstitutionCreateView"]

import django.contrib.auth.mixins
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


