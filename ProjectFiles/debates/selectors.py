from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Topic, Side, Comment


def _with_vote_results(queryset):
    return queryset.annotate(
        vote_count=Count(
            "comments", filter=Q(comments__side__isnull=False), distinct=True
        )
    ).prefetch_related(
        Prefetch(
            "sides",
            queryset=Side.objects.annotate(vote_count=Count("comment", distinct=True)),
        ),
    )


def get_topics(search_query="", hide_expired=False):
    # เริ่มต้นด้วย QuerySet ที่ผูกการนับคะแนนโหวตแล้ว
    queryset = _with_vote_results(Topic.objects.select_related("created_by")).order_by("-created_at", "-id")
    
    # เงื่อนไขซ่อนกระทู้หมดเวลา
    if hide_expired:
        now = timezone.now()
        queryset = queryset.filter(Q(end_date__isnull=True) | Q(end_date__gt=now))

    # เงื่อนไขการค้นหา
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
        
    return queryset.distinct()


def get_topic(topic_id):
    return get_object_or_404(
        _with_vote_results(Topic.objects.select_related("created_by")).prefetch_related(
            "comments__author", "comments__side"
        ),
        id=topic_id,
    )


def get_user_vote(user, topic):
    if not user.is_authenticated:
        return None
    return Comment.objects.filter(author=user, topic=topic).first()


def get_user_topics(user):
    return Topic.objects.filter(created_by=user).order_by("-created_at")


def get_user_comments(user):
    return Comment.objects.filter(author=user).order_by("-created_at")