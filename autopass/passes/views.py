__all__ = ()

import shutil
import tempfile

import django.contrib
import django.contrib.admin.views.decorators
import django.views.generic

import card_maker.card_maker
import passes.models


@django.utils.decorators.method_decorator(
    django.contrib.admin.views.decorators.staff_member_required,
    name="dispatch",
)
class GroupsView(django.views.generic.ListView):
    template_name = "passes/group.html"
    context_object_name = "groups"
    model = django.contrib.auth.models.Group

    def get_queryset(self):
        return django.contrib.auth.models.Group.objects.all()


@django.utils.decorators.method_decorator(
    django.contrib.admin.views.decorators.staff_member_required,
    name="dispatch",
)
class DownloadAllGroupPassesView(django.views.generic.View):
    def get(self, request, group_id):

        group = django.contrib.auth.models.Group.objects.get(pk=group_id)
        passes_list = passes.models.Pass.objects.filter(
            user__groups=group,
            status="Verify",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            for pass_obj in passes_list:
                name = f"{pass_obj.user.first_name} {pass_obj.user.last_name}"

                im = card_maker.card_maker.ImageEditor(
                    template_path="template.png",
                    output_path=temp_dir,
                    circle_size=(250, 250),
                    photo_position=(50, 100),
                    text_position=(350, 400),
                )

                im.create_final_image(
                    image_path=pass_obj.user.profile.avatar.path,
                    text=name,
                    final_name=f"{name}.png",
                )

            zip_path = f"/tmp/{group.name}.zip"
            shutil.make_archive(zip_path.replace(".zip", ""), "zip", temp_dir)

            with open(zip_path, "rb") as f:
                file_content = f.read()

            response = django.http.HttpResponse(
                file_content,
                content_type="application/zip",
            )
            response["Content-Disposition"] = f'attachment; filename="{group.name}.zip"'
            return response
