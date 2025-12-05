__all__ = ("ProfileStudent",)
import django.contrib.auth
import django.contrib.auth.models
import django.db.models
import django.templatetags.static


class ProfileStudent(django.db.models.Model):
    user = django.db.models.OneToOneField(
        django.contrib.auth.models.User,
        on_delete=django.db.models.CASCADE,
        related_name="profile",
        verbose_name="ученик",
        help_text="Связь с пользователем",
    )
    middle_name = django.db.models.CharField(max_length=50)
    image = django.db.models.ImageField(
        upload_to="photos/",
        verbose_name="фото",
        help_text="Фото пользователя",
        null=True,
        blank=True,
    )
