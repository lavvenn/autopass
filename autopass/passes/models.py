__all__ = ()

import django.contrib.auth.models
import django.db.models
from django.utils.translation import gettext_lazy as _


class Pass(django.db.models.Model):

    class RatingChoices(django.db.models.TextChoices):
        NotVerify = "NotUnVerify", _("Не проверен")
        Verify = "Verify", _("Проверен")
        Printed = "Printed", _("Нейтрально")

    photo = django.db.models.ImageField(
        upload_to="pass_photo/%Y/%m/%d/",
        verbose_name=_("Фото на пропуск"),
    )
    status = django.db.models.CharField(
        "статус",
        choices=RatingChoices,
        default="received",
    )
    user = django.db.models.OneToOneField(
        django.contrib.auth.models.User,
        on_delete=django.db.models.CASCADE,
    )
