__all__ = ()

import django.views.generic


class HomeView(django.views.generic.TemplateView):
    template_name = "homepage/home.html"
    context_object_name = "items"
