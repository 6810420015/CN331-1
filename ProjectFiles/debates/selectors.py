from django.db.models import Q
from django.utils import timezone

from .models import Comment, Topic


def get_topics(search_query="", hide_expired=False):
    """ดึงกระทู้พร้อมความสัมพันธ์ ป้องกันปัญหา N+1 queries"""
    qs = Topic.objects.select_related("created_by").prefetch_related("sides", "tags")

    if search_query:
        qs = qs.filter(
            Q(title__icontains=search_query) | Q(tags__name__icontains=search_query)
        ).distinct()

    if hide_expired:
        qs = qs.filter(Q(end_date__isnull=True) | Q(end_date__gt=timezone.now()))

    return qs.order_by("-created_at")


def get_topic(topic_id):
    """ดึงกระทู้เดี่ยวพร้อม prefetch ข้อมูลคอมเมนต์ ผู้เขียน และตัวเลือกฝั่ง"""
    return (
        Topic.objects.select_related("created_by")
        .prefetch_related(
            "sides",
            "tags",
            "comments__author",
            "comments__side",
        )
        .get(id=topic_id)
    )


def get_user_vote(user, topic):
    """ตรวจดูว่าผู้ใช้เคยลงคะแนนในหัวข้อนี้หรือยัง"""
    return (
        Comment.objects.filter(topic=topic, author=user).select_related("side").first()
    )


def get_user_topics(user):
    """ดึงรายการกระทู้ที่ผู้ใช้สร้างขึ้นเอง"""
    return (
        Topic.objects.filter(created_by=user)
        .select_related("created_by")
        .prefetch_related("sides", "tags")
        .order_by("-created_at")
    )


def get_user_comments(user):
    """ดึงประวัติการคอมเมนต์และโหวตของผู้ใช้"""
    return (
        Comment.objects.filter(author=user)
        .select_related("topic", "side")
        .order_by("-created_at")
    )
