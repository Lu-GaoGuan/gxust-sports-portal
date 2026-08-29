from django.urls import path

from .views import ActivityDetailView, ActivityListView, CurrentMemberListView, FAQListView, MemberDetailView, MemberListView, MessageListCreateView, department_profile, health_check

app_name = "portal"

urlpatterns = [
    path("health/", health_check, name="health"),
    path("profile/", department_profile, name="profile"),
    path("members/", MemberListView.as_view(), name="members"),
    path("members/current/", CurrentMemberListView.as_view(), name="current-members"),
    path("members/<int:pk>/", MemberDetailView.as_view(), name="member-detail"),
    path("activities/", ActivityListView.as_view(), name="activities"),
    path("activities/<int:pk>/", ActivityDetailView.as_view(), name="activity-detail"),
    path("faqs/", FAQListView.as_view(), name="faqs"),
    path("messages/", MessageListCreateView.as_view(), name="messages"),
]
