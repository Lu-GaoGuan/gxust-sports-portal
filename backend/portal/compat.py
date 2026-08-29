from enum import Enum


def apply_simpleui_enum_compatibility():
    """Allow SimpleUI to serialize Django 6.1 admin action locations."""
    from simpleui.templatetags.simpletags import LazyEncoder

    if getattr(LazyEncoder, "_portal_enum_compatibility", False):
        return

    original_default = LazyEncoder.default

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return original_default(self, obj)

    LazyEncoder.default = default
    LazyEncoder._portal_enum_compatibility = True
