from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from .models import Topic, Side, Comment
from . import services

class DebateTests(TestCase):
    def setUp(self):
        # Mock Data
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.topic = Topic.objects.create(
            title='หัวข้อทดสอบระบบ',
            description='รายละเอียดทดสอบ',
            created_by=self.user,
            end_date=timezone.now() + timedelta(days=1) # ตั้งให้ยังไม่หมดอายุ
        )
        self.side = Side.objects.create(topic=self.topic, name='เห็นด้วย')

    # ทดสอบ Model 
    def test_topic_is_expired(self):
        self.topic.end_date = timezone.now() - timedelta(days=1) # จำลองให้หมดอายุ
        self.topic.save()
        self.assertTrue(self.topic.is_expired())

    # ทดสอบ Views 
    def test_topic_list_view_status_code(self):
        response = self.client.get(reverse('topic_list'))
        self.assertEqual(response.status_code, 200) # โหลดหน้าแรกสำเร็จ

    def test_create_topic_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('create_topic'))
        self.assertEqual(response.status_code, 302) # คนไม่ล็อกอินต้องโดนเตะไปหน้า Login

    # ทดสอบ Services 
    def test_submit_vote_success(self):
        services.submit_vote(
            user=self.user,
            topic=self.topic,
            side_id=self.side.id,
            comment_text="ทดสอบคอมเมนต์"
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().text, "ทดสอบคอมเมนต์")

    def test_submit_vote_expired_topic(self):
        # ทดสอบว่าหัวข้อหมดเวลาจะโหวตไม่ได้และเด้ง ValidationError
        self.topic.end_date = timezone.now() - timedelta(days=1)
        self.topic.save()
        
        with self.assertRaises(ValidationError):
            services.submit_vote(
                user=self.user,
                topic=self.topic,
                side_id=self.side.id,
                comment_text="ทดสอบโหวตตอนหมดเวลา"
            )