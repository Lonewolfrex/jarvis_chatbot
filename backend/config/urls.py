from django.contrib import admin
from django.urls import path, include
# Add these two missing imports:
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/chat/", include("chat.urls")),
    path('', include('frontend_ui.urls')),
]

# This will now execute perfectly without throwing a NameError
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)