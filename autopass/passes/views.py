__all__ = ()

import django.contrib
import django.urls
import django.views.generic

import card_maker.card_maker
import passes.models


class PassFormView(django.views.generic.FormView):
    template_name = "passes/pass.html"

    success_url = django.urls.reverse_lazy("passes:create")

    def form_valid(self, form):
        user = django.contrib.auth.get_user_model()
        user_pass = form.save(commit=False)
        user_pass.user = user.objects.get(pk=self.request.user.id)
        user_pass = form.save()

        name = f"{self.request.user.first_name} {self.request.user.last_name}"

        im = card_maker.card_maker.ImageEditor(
            template_path="template.png",
            output_path="output",
            circle_size=(250, 250),
            photo_position=(50, 100),
            text_position=(350, 400),
        )

        im.create_final_image(
            image_path=passes.models.Pass.objects.get(
                user=user.objects.get(pk=self.request.user.id),
            ).photo.path,
            text=name,
            final_name=f"{name}.png",
        )
        django.contrib.messages.success(self.request, "Пропуск сохранён")
        return super().form_valid(form)
