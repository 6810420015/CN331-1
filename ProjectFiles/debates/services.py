from django.core.exceptions import ValidationError
from .models import Side, Comment

def submit_vote(user, topic, side_id, comment_text):
    if topic.is_expired():
        raise ValidationError("หัวข้อนี้ปิดรับโหวตแล้ว")
        
    user_vote = topic.comments.filter(author=user, side__isnull=False).first()
    if user_vote:
        raise ValidationError("คุณได้ลงคะแนนในหัวข้อนี้แล้ว")

    if not side_id or not comment_text:
        raise ValidationError("กรุณาเลือกฝั่งและเขียนความคิดเห็นก่อนส่ง")

    try:
        selected_side = Side.objects.get(id=side_id, topic=topic)
    except (Side.DoesNotExist, TypeError, ValueError):
        raise ValidationError("ตัวเลือกนี้ไม่ถูกต้อง กรุณาเลือกฝั่งในหัวข้อนี้")

    Comment.objects.create(
        topic=topic, author=user, side=selected_side, text=comment_text
    )

def create_topic_with_sides(user, form, side_names):
    topic = form.save(commit=False)
    topic.created_by = user
    topic.save()
    for side_name in side_names:
        if side_name.strip():
            Side.objects.create(topic=topic, name=side_name.strip())
    return topic

def delete_topic_by_user(user, topic):
    if user == topic.created_by:
        topic.delete()