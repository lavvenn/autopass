__all__ = ("CuratorRequiredMixin", "PassRequestsView")
import django.contrib.auth.decorators
import django.http
import django.shortcuts
import django.urls
import django.utils.decorators
import django.views.generic

import passes.models
import users.models


class CuratorRequiredMixin:
    @django.utils.decorators.method_decorator(
        django.contrib.auth.decorators.login_required,
    )
    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.role != "куратор":
            return django.http.HttpResponseNotFound()

        return super().dispatch(request, *args, **kwargs)


class PassRequestsView(CuratorRequiredMixin, django.views.generic.ListView):
    template_name = "curator/pass_requests.html"
    context_object_name = "passes"

    def get_queryset(self):
        led_groups = users.models.GroupLeader.objects.filter(curator=self.request.user)
        group_ids = led_groups.values_list("group__id", flat=True)
        return passes.models.Pass.objects.filter(
            user__groups__id__in=group_ids,
            status__in=[
                "NotFilledIn",
                "NotVerify",
            ],
        ).order_by("user__groups__name")

    def post(self, request, *args, **kwargs):
        pass_id = request.POST.get("pass_id")
        status = request.POST.get("status")

        if pass_id and status in ["Verify", "NotFilledIn"]:
            try:
                pass_obj = passes.models.Pass.objects.get(id=pass_id)
                pass_obj.status = status
                pass_obj.save()
            except passes.models.Pass.DoesNotExist:
                pass

        return django.shortcuts.redirect("curator:pass-requests")
