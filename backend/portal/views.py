from django.db.models import Max
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .models import Activity, DepartmentProfile, FAQ, Member, Message
from .serializers import ActivitySerializer, DepartmentProfileSerializer, FAQSerializer, MemberSerializer, MessageSerializer


@api_view(["GET"])
def health_check(request):
    return Response(
        {
            "status": "ok",
            "service": "sports-department-portal-api",
        }
    )


@api_view(["GET"])
def department_profile(request):
    profile = DepartmentProfile.objects.first()
    if profile is None:
        return Response(None)
    return Response(DepartmentProfileSerializer(profile, context={"request": request}).data)


class MemberListView(generics.ListAPIView):
    serializer_class = MemberSerializer
    queryset = Member.objects.filter(is_visible=True)


class MemberDetailView(generics.RetrieveAPIView):
    serializer_class = MemberSerializer
    queryset = Member.objects.filter(is_visible=True)


class CurrentMemberListView(generics.ListAPIView):
    serializer_class = MemberSerializer

    def get_queryset(self):
        visible_members = Member.objects.filter(is_visible=True)
        current_generation = visible_members.aggregate(value=Max("generation"))["value"]
        if current_generation is None:
            return visible_members.none()
        return visible_members.filter(generation=current_generation)


class ActivityListView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    queryset = Activity.objects.filter(is_visible=True).prefetch_related("media")


class ActivityDetailView(generics.RetrieveAPIView):
    serializer_class = ActivitySerializer
    queryset = Activity.objects.filter(is_visible=True).prefetch_related("media")


class FAQListView(generics.ListAPIView):
    serializer_class = FAQSerializer
    queryset = FAQ.objects.filter(is_visible=True)


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    throttle_scope = "message_submission"

    def get_queryset(self):
        return Message.objects.filter(review_status=Message.ReviewStatus.APPROVED)

    def perform_create(self, serializer):
        serializer.save(review_status=Message.ReviewStatus.APPROVED)

    def get_throttles(self):
        if self.request.method == "POST":
            return [ScopedRateThrottle()]
        return []
