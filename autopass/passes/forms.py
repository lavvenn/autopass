__all__ = ()

import django.forms

import passes.models


class PassForm(django.forms.ModelForm):
    class Meta:
        model = passes.models.Pass
        fields = (passes.models.Pass.photo.field.name,)
