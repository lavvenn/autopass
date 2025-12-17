__all__ = ["Group", "Institution"]

import datetime

import django.core.validators
import django.db.models

import users.models


class Institution(django.db.models.Model):
    """Учебное заведение"""

    class Meta:
        verbose_name = "учебное заведение"
        verbose_name_plural = "учебные заведения"

    name = django.db.models.CharField(
        "название учебного заведения",
        max_length=255,
        unique=True,
    )
    short_name = django.db.models.CharField(
        "краткое название",
        max_length=50,
        unique=True,
    )
    information = django.db.models.TextField(
        "описание",
        validators=[
            django.core.validators.MaxLengthValidator(
                limit_value=5000,
            ),
        ],
    )
    logo = django.db.models.ImageField(
        "логотип учебного заведения",
        upload_to="institutions/",
        blank=True,
        null=True,
        validators=[
            django.core.validators.FileExtensionValidator(
                allowed_extensions=[
                    "png",
                    "jpg",
                    "svg",
                ],
                message="Недопустимый формат изображения",
            ),
        ],
    )
    admin = django.db.models.ForeignKey(
        users.models.User,
        verbose_name="администратор организации",
        on_delete=django.db.models.CASCADE,
        related_name="created_institutions",
    )

    def __str__(self):
        return self.short_name


class Group(django.db.models.Model):
    """Учебная группа"""

    class Meta:
        verbose_name = "группа"
        verbose_name_plural = "группы"

    name = django.db.models.CharField(
        "название группы",
        max_length=50,
    )
    course = django.db.models.IntegerField(
        "курс",
        validators=[
            django.core.validators.MinValueValidator(
                1,
                "Курс обучения не может быть меньше 1",
            ),
            django.core.validators.MaxValueValidator(6, "Курс не может быть больше 6"),
        ],
        default=1,
    )
    year = django.db.models.DateField(
        "год поступления",
        default=datetime.date(datetime.datetime.now().year, 1, 1),
    )
    curator = django.db.models.ForeignKey(
        users.models.User,
        verbose_name="куратор",
        on_delete=django.db.models.CASCADE,
        related_name="curated_groups",
        limit_choices_to={
            "role": "curator",
        },
    )
    institution = django.db.models.ForeignKey(
        "Institution",
        verbose_name="учебное заведение",
        on_delete=django.db.models.CASCADE,
        related_name="groups",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name} ({self.institution.short_name})"
