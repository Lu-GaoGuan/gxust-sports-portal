from datetime import date
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .admin import ActivityAdmin, FAQAdmin, MemberAdmin, MessageAdmin
from .models import (
    Activity,
    ActivityMedia,
    DepartmentProfile,
    FAQ,
    Member,
    Message,
)


class HealthCheckTests(APITestCase):
    def test_clickjacking_middleware_remains_enabled(self):
        self.assertIn(
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            settings.MIDDLEWARE,
        )

    def test_health_check(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")

    def test_public_content_only_returns_visible_records(self):
        Member.objects.create(name="展示成员", position="部长", generation=1)
        Member.objects.create(name="隐藏成员", position="副部长", generation=1, is_visible=False)
        response = self.client.get("/api/members/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["name"] for item in response.data], ["展示成员"])

    def test_message_submission_is_immediately_public(self):
        response = self.client.post("/api/messages/", {"nickname": "新生", "content": "想加入体育部"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.get().review_status, Message.ReviewStatus.APPROVED)
        self.assertEqual(self.client.get("/api/messages/").data[0]["nickname"], "新生")

    def test_approved_message_is_public(self):
        Message.objects.create(nickname="同学", content="欢迎大家", review_status=Message.ReviewStatus.APPROVED)
        response = self.client.get("/api/messages/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["nickname"], "同学")


class PublicApiTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_profile_endpoint(self):
        DepartmentProfile.objects.create(
            introduction="测试简介",
            recruitment_info="测试招新信息",
        )
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["introduction"], "测试简介")
        self.assertEqual(response.data["recruitment_info"], "测试招新信息")

    def test_member_list_detail_and_current_generation_only_show_visible(self):
        previous = Member.objects.create(
            name="往届成员", position="部长", generation=5, sort_order=1
        )
        current = Member.objects.create(
            name="当前成员", position="部长", generation=6, sort_order=2
        )
        hidden = Member.objects.create(
            name="隐藏成员", position="副部长", generation=7, is_visible=False
        )

        list_response = self.client.get("/api/members/")
        self.assertEqual(
            [item["id"] for item in list_response.data], [previous.pk, current.pk]
        )
        detail_response = self.client.get(f"/api/members/{current.pk}/")
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["name"], "当前成员")
        self.assertEqual(
            self.client.get(f"/api/members/{hidden.pk}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        current_response = self.client.get("/api/members/current/")
        self.assertEqual([item["id"] for item in current_response.data], [current.pk])

    def test_activity_list_detail_media_url_and_visibility(self):
        activity = Activity.objects.create(name="公开活动")
        ActivityMedia.objects.create(
            activity=activity,
            file="activities/media/example.jpg",
            description="活动照片",
        )
        hidden = Activity.objects.create(name="隐藏活动", is_visible=False)

        list_response = self.client.get("/api/activities/")
        self.assertEqual([item["id"] for item in list_response.data], [activity.pk])
        media_url = list_response.data[0]["media"][0]["file"]
        self.assertEqual(media_url, "http://testserver/media/activities/media/example.jpg")
        self.assertEqual(
            self.client.get(f"/api/activities/{activity.pk}/").status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.client.get(f"/api/activities/{hidden.pk}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_public_endpoints_reject_mutation(self):
        member = Member.objects.create(name="测试成员", position="部长", generation=1)
        activity = Activity.objects.create(name="测试活动")
        requests = (
            self.client.post("/api/members/", {}),
            self.client.patch(f"/api/members/{member.pk}/", {"name": "修改"}),
            self.client.delete(f"/api/members/{member.pk}/"),
            self.client.post("/api/activities/", {}),
            self.client.patch(f"/api/activities/{activity.pk}/", {"name": "修改"}),
            self.client.delete(f"/api/activities/{activity.pk}/"),
            self.client.post("/api/faqs/", {}),
        )
        for response in requests:
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_message_validation(self):
        blank = self.client.post("/api/messages/", {"nickname": " ", "content": "内容"})
        too_short = self.client.post(
            "/api/messages/", {"nickname": "同学", "content": "好"}
        )
        too_long = self.client.post(
            "/api/messages/", {"nickname": "同学", "content": "字" * 1001}
        )
        control_character = self.client.post(
            "/api/messages/", {"nickname": "同学", "content": "测试\u0001内容"}
        )
        for response in (blank, too_short, too_long, control_character):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Message.objects.count(), 0)

    def test_message_submission_is_rate_limited(self):
        cache.clear()
        for index in range(5):
            response = self.client.post(
                "/api/messages/",
                {"nickname": "同学", "content": f"第 {index + 1} 条留言"},
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        limited = self.client.post(
            "/api/messages/", {"nickname": "同学", "content": "第六条留言"}
        )
        self.assertEqual(limited.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_cors_allows_configured_frontend_origin(self):
        response = self.client.get(
            "/api/health/", HTTP_ORIGIN="http://127.0.0.1:5173"
        )
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"],
            "http://127.0.0.1:5173",
        )


class PortalModelTests(TestCase):
    def test_department_profile_is_singleton(self):
        profile = DepartmentProfile.objects.create(welcome_slogan="测试标语")

        with self.assertRaises(ValidationError):
            DepartmentProfile.objects.create(welcome_slogan="第二条资料")

        self.assertEqual(str(profile), "体育部资料")
        self.assertEqual(DepartmentProfile.objects.count(), 1)

    def test_member_defaults_and_ordering(self):
        second = Member.objects.create(
            name="测试成员乙",
            position="测试职务",
            generation=2,
            sort_order=20,
        )
        first = Member.objects.create(
            name="测试成员甲",
            position="测试职务",
            generation=1,
            sort_order=10,
        )

        self.assertTrue(first.is_visible)
        self.assertEqual(list(Member.objects.all()), [first, second])
        self.assertEqual(str(first), "第1届 测试成员甲")

    def test_activity_media_relationship_and_cascade(self):
        activity = Activity.objects.create(
            name="测试活动",
            category=Activity.Category.WELCOME,
            activity_date=date(2026, 8, 1),
        )
        media = ActivityMedia.objects.create(
            activity=activity,
            file="activities/media/test.jpg",
            media_type=ActivityMedia.MediaType.IMAGE,
            description="测试媒体",
        )

        self.assertEqual(activity.media.get(), media)
        self.assertEqual(str(media), "测试活动 - 图片")

        activity.delete()
        self.assertFalse(ActivityMedia.objects.filter(pk=media.pk).exists())

    def test_image_media_records_dimensions(self):
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            from PIL import Image
            from django.core.files.uploadedfile import SimpleUploadedFile

            image_path = Path(media_root) / "dimension-test.jpg"
            Image.new("RGB", (320, 180), "blue").save(image_path)
            activity = Activity.objects.create(name="尺寸测试")
            with image_path.open("rb") as source:
                media = ActivityMedia.objects.create(
                    activity=activity,
                    file=SimpleUploadedFile("dimension-test.jpg", source.read()),
                )
            self.assertEqual((media.width, media.height), (320, 180))

    def test_faq_defaults(self):
        faq = FAQ.objects.create(question="测试问题？", answer="测试回答。")

        self.assertTrue(faq.is_visible)
        self.assertEqual(faq.sort_order, 0)
        self.assertEqual(str(faq), "测试问题？")

    def test_message_defaults_to_pending(self):
        message = Message.objects.create(
            nickname="测试昵称",
            content="测试留言内容",
        )

        self.assertEqual(message.review_status, Message.ReviewStatus.PENDING)
        self.assertIsNone(message.reviewed_at)
        self.assertIsNotNone(message.submitted_at)

    def test_message_review_timestamp_tracks_status(self):
        message = Message.objects.create(
            nickname="测试昵称",
            content="测试留言内容",
        )
        message.review_status = Message.ReviewStatus.APPROVED
        message.save()

        self.assertIsNotNone(message.reviewed_at)

        message.review_status = Message.ReviewStatus.PENDING
        message.save()
        self.assertIsNone(message.reviewed_at)


class ConfirmedContentSeedTests(TestCase):
    def test_seed_command_is_idempotent(self):
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            call_command("seed_confirmed_content", stdout=StringIO())
            call_command("seed_confirmed_content", stdout=StringIO())

        self.assertEqual(DepartmentProfile.objects.count(), 1)
        self.assertEqual(Member.objects.count(), 12)
        self.assertEqual(Activity.objects.count(), 28)
        self.assertEqual(Activity.objects.filter(is_visible=True).count(), 19)
        self.assertEqual(ActivityMedia.objects.count(), 52)
        handover = Activity.objects.get(name="2025年体育部换届大会")
        self.assertEqual(handover.media.count(), 3)
        self.assertEqual(
            list(handover.media.values_list("media_type", flat=True)),
            [
                ActivityMedia.MediaType.IMAGE,
                ActivityMedia.MediaType.IMAGE,
                ActivityMedia.MediaType.VIDEO,
            ],
        )
        self.assertEqual(FAQ.objects.count(), 13)
        self.assertEqual(
            Member.objects.filter(generation=6, tenure="2026—2027").count(),
            7,
        )
        self.assertFalse(Member.objects.filter(generation=7).exists())
        self.assertEqual(
            FAQ.objects.filter(answer__startswith="【需要学院确认】").count(),
            10,
        )
        included_names = set(
            ActivityMedia.objects.values_list("description", flat=True)
        )
        for source_name in (
            "部门抖音群.jpeg",
            "2024年部门生日烧烤照片.jpeg",
            "2023年部门生日群体照片1.jpeg",
            "2023年部门生日群体照片3.jpeg",
            "2023届运动会聚餐照片.jpeg",
            "2025年部门生日会打麻将的照片.jpeg",
            "2025年部门生日会三国杀群体游戏照片.jpeg",
            "25年校运会偷懒照片.jpeg",
            "25年校运会聚餐视频.mp4",
        ):
            self.assertIn(f"[确认资料] {source_name}", included_names)
        self.assertIn(
            "[确认资料] 2025年部门生日会唱歌照片1.jpeg",
            included_names,
        )


class PortalAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_superuser(
            username="admin-test",
            email="admin-test@example.com",
            password="test-password-only",
        )

    def setUp(self):
        self.client.force_login(self.superuser)
        self.request = RequestFactory().get("/admin/")
        self.request.user = self.superuser

    def test_all_models_are_registered(self):
        for model in (
            DepartmentProfile,
            Member,
            Activity,
            ActivityMedia,
            FAQ,
            Message,
        ):
            self.assertTrue(admin.site.is_registered(model))

    def test_department_profile_admin_allows_only_one_record(self):
        model_admin = admin.site._registry[DepartmentProfile]

        self.assertTrue(model_admin.has_add_permission(self.request))
        DepartmentProfile.objects.create(welcome_slogan="测试标语")
        self.assertFalse(model_admin.has_add_permission(self.request))
        self.assertFalse(model_admin.has_delete_permission(self.request))

    def test_admin_changelists_load_with_simpleui(self):
        urls = (
            reverse("admin:portal_member_changelist"),
            reverse("admin:portal_activity_changelist"),
            reverse("admin:portal_activitymedia_changelist"),
            reverse("admin:portal_faq_changelist"),
            reverse("admin:portal_message_changelist"),
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "simpleui-x")

    def test_admin_search_and_filters_are_configured(self):
        member_admin = admin.site._registry[Member]
        activity_admin = admin.site._registry[Activity]
        media_admin = admin.site._registry[ActivityMedia]
        faq_admin = admin.site._registry[FAQ]
        message_admin = admin.site._registry[Message]

        self.assertIn("name", member_admin.search_fields)
        self.assertIn("generation", member_admin.list_filter)
        self.assertIn("name", activity_admin.search_fields)
        self.assertIn("category", activity_admin.list_filter)
        self.assertIn("description", media_admin.search_fields)
        self.assertIn("media_type", media_admin.list_filter)
        self.assertIn("question", faq_admin.search_fields)
        self.assertIn("review_status", message_admin.list_filter)

    def test_visibility_actions_update_selected_records(self):
        member = Member.objects.create(
            name="测试成员",
            position="测试职务",
            generation=1,
            is_visible=True,
        )
        faq = FAQ.objects.create(
            question="测试问题？",
            answer="测试回答。",
            is_visible=True,
        )

        for model_admin, queryset in (
            (MemberAdmin(Member, admin.site), Member.objects.filter(pk=member.pk)),
            (FAQAdmin(FAQ, admin.site), FAQ.objects.filter(pk=faq.pk)),
        ):
            with self.subTest(model_admin=model_admin):
                model_admin.message_user = lambda *args, **kwargs: None
                model_admin.make_hidden(self.request, queryset)
                self.assertFalse(queryset.get().is_visible)
                model_admin.make_visible(self.request, queryset)
                self.assertTrue(queryset.get().is_visible)

    def test_activity_admin_media_count(self):
        activity = Activity.objects.create(name="测试活动")
        ActivityMedia.objects.create(
            activity=activity,
            file="activities/media/test.jpg",
        )
        model_admin = ActivityAdmin(Activity, admin.site)
        annotated = model_admin.get_queryset(self.request).get(pk=activity.pk)

        self.assertEqual(model_admin.media_count(annotated), 1)

    def test_message_admin_review_actions(self):
        message = Message.objects.create(
            nickname="测试昵称",
            content="测试留言内容",
        )
        model_admin = MessageAdmin(Message, admin.site)
        model_admin.message_user = lambda *args, **kwargs: None
        queryset = Message.objects.filter(pk=message.pk)

        model_admin.approve_messages(self.request, queryset)
        message.refresh_from_db()
        self.assertEqual(message.review_status, Message.ReviewStatus.APPROVED)
        self.assertIsNotNone(message.reviewed_at)
        self.assertLessEqual(message.reviewed_at, timezone.now())

        model_admin.mark_pending(self.request, queryset)
        message.refresh_from_db()
        self.assertEqual(message.review_status, Message.ReviewStatus.PENDING)
        self.assertIsNone(message.reviewed_at)
