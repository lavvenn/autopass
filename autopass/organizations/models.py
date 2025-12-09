__all__ = ["Group", "Institution"]

import django.core.validators
import django.db.models


class Institution(django.db.models.Model):
    """Учебное заведение"""

    class Meta:
        verbose_name = "учебное заведение"
        verbose_name_plural = "учебные заведения"

    name = django.db.models.CharField(
        "название учебного заведения",
        max_length=255,
    )
    short_name = django.db.models.CharField(
        "краткое название",
        max_length=50,
    )
    logo = django.db.models.ImageField(
        "логотип учебного заведения",
        upload_to="institutions/",
        blank=True,
        null=True,
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
    )
    year = django.db.models.DateField(
        "год поступления",
    )

    def __str__(self):
        return f"{self.name} ({self.course} курс)"
