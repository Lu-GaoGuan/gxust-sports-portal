from django.apps import AppConfig
from django.conf import settings


class PortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portal"
    verbose_name = "体育部网站内容"

    def ready(self):
        from .compat import apply_simpleui_enum_compatibility

        apply_simpleui_enum_compatibility()
        frame_middleware = "django.middleware.clickjacking.XFrameOptionsMiddleware"
        if frame_middleware not in settings.MIDDLEWARE:
            settings.MIDDLEWARE.append(frame_middleware)
