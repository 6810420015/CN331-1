from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from .models import Side, Comment, Topic, Tag

def validate_side_names(side_names):
    names = [name.strip() for name in side_names if name.strip()]
    if len(names) < 2:
        raise ValidationError("กรุณากำหนดตัวเลือกอย่างน้อย 2 ฝั่ง")
    if any(len(name) > 100 for name in names):
        raise ValidationError("ชื่อตัวเลือกต้องมีความยาวไม่เกิน 100 ตัวอักษร")

    normalized_names = [name.casefold() for name in names]
    if len(normalized_names) != len(set(normalized_names)):
        raise ValidationError("ชื่อตัวเลือกต้องไม่ซ้ำกัน")
    return names

def submit_vote(user, topic, side_id, comment_text):
    if topic.is_expired():
        raise ValidationError("หัวข้อนี้ปิดรับโหวตแล้ว")
        
    if not side_id or not comment_text or not comment_text.strip():
        raise ValidationError("กรุณาเลือกฝั่งและเขียนความคิดเห็นก่อนส่ง")

    try:
        selected_side = Side.objects.get(id=side_id, topic=topic)
    except (Side.DoesNotExist, TypeError, ValueError):
        raise ValidationError("ตัวเลือกนี้ไม่ถูกต้อง กรุณาเลือกฝั่งในหัวข้อนี้")

    if topic.comments.filter(author=user, side__isnull=False).exists():
        raise ValidationError("คุณได้ลงคะแนนในหัวข้อนี้แล้ว")

    try:
        with transaction.atomic():
            Comment.objects.create(
                topic=topic, author=user, side=selected_side, text=comment_text.strip()
            )
    except IntegrityError as err:
        if topic.comments.filter(author=user, side__isnull=False).exists():
            raise ValidationError("คุณได้ลงคะแนนในหัวข้อนี้แล้ว") from err
        raise

def _assign_tags(topic, tags_string):
    if not tags_string:
        topic.tags.clear()
        return
        
    tag_names = [name.strip() for name in tags_string.split(',') if name.strip()]
    tag_objs = []
    for name in set(tag_names):
        tag_obj, created = Tag.objects.get_or_create(name=name)
        tag_objs.append(tag_obj)
        
    topic.tags.set(tag_objs)


def create_topic_with_sides(user, form, side_names):
    validated_names = validate_side_names(side_names)
    
    with transaction.atomic():
        topic = form.save(commit=False)
        topic.created_by = user
        topic.save()
        
        Side.objects.bulk_create(
            [Side(topic=topic, name=side_name) for side_name in validated_names]
        )
        
        tags_string = form.cleaned_data.get('tags_string', '')
        _assign_tags(topic, tags_string)
        
    return topic


def update_topic(topic, form):
    with transaction.atomic():
        topic = form.save()
        tags_string = form.cleaned_data.get('tags_string', '')
        _assign_tags(topic, tags_string)
    return topic


def delete_topic_by_user(user, topic):
    if user != topic.created_by:
        raise PermissionDenied("คุณไม่มีสิทธิ์ลบหัวข้อนี้")
    topic.delete()