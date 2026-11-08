from django.contrib import admin

from .models import Comment, Side, Topic


class SideInline(admin.TabularInline):
    model = Side
    extra = 2  # แสดงช่องให้กรอกตัวเลือก 2 ฝั่งอัตโนมัติ


class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "created_at")
    inlines = [SideInline]


class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "topic", "side", "created_at")


admin.site.register(Topic, TopicAdmin)
admin.site.register(Side)
admin.site.register(Comment, CommentAdmin)
