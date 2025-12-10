__all__ = ()

import django.contrib
import django.urls
import django.views.generic

import passes.forms


class PassFormView(django.views.generic.FormView):
    template_name = "passes/pass.html"
    form_class = passes.forms.PassForm

    success_url = django.urls.reverse_lazy("passes:create")

    def form_valid(self, form):
        user = django.contrib.auth.get_user_model()

        user_pass = form.save(commit=False)
        user_pass.user = user.objects.get(pk=self.request.user.id)
        user_pass = form.save()
        django.contrib.messages.success(self.request, "Пропуск сохранён")
        return super().form_valid(form)
