from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    title = models.CharField(max_length=200, verbose_name="หัวข้อกระทู้")
    description = models.TextField(verbose_name="รายละเอียดประเด็น")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="ผู้ตั้งกระทู้"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Side(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="sides")
    name = models.CharField(max_length=100, verbose_name="ชื่อฝั่ง (เช่น เห็นด้วย/ไม่เห็นด้วย)")

    def __str__(self):
        return f"{self.topic.title} - {self.name}"


class Comment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ผู้คอมเมนต์")
    side = models.ForeignKey(
        Side,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="ฝั่งที่เลือกโหวต",
    )
    text = models.TextField(verbose_name="ความคิดเห็น")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.topic.title}"
