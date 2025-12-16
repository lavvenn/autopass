__all__ = (
    "ActivateUserView",
    "SignUpView",
    "UploadAvatarApiView",
    "UploadAvatarPageView",
)
from datetime import timedelta

import django.conf
import django.contrib.auth.decorators
import django.contrib.auth.models
import django.core.files.base
import django.core.mail
import django.http
import django.shortcuts
import django.utils.decorators
import django.utils.timezone
import django.views.generic

import users.forms
import users.models


class SignUpView(django.views.generic.View):
    def get(self, request):
        personal_form = users.forms.SignupForm()
        return django.shortcuts.render(
            request,
            "users/signup.html",
            {
                "personal_form": personal_form,
            },
        )

    def post(self, request):
        personal_form = users.forms.SignupForm(request.POST)
        if personal_form.is_valid():
            user = personal_form.save(commit=False)
            user.is_active = django.conf.settings.DEFAULT_USER_IS_ACTIVE
            user.save()
            users.models.Profile.objects.create(
                user=user,
                role="куратор",
            )
            if not user.is_active:
                django.core.mail.send_mail(
                    subject="Подтвердите вашу почту",
                    message="Для подтверждения почты перейдите по ссылке"
                    f" - /activate/{user.username}",
                    from_email=django.conf.settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[
                        users.models.User.objects.normalize_email(user.email),
                    ],
                    fail_silently=False,
                )

            return django.shortcuts.redirect("users:login")

        return django.shortcuts.render(
            request,
            "users/signup.html",
            {
                "personal_form": personal_form,
            },
        )


class ActivateUserView(django.views.generic.View):

    def get(self, request, username):
        try:
            base_query = django.contrib.auth.models.User.objects
            user = base_query.get(username=username)
            try:
                user_profile = user.profile
                if user_profile.attempts_time is not None:
                    if (
                        django.utils.timezone.now() - user_profile.attempts_time
                        <= timedelta(
                            days=7,
                        )
                    ):
                        user.is_active = True
                        user.save()
                        user_profile.attempts_time = None
                        user_profile.attempts_count = 0
                        user_profile.save()
                        return django.shortcuts.render(
                            request,
                            "users/activate_done.html",
                        )

            except Exception:
                pass

            user = base_query.get(username=username)
            if user.profile.attempts_time is None:
                if django.utils.timezone.now() - user.date_joined <= timedelta(
                    hours=12,
                ):
                    user.is_active = True
                    user.save()
                    return django.shortcuts.render(
                        request,
                        "users/activate_done.html",
                    )

        except Exception:

            raise django.http.Http404()

        raise django.http.Http404()


@django.utils.decorators.method_decorator(
    django.contrib.auth.decorators.login_required,
    name="dispatch",
)
class UploadAvatarPageView(django.views.generic.View):

    def get(self, request):
        if request.user.profile.role == "куратор":
            return django.http.HttpResponseNotFound()

        return django.shortcuts.render(request, "users/profile_form.html")


@django.utils.decorators.method_decorator(
    django.contrib.auth.decorators.login_required,
    name="dispatch",
)
class UploadAvatarApiView(django.views.generic.View):
    def post(self, request):
        if request.user.profile.role == "куратор":
            return django.http.HttpResponseNotFound()

        if "avatar" not in request.FILES:
            return django.http.JsonResponse(
                {"status": "error", "message": "Файл не найден"},
                status=400,
            )

        try:
            avatar_file = request.FILES["avatar"]

            if avatar_file.size > 5 * 1024 * 1024:
                return django.http.JsonResponse(
                    {"status": "error", "message": "Файл слишком большой (макс. 5MB)"},
                    status=400,
                )

            profile = request.user.profile

            if profile.avatar:
                profile.avatar.delete(save=False)

            profile.avatar.save(
                f"avatar_{request.user.id}.jpg",
                django.core.files.base.ContentFile(avatar_file.read()),
            )
            profile.save()

            return django.http.JsonResponse(
                {
                    "status": "success",
                    "message": "Фото успешно загружено",
                    "avatar_url": profile.avatar.url,
                },
            )

        except Exception:
            return django.http.JsonResponse(
                {"status": "error", "message": "Ошибка сервера"},
                status=500,
            )
