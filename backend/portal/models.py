from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from PIL import Image, UnidentifiedImageError


class DepartmentProfile(models.Model):
    introduction = models.TextField("体育部简介", blank=True)
    welcome_slogan = models.CharField("迎新标语", max_length=200, blank=True)
    recruitment_info = models.TextField("招新信息", blank=True)
    contact_info = models.TextField(
        "联系方式",
        blank=True,
        help_text="可填写经确认的邮箱、QQ群或其他公开联系方式。",
    )
    qq_group_qr_code = models.ImageField(
        "QQ群二维码",
        upload_to="department/qr_codes/",
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "体育部资料"
        verbose_name_plural = "体育部资料"

    def __str__(self):
        return "体育部资料"

    def clean(self):
        existing = DepartmentProfile.objects.exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError("体育部资料只能创建一条，请编辑现有资料。")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Member(models.Model):
    name = models.CharField("姓名", max_length=50)
    major_class = models.CharField("专业班级", max_length=100, blank=True)
    position = models.CharField("职务", max_length=100)
    generation = models.PositiveSmallIntegerField(
        "届数",
        validators=[MinValueValidator(1)],
        db_index=True,
    )
    tenure = models.CharField(
        "任期",
        max_length=100,
        blank=True,
        help_text="按已确认资料填写，例如“2020-2022”。",
    )
    introduction = models.TextField("个人介绍", blank=True)
    welcome_message = models.TextField("新生寄语", blank=True)
    photo = models.ImageField(
        "照片",
        upload_to="members/",
        blank=True,
        null=True,
    )
    sort_order = models.PositiveIntegerField("排序", default=0, db_index=True)
    is_visible = models.BooleanField("是否展示", default=True, db_index=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "成员"
        verbose_name_plural = "成员"
        ordering = ("sort_order", "generation", "id")
        indexes = [
            models.Index(
                fields=("is_visible", "sort_order"),
                name="member_visible_sort_idx",
            )
        ]

    def __str__(self):
        return f"第{self.generation}届 {self.name}"


class Activity(models.Model):
    class Category(models.TextChoices):
        SPORTS = "sports", "体育赛事"
        WELCOME = "welcome", "迎新活动"
        TEAM_BUILDING = "team_building", "团建活动"
        BIRTHDAY = "birthday", "部门生日会"
        VOLUNTEER = "volunteer", "志愿服务"
        MEETING = "meeting", "会议与学习"
        OTHER = "other", "其他活动"

    name = models.CharField("活动名称", max_length=150)
    category = models.CharField(
        "活动分类",
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER,
        db_index=True,
    )
    activity_date = models.DateField(
        "活动日期",
        blank=True,
        null=True,
        db_index=True,
    )
    introduction = models.TextField("活动简介", blank=True)
    cover = models.ImageField(
        "封面",
        upload_to="activities/covers/",
        blank=True,
        null=True,
    )
    sort_order = models.PositiveIntegerField("排序", default=0, db_index=True)
    is_visible = models.BooleanField("是否展示", default=True, db_index=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "活动"
        verbose_name_plural = "活动"
        ordering = ("sort_order", "-activity_date", "id")
        indexes = [
            models.Index(
                fields=("is_visible", "sort_order"),
                name="activity_visible_sort_idx",
            )
        ]

    def __str__(self):
        return self.name


class ActivityMedia(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", "图片"
        VIDEO = "video", "视频"

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="media",
        verbose_name="所属活动",
    )
    file = models.FileField("图片或视频", upload_to="activities/media/")
    media_type = models.CharField(
        "媒体类型",
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
        db_index=True,
    )
    description = models.CharField("说明", max_length=250, blank=True)
    width = models.PositiveIntegerField("媒体宽度", blank=True, null=True, editable=False)
    height = models.PositiveIntegerField("媒体高度", blank=True, null=True, editable=False)
    sort_order = models.PositiveIntegerField("排序", default=0, db_index=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "活动媒体"
        verbose_name_plural = "活动媒体"
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(
                fields=("activity", "sort_order"),
                name="media_activity_sort_idx",
            )
        ]

    def __str__(self):
        return f"{self.activity} - {self.get_media_type_display()}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        dimensions = (None, None)
        if self.media_type == self.MediaType.IMAGE and self.file:
            try:
                self.file.open("rb")
                with Image.open(self.file) as image:
                    dimensions = image.size
            except (FileNotFoundError, OSError, UnidentifiedImageError):
                dimensions = (None, None)
            finally:
                try:
                    self.file.close()
                except (AttributeError, ValueError):
                    pass
        if (self.width, self.height) != dimensions:
            self.width, self.height = dimensions
            type(self).objects.filter(pk=self.pk).update(
                width=self.width,
                height=self.height,
            )


class FAQ(models.Model):
    question = models.CharField("问题", max_length=250)
    answer = models.TextField("回答")
    sort_order = models.PositiveIntegerField("排序", default=0, db_index=True)
    is_visible = models.BooleanField("是否展示", default=True, db_index=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "常见问题"
        verbose_name_plural = "常见问题"
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(
                fields=("is_visible", "sort_order"),
                name="faq_visible_sort_idx",
            )
        ]

    def __str__(self):
        return self.question


class Message(models.Model):
    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "待审核"
        APPROVED = "approved", "已通过"
        REJECTED = "rejected", "已拒绝"

    nickname = models.CharField("留言昵称", max_length=50)
    content = models.TextField("留言内容")
    review_status = models.CharField(
        "审核状态",
        max_length=10,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
        db_index=True,
    )
    submitted_at = models.DateTimeField("提交时间", auto_now_add=True, db_index=True)
    reviewed_at = models.DateTimeField("审核时间", blank=True, null=True)

    class Meta:
        verbose_name = "留言"
        verbose_name_plural = "留言"
        ordering = ("-submitted_at", "id")
        indexes = [
            models.Index(
                fields=("review_status", "-submitted_at"),
                name="message_status_time_idx",
            )
        ]

    def __str__(self):
        return f"{self.nickname}：{self.content[:20]}"

    def save(self, *args, **kwargs):
        if self.review_status == self.ReviewStatus.PENDING:
            self.reviewed_at = None
        elif self.reviewed_at is None:
            self.reviewed_at = timezone.now()
        return super().save(*args, **kwargs)
