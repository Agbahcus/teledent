import os

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.urls import include, path
from django.views.static import serve as static_serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('', include('dentist.urls')),
    path('', include('consultations.urls')),
]

# In production, Django doesn't serve media files. For hobby/showcase deployments on PaaS
# where you're OK with ephemeral local storage, you can set DJANGO_SERVE_MEDIA=true.
_serve_media = os.environ.get("DJANGO_SERVE_MEDIA", "").strip().lower() in {"1", "true", "yes", "on"}
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif _serve_media:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", static_serve, {"document_root": settings.MEDIA_ROOT}),
    ]
