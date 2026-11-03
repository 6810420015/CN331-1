from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Topic, Comment

def get_topics(search_query=""):
    if search_query:
        return Topic.objects.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        ).distinct()
    return Topic.objects.all()

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