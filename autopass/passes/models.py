__all__ = ()

import django.contrib.auth.models
import django.db.models
from django.utils.translation import gettext_lazy as _


class Pass(django.db.models.Model):

    class RatingChoices(django.db.models.TextChoices):
        NotFilledIn = "NotFilledIn", "Не заполнено"
        NotVerify = "NotVerify", _("Не проверен")
        Verify = "Verify", _("Проверен")
        Printed = "Printed", _("Нейтрально")

    status = django.db.models.CharField(
        "статус",
        choices=RatingChoices,
        default="NotFilledIn",
    )
    user = django.db.models.OneToOneField(
        django.contrib.auth.models.User,
        related_name="user_pass",
        on_delete=django.db.models.CASCADE,
    )
