__all__ = (
    "ActivateUserView",
    "SignUpView",
    "UploadAvatarApiView",
    "UploadAvatarPageView",
)
from datetime import timedelta
import os
import tempfile

import django.conf
import django.contrib.auth.decorators
import django.contrib.auth.models
import django.contrib.messages
import django.core.files.base
import django.core.mail
import django.http
import django.shortcuts
import django.urls
import django.utils.decorators
import django.utils.timezone
import django.views.generic

import organizations.models
import users.forms
import users.models
import users.utils


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

            return django.shortcuts.redirect("users:login-curator")

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


@django.utils.decorators.method_decorator(
    django.contrib.auth.decorators.login_required,
    name="dispatch",
)
class UploadStudentsView(django.views.generic.FormView):
    template_name = "pdf/upload_students.html"
    form_class = users.forms.UploadFileForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.role != "куратор":
            return django.http.HttpResponseNotFound()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        group_name = form.cleaned_data["group_name"]
        uploaded_file = form.cleaned_data["file"]
        delimiter = form.cleaned_data["delimiter"] or ","

        # Проверяем существование групп в обеих системах
        try:
            django.contrib.auth.models.Group.objects.get(name=group_name)
            form.add_error(
                "group_name",
                f"Группа с названием '{group_name}' уже существует",
            )
            return self.form_invalid(form)
        except django.contrib.auth.models.Group.DoesNotExist:
            pass

        try:
            organizations.models.Group.objects.get(name=group_name)
            form.add_error(
                "group_name",
                f"Группа с названием '{group_name}' уже существует",
            )
            return self.form_invalid(form)
        except organizations.models.Group.DoesNotExist:
            pass

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(uploaded_file.name)[1].lower(),
        ) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

            temp_file_path = temp_file.name

        try:
            # Создаем organizations.models.Group, который синхронизирует Django auth Group
            org_group = organizations.models.Group.objects.create(
                name=group_name,
                curator=self.request.user,
                course=1,
            )
            # sync_auth_group вызывается сигналом, но убедимся что он создан
            org_group.sync_auth_group()
            auth_group = org_group.auth_group

            users.utils.get_file(
                file_path=temp_file_path,
                group_name=group_name,
                delimiter=delimiter,
            )
            # GroupLeader должен быть создан сигналом, но проверим
            users.models.GroupLeader.objects.get_or_create(
                group=auth_group,
                curator=self.request.user,
            )
            django.core.mail.send_mail(
                subject=f"Создана группа {group_name}",
                message="Для получения логинов перейдите по ссылке"
                f" - /users/upload/result/{group_name}",
                from_email=django.conf.settings.DEFAULT_FROM_EMAIL,
                recipient_list=[
                    self.request.user.email,
                ],
                fail_silently=False,
            )

            return django.shortcuts.redirect(
                django.urls.reverse(
                    "users:upload-result",
                    kwargs={"group_name": group_name},
                ),
            )

        except Exception as e:
            # Удаляем созданные группы при ошибке
            try:
                if "org_group" in locals():
                    org_group.delete()
                elif "group" in locals():
                    group.delete()
            except Exception:
                pass
            form.add_error("file", f"Ошибка файла: {str(e)}")
            return self.form_invalid(form)

        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


@django.utils.decorators.method_decorator(
    django.contrib.auth.decorators.login_required,
    name="dispatch",
)
class UploadResultView(django.views.generic.TemplateView):
    template_name = "pdf/upload_result.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.role != "куратор":
            return django.http.HttpResponseNotFound()

        group_name = self.kwargs.get("group_name")

        try:
            group = django.contrib.auth.models.Group.objects.get(name=group_name)
        except django.contrib.auth.models.Group.DoesNotExist:
            return django.http.HttpResponseNotFound()

        try:
            users.models.GroupLeader.objects.get(group=group, curator=request.user)
        except users.models.GroupLeader.DoesNotExist:
            return django.http.HttpResponseNotFound()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_name = self.kwargs.get("group_name")

        html_content = users.utils.create_pdf(group_name)
        context["generated_html"] = html_content
        context["group_name"] = group_name

        return context


@django.utils.decorators.method_decorator(
    django.contrib.auth.decorators.login_required,
    name="dispatch",
)
class ResetStudentsView(django.views.generic.FormView):
    template_name = "pdf/reset_students.html"
    form_class = users.forms.ResetStudent

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.role != "куратор":
            return django.http.HttpResponseNotFound()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        token = form.cleaned_data["token"]
        user = users.models.User.objects.filter(username=token)
        if not user.exists() or (user := user.first()).profile.role != "ученик":
            form.add_error(
                "token",
                "Такой студент не существует или у вас нет прав на его изменения",
            )
            return self.form_invalid(form)

        group = user.groups.first()
        try:
            users.models.GroupLeader.objects.get(group=group, curator=self.request.user)
            user.delete()
            new_token = users.utils.create_student(
                *[user.last_name, user.first_name, user.profile.middle_name],
                group_id=group.id,
            )
            django.contrib.messages.success(
                self.request,
                f"Логин был сброшен. \nДанные обновлены в общей таблице "
                f"<a href='/users/upload/result/{group.name}/' "
                f"class='alert-link'>общей таблице</a>. \nНовый логин: {new_token}",
            )
            return django.shortcuts.redirect(self.request.path_info)
        except Exception as e:
            print(e)
            form.add_error(
                "token",
                "Такой студент не существует или у вас нет прав на его изменения",
            )
            return self.form_invalid(form)
