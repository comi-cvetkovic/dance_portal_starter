from django.contrib import admin
from django.urls import path, include
from core.views import CustomLoginView, custom_logout_view
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path("accounts/logout/", custom_logout_view, name="logout"),
    path('', include('core.urls')),
    path("i18n/", include("django.conf.urls.i18n")),  # language switcher
]

# Wrap your app's URLs in i18n_patterns (✅ allowed here at root)
# urlpatterns += i18n_patterns(
#     path("", include("core.urls")),
# )

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



