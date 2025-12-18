__all__ = ["Group", "Institution"]

import datetime

import django.contrib.auth.models
import django.core.validators
import django.db.models
import django.db.models.signals
import django.dispatch

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
    auth_group = django.db.models.OneToOneField(
        django.contrib.auth.models.Group,
        verbose_name="группа Django",
        on_delete=django.db.models.CASCADE,
        related_name="org_group",
        null=True,
        blank=True,
    )

    def __str__(self):
        institution_name = (
            self.institution.short_name if self.institution else "Без организации"
        )
        return f"{self.name} ({institution_name})"

    @property
    def students(self):
        """Получить всех студентов группы через Django auth Group"""
        if self.auth_group:
            return users.models.Profile.objects.filter(
                user__groups=self.auth_group,
                role="ученик",
            ).select_related("user")
        return users.models.Profile.objects.none()

    def sync_auth_group(self):
        """Синхронизировать Django auth Group с этой группой"""
        if not self.auth_group:
            auth_group, created = django.contrib.auth.models.Group.objects.get_or_create(
                name=self.name,
            )
            self.auth_group = auth_group
            self.save(update_fields=["auth_group"])

            # Создать GroupLeader если его нет
            if created:
                users.models.GroupLeader.objects.get_or_create(
                    group=auth_group,
                    curator=self.curator,
                )
        else:
            # Обновить название если изменилось
            if self.auth_group.name != self.name:
                self.auth_group.name = self.name
                self.auth_group.save()

            # Синхронизировать куратора
            try:
                group_leader = self.auth_group.leader
                if group_leader.curator != self.curator:
                    group_leader.curator = self.curator
                    group_leader.save()
            except users.models.GroupLeader.DoesNotExist:
                users.models.GroupLeader.objects.create(
                    group=self.auth_group,
                    curator=self.curator,
                )


@django.dispatch.receiver(django.db.models.signals.post_save, sender=Group)
def sync_group_on_save(sender, instance, created, **kwargs):
    """Синхронизировать группу при сохранении"""
    instance.sync_auth_group()


@django.dispatch.receiver(django.db.models.signals.pre_delete, sender=Group)
def sync_group_on_delete(sender, instance, **kwargs):
    """Удалить связанную Django auth Group при удалении группы"""
    if instance.auth_group:
        # Удалить GroupLeader сначала
        try:
            instance.auth_group.leader.delete()
        except users.models.GroupLeader.DoesNotExist:
            pass
        # Удалить auth_group
        instance.auth_group.delete()
