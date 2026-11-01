from django.shortcuts import render, get_object_or_404, redirect
from .models import Topic, Side, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import TopicForm, EditTopicForm


def topic_list(request):
    topics = Topic.objects.all().order_by("-created_at")
    return render(request, "debates/topic_list.html", {"topics": topics})


def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)

    if request.method == "POST":
        side_id = request.POST.get("side")
        comment_text = request.POST.get("comment_text", "")  # รับค่าข้อความที่พิมพ์

        if side_id and request.user.is_authenticated:
            selected_side = get_object_or_404(Side, id=side_id)
            Comment.objects.create(
                topic=topic, author=request.user, side=selected_side, text=comment_text
            )
            return redirect("topic_detail", topic_id=topic.id)

    return render(request, "debates/topic_detail.html", {"topic": topic})


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
            topic = form.save(commit=False)
            topic.created_by = request.user  # ผูกกระทู้กับคนที่ล็อกอิน
            topic.save()

            # บันทึกตัวเลือกทั้ง 2 ฝั่งลงฐานข้อมูล
            Side.objects.create(topic=topic, name=form.cleaned_data["side1"])
            Side.objects.create(topic=topic, name=form.cleaned_data["side2"])

            return redirect("topic_list")
    else:
        form = TopicForm()
    return render(request, "debates/create_topic.html", {"form": form})


@login_required
def delete_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    # ตรวจสอบว่าเป็นเจ้าของกระทู้จริงๆ
    if request.user == topic.created_by:
        topic.delete()
    return redirect("topic_list")


@login_required
def edit_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)

    # ป้องกันไม่ให้คนอื่นที่แอบเข้าลิงก์นี้มาแก้กระทู้ได้
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
    # ดึงกระทู้ที่ผู้ใช้คนนี้เป็นคนตั้ง
    my_topics = Topic.objects.filter(created_by=request.user).order_by("-created_at")
    # ดึงคอมเมนต์ที่ผู้ใช้คนนี้เป็นคนพิมพ์
    my_comments = Comment.objects.filter(author=request.user).order_by("-created_at")

    return render(
        request,
        "debates/profile.html",
        {"my_topics": my_topics, "my_comments": my_comments},
    )
