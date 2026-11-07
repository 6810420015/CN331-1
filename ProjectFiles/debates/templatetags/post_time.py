from django import template
from django.utils import timezone

register = template.Library()


@register.simple_tag
def show_post_time(created_at):
    if not created_at:
        return ""

    # แปลงเป็นเวลาไทย
    from zoneinfo import ZoneInfo

    if timezone.is_aware(created_at):
        created_at = timezone.localtime(
            created_at, ZoneInfo("Asia/Bangkok")
        )

    return f"โพสต์เมื่อ {created_at:%d/%m/%Y %H:%M}"