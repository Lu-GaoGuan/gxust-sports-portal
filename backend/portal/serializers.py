from rest_framework import serializers

from .models import Activity, ActivityMedia, DepartmentProfile, FAQ, Member, Message


class DepartmentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentProfile
        fields = ("introduction", "welcome_slogan", "recruitment_info", "contact_info", "qq_group_qr_code", "updated_at")


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ("id", "name", "major_class", "position", "generation", "tenure", "introduction", "welcome_message", "photo")


class ActivityMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityMedia
        fields = ("id", "file", "media_type", "description", "width", "height")


class ActivitySerializer(serializers.ModelSerializer):
    media = ActivityMediaSerializer(many=True, read_only=True)
    category_label = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Activity
        fields = ("id", "name", "category", "category_label", "activity_date", "introduction", "cover", "media")


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ("id", "question", "answer")


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "nickname", "content", "submitted_at")
        read_only_fields = ("id", "submitted_at")

    def validate_nickname(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("请填写昵称。")
        return value

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("请填写留言内容。")
        if len(value) < 2:
            raise serializers.ValidationError("留言内容至少需要 2 个字符。")
        if len(value) > 1000:
            raise serializers.ValidationError("留言内容不能超过 1000 个字符。")
        if any(ord(character) < 32 and character not in "\n\r\t" for character in value):
            raise serializers.ValidationError("留言内容包含不支持的控制字符。")
        return value
