__all__ = ["CreateInstitutionForm"]

import django.core.validators
import django.forms

import models


class CreateInstitutionForm(django.forms.ModelForm):
    """Форма для создания учебного заведения"""

    class Meta:
        model = models.Institution
        fields = [
            "name",
            "short_name",
            "information",
            "logo",
        ]
        widgets = {
            "name": django.forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Название организации",
                },
            ),
            "short_name": django.forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Сокращенное название орзанизации",
                },
            ),
            "information": django.forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Описание",
                },
            ),
        }
        labels = {
            "name": "Название учебного заведения",
            "short_name": "Краткое название",
            "information": "Описание",
            "logo": "Логотип",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.admin = self.user

        if commit:
            instance.save()

        return instance

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        short_name = cleaned_data.get("short_name")

        if name and short_name and len(short_name) >= len(name):
            self.add_error(
                "short_name",
                "Краткое название должно быть меньше основного.",
            )

        return cleaned_data

    def clean_short_name(self):
        short_name = self.cleaned_data["short_name"]
        if len(short_name) <= 2:
            raise django.forms.ValidationError(
                message="Краткое название должно быть больше 2 символов.",
            )

        return short_name


class CreateGroupForm(django.forms.ModelForm):
    """Форма для создания учебной группы"""

    class Meta:
        model = models.Group
        fields = [
            "name",
            "course",
        ]
        widgets = {
            "name": django.forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название группы",
                },
            ),
        }
        labels = {
            "name": "Название  группы",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.institution = kwargs.pop("institution", None)
        super().__init__(*args, **kwargs)

        if self.institution:
            self.fields["institution"].initial = self.institution

        if self.user and self.user.role == "curator":
            pass

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.curator = self.user

        if commit:
            instance.save()

        return instance

    def clean(self):
        name = self.cleaned_data["name"]
        if len(name) <= 2:
            raise django.forms.ValidationError(
                message="Название должно быть больше 2 символов.",
            )

        return name
