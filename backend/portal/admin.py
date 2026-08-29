from django.contrib import admin, messages
from django.db.models import Count
from django.utils import timezone

from .models import (
    Activity,
    ActivityMedia,
    DepartmentProfile,
    FAQ,
    Member,
    Message,
)

admin.site.site_header = "体育部网站管理后台"
admin.site.site_title = "体育部网站管理"
admin.site.index_title = "广西科技大学电子工程学院团委学生会体育部"


class VisibilityActionsMixin:
    @admin.action(description="将选中项设为展示")
    def make_visible(self, request, queryset):
        updated = queryset.update(is_visible=True)
        self.message_user(request, f"已将 {updated} 项设为展示。", messages.SUCCESS)

    @admin.action(description="将选中项设为不展示")
    def make_hidden(self, request, queryset):
        updated = queryset.update(is_visible=False)
        self.message_user(request, f"已将 {updated} 项设为不展示。", messages.SUCCESS)


@admin.register(DepartmentProfile)
class DepartmentProfileAdmin(admin.ModelAdmin):
    list_display = ("__str__", "updated_at")
    readonly_fields = ("updated_at",)
    fieldsets = (
        (
            "部门介绍",
            {
                "fields": (
                    "introduction",
                    "welcome_slogan",
                    "recruitment_info",
                )
            },
        ),
        (
            "联系方式",
            {
                "fields": (
                    "contact_info",
                    "qq_group_qr_code",
                )
            },
        ),
        ("系统信息", {"fields": ("updated_at",)}),
    )

    def has_add_permission(self, request):
        return not DepartmentProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Member)
class MemberAdmin(VisibilityActionsMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "position",
        "major_class",
        "generation",
        "tenure",
        "sort_order",
        "is_visible",
        "updated_at",
    )
    list_display_links = ("name",)
    search_fields = (
        "name",
        "position",
        "major_class",
        "tenure",
        "introduction",
        "welcome_message",
    )
    list_filter = ("is_visible", "generation", "position")
    ordering = ("sort_order", "generation", "id")
    list_editable = ("sort_order", "is_visible")
    readonly_fields = ("created_at", "updated_at")
    actions = ("make_visible", "make_hidden")
    save_on_top = True
    fieldsets = (
        (
            "基本信息",
            {
                "fields": (
                    "name",
                    "major_class",
                    "position",
                    "generation",
                    "tenure",
                    "photo",
                )
            },
        ),
        (
            "展示内容",
            {
                "fields": (
                    "introduction",
                    "welcome_message",
                    "sort_order",
                    "is_visible",
                )
            },
        ),
        ("系统信息", {"fields": ("created_at", "updated_at")}),
    )


class ActivityMediaInline(admin.TabularInline):
    model = ActivityMedia
    extra = 0
    fields = ("file", "media_type", "description", "width", "height", "sort_order")
    readonly_fields = ("width", "height")
    ordering = ("sort_order", "id")


@admin.register(Activity)
class ActivityAdmin(VisibilityActionsMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "activity_date",
        "media_count",
        "sort_order",
        "is_visible",
        "updated_at",
    )
    list_display_links = ("name",)
    search_fields = ("name", "introduction", "media__description")
    list_filter = ("is_visible", "category", "activity_date")
    date_hierarchy = "activity_date"
    ordering = ("sort_order", "-activity_date", "id")
    list_editable = ("sort_order", "is_visible")
    readonly_fields = ("created_at", "updated_at")
    actions = ("make_visible", "make_hidden")
    inlines = (ActivityMediaInline,)
    save_on_top = True

    @admin.display(description="媒体数量", ordering="_media_count")
    def media_count(self, obj):
        return obj._media_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_media_count=Count("media"))


@admin.register(ActivityMedia)
class ActivityMediaAdmin(admin.ModelAdmin):
    list_display = (
        "activity",
        "media_type",
        "description",
        "width",
        "height",
        "sort_order",
        "created_at",
    )
    list_display_links = ("activity",)
    search_fields = ("activity__name", "description", "file")
    list_filter = ("media_type", "activity__category")
    ordering = ("activity", "sort_order", "id")
    list_editable = ("sort_order",)
    autocomplete_fields = ("activity",)
    readonly_fields = ("width", "height", "created_at")


@admin.register(FAQ)
class FAQAdmin(VisibilityActionsMixin, admin.ModelAdmin):
    list_display = (
        "question",
        "sort_order",
        "is_visible",
        "updated_at",
    )
    list_display_links = ("question",)
    search_fields = ("question", "answer")
    list_filter = ("is_visible",)
    ordering = ("sort_order", "id")
    list_editable = ("sort_order", "is_visible")
    readonly_fields = ("created_at", "updated_at")
    actions = ("make_visible", "make_hidden")
    save_on_top = True


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "nickname",
        "content_preview",
        "review_status",
        "submitted_at",
        "reviewed_at",
    )
    list_display_links = ("nickname",)
    search_fields = ("nickname", "content")
    list_filter = ("review_status", "submitted_at")
    date_hierarchy = "submitted_at"
    ordering = ("-submitted_at", "id")
    readonly_fields = ("submitted_at", "reviewed_at")
    actions = ("approve_messages", "reject_messages", "mark_pending")
    save_on_top = True

    @admin.display(description="留言内容")
    def content_preview(self, obj):
        return obj.content if len(obj.content) <= 50 else f"{obj.content[:50]}..."

    def _set_review_status(self, request, queryset, status, description):
        reviewed_at = None if status == Message.ReviewStatus.PENDING else timezone.now()
        updated = queryset.update(
            review_status=status,
            reviewed_at=reviewed_at,
        )
        self.message_user(request, f"已将 {updated} 条留言设为{description}。", messages.SUCCESS)

    @admin.action(description="审核通过选中留言")
    def approve_messages(self, request, queryset):
        self._set_review_status(
            request,
            queryset,
            Message.ReviewStatus.APPROVED,
            "已通过",
        )

    @admin.action(description="拒绝选中留言")
    def reject_messages(self, request, queryset):
        self._set_review_status(
            request,
            queryset,
            Message.ReviewStatus.REJECTED,
            "已拒绝",
        )

    @admin.action(description="将选中留言退回待审核")
    def mark_pending(self, request, queryset):
        self._set_review_status(
            request,
            queryset,
            Message.ReviewStatus.PENDING,
            "待审核",
        )
