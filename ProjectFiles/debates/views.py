from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from .forms import EditTopicForm, TopicForm
from . import selectors, services

def topic_list(request):
    search_query = request.GET.get("q", "")
    topics = selectors.get_topics(search_query)
    return render(request, "debates/topic_list.html", {"topics": topics, "search_query": search_query})

def topic_detail(request, topic_id):
    topic = selectors.get_topic(topic_id)
    user_vote = selectors.get_user_vote(request.user, topic)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        try:
            services.submit_vote(
                user=request.user, 
                topic=topic, 
                side_id=request.POST.get("side"), 
                comment_text=request.POST.get("comment_text", "").strip()
            )
            messages.success(request, "บันทึกคะแนนและความคิดเห็นแล้ว")
        except ValidationError as err:
            messages.error(request, err.message)
            
        return redirect("topic_detail", topic_id=topic.id)

    return render(request, "debates/topic_detail.html", {"topic": topic, "user_vote": user_vote})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("topic_list")
    else:
        form = UserCreationForm()
    return render(request, "debates/signup.html", {"form": form})

@login_required
def create_topic(request):
    if request.method == "POST":
        form = TopicForm(request.POST)
        if form.is_valid():
            services.create_topic_with_sides(request.user, form, request.POST.getlist("sides"))
            return redirect("topic_list")
    else:
        form = TopicForm()
    return render(request, "debates/create_topic.html", {"form": form})

@login_required
def delete_topic(request, topic_id):
    topic = selectors.get_topic(topic_id)
    services.delete_topic_by_user(request.user, topic)
    return redirect("topic_list")

@login_required
def edit_topic(request, topic_id):
    topic = selectors.get_topic(topic_id)
    if request.user != topic.created_by:
        return redirect("topic_list")

    if request.method == "POST":
        form = EditTopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            return redirect("topic_detail", topic_id=topic.id)
    else:
        form = EditTopicForm(instance=topic)
    return render(request, "debates/edit_topic.html", {"form": form, "topic": topic})

@login_required
def user_profile(request):
    my_topics = selectors.get_user_topics(request.user)
    my_comments = selectors.get_user_comments(request.user)
    return render(request, "debates/profile.html", {"my_topics": my_topics, "my_comments": my_comments})