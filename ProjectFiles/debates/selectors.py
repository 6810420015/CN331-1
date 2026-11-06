from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Topic, Comment

def get_topics(search_query=""):
    active_topics = Topic.objects.filter(
        Q(end_date__isnull=True) | Q(end_date__gt=timezone.now())
    )
    if search_query:
        return active_topics.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        ).distinct()
    return active_topics

def get_topic(topic_id):
    return get_object_or_404(Topic, id=topic_id)

def get_user_vote(user, topic):
    if user.is_authenticated:
        return topic.comments.filter(author=user, side__isnull=False).first()
    return None

def get_user_topics(user):
    return Topic.objects.filter(created_by=user).order_by("-created_at")

def get_user_comments(user):
    return Comment.objects.filter(author=user).order_by("-created_at")
