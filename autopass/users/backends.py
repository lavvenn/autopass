__all__ = ["EmailOrUsernameModelBackend"]

import django.conf
import django.contrib
import django.contrib.auth.backends
import django.core.exceptions
import django.core.mail
import django.core.validators
import django.urls
import django.utils.timezone

from users.models import Profile, User


class EmailOrUsernameModelBackend(django.contrib.auth.backends.ModelBackend):
    def _is_email(self, value):
        try:
            django.core.validators.validate_email(value)
            return True
        except django.core.exceptions.ValidationError:
            return False

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        if username == password:
            user = User.objects.get(username=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

            return None

        if self._is_email(username):
            normalized_email = User.objects.normalize_email(username)
            user = User.objects.by_mail(normalized_email)
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        if not user:
            return None

        profile, _ = Profile.objects.get_or_create(user=user)

        if user.check_password(password) and self.user_can_authenticate(user):
            if profile.attempts_count > 0:
                profile.attempts_count = 0
                profile.save()

            return user

        profile.attempts_count += 1
        profile.save()
        if profile.attempts_count >= django.conf.settings.MAX_AUTH_ATTEMPTS:
            user.is_active = False
            profile.attempts_time = django.utils.timezone.now()
            user.save()
            profile.save()
            if request:
                django.contrib.messages.error(
                    request,
                    "Достигнут лимит неправильных входов",
                )

            django.core.mail.send_mail(
                subject="Активация аккаунта",
                message=(
                    "Превышен лимит ошибок"
                    "Для подтверждения личности перейдите -"
                    f"users/activate/{user.username}"
                ),
                from_email=django.conf.settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        profile.save()
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
