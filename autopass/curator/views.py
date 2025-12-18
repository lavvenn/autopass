import django.views.generic
import django.shortcuts
import django.urls
import django.http
import django.contrib.auth.decorators
import django.utils.decorators
import passes.models


@django.utils.decorators.method_decorator(
    django.contrib.auth.decorators.login_required,
    name="dispatch",
)
class PassRequestsView(django.views.generic.ListView):
    template_name = "curator/pass_requests.html"
    context_object_name = "passes"

    def get_queryset(self):
        return passes.models.Pass.objects.all()

    def post(self, request, *args, **kwargs):
        pass_id = request.POST.get("pass_id")
        status = request.POST.get("status")

        if pass_id and status in ["принят", "отклонен"]:
            try:
                pass_obj = passes.models.Pass.objects.get(id=pass_id)
                pass_obj.status = status
                pass_obj.save()
            except passes.models.Pass.DoesNotExist:
                pass

        return django.shortcuts.redirect("curator:pass-requests")