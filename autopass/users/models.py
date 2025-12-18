__all__ = ("Profile", "User", "UserManager", "GroupLeader")
import sys

import django.contrib.auth
import django.contrib.auth.models
import django.db.models
import django.db.models.signals
import django.dispatch


user = django.contrib.auth.get_user_model()

if "makemigrations" not in sys.argv and "migrate" not in sys.argv:
    user._meta.get_field("email")._unique = True


class UserManager(django.contrib.auth.models.UserManager):

    @classmethod
    def normalize_email(cls, email):
        if "@" not in email:
            return email

        email = super().normalize_email(email or "").lower().strip()
        local, domain = email.split("@")
        local = local.split("+")[0]
        if domain in ["ya.ru", "yandex.ru"]:
            domain = "yandex.ru"
            local = local.replace(".", "-")
        elif domain == "gmail.com":
            local = local.replace(".", "")

        return f"{local}@{domain}"

    def by_mail(self, email):
        if not email:
            return None

        return (
            self.get_queryset().filter(email__iexact=email, email__isnull=False).first()
        )

    def active(self):
        return self.get_queryset().filter(is_active=True).select_related("profile")


class User(django.contrib.auth.models.User):
    objects = UserManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if self.email:
            normalized_email = self.__class__.objects.normalize_email(
                self.email,
            )

            if normalized_email:
                self.email = normalized_email

            self.full_clean()

        super().save(*args, **kwargs)


class Profile(django.db.models.Model):
    user = django.db.models.OneToOneField(
        django.contrib.auth.models.User,
        on_delete=django.db.models.CASCADE,
        related_name="profile",
        verbose_name="ученик",
        help_text="Связь с пользователем",
    )
    role = django.db.models.CharField(max_length=50)
    avatar = django.db.models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
    )
    middle_name = django.db.models.CharField(max_length=50)
    attempts_count = django.db.models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name="ошибочных попыток входа",
    )
    attempts_time = django.db.models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="время блокировки",
    )


class GroupLeader(django.db.models.Model):
    group = django.db.models.OneToOneField(
        django.contrib.auth.models.Group,
        on_delete=django.db.models.CASCADE,
        related_name="leader",
    )
    curator = django.db.models.ForeignKey(
        django.contrib.auth.models.User,
        on_delete=django.db.models.CASCADE,
        related_name="led_groups",
    )
    created_at = django.db.models.DateTimeField(auto_now_add=True)


@django.dispatch.receiver(django.db.models.signals.post_save, sender=GroupLeader)
def sync_group_leader_on_save(sender, instance, created, **kwargs):
    """Синхронизировать organizations.models.Group при создании GroupLeader"""
    if created:
        # Проверяем, есть ли уже organizations.models.Group для этого auth_group
        try:
            import organizations.models

            org_group = organizations.models.Group.objects.get(
                auth_group=instance.group,
            )
            # Обновляем куратора если нужно
            if org_group.curator != instance.curator:
                org_group.curator = instance.curator
                org_group.save()
        except organizations.models.Group.DoesNotExist:
            # Создаем organizations.models.Group если его нет
            try:
                import organizations.models

                # Ищем группу с таким именем без auth_group
                try:
                    org_group = organizations.models.Group.objects.get(
                        name=instance.group.name,
                        auth_group__isnull=True,
                    )
                    # Связываем существующую группу с auth_group
                    org_group.auth_group = instance.group
                    org_group.curator = instance.curator
                    org_group.save()
                except organizations.models.Group.DoesNotExist:
                    # Создаем новую группу
                    organizations.models.Group.objects.create(
                        name=instance.group.name,
                        curator=instance.curator,
                        course=1,
                        auth_group=instance.group,
                    )
            except Exception:
                # Игнорируем ошибки при синхронизации
                pass
