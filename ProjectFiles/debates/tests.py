from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import Topic, Side, Comment, Tag
from .forms import TopicForm
from . import services, selectors

class TopicModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='modeluser', password='password123')
        self.topic = Topic.objects.create(
            title='Test Topic',
            description='Test Description',
            created_by=self.user
        )

    def test_topic_str(self):
        """ทดสอบ String Representation ของ Topic"""
        self.assertEqual(str(self.topic), 'Test Topic')

    def test_topic_expiration(self):
        """ทดสอบสถานะหมดเวลาของ Topic"""
        self.assertFalse(self.topic.is_expired())

        self.topic.end_date = timezone.now() - timedelta(days=1)
        self.topic.save()
        self.assertTrue(self.topic.is_expired())


class SideAndCommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='subuser', password='password123')
        self.topic = Topic.objects.create(title='Sample Topic', description='Desc', created_by=self.user)
        self.side = Side.objects.create(topic=self.topic, name='Agree')
        
        services.submit_vote(user=self.user, topic=self.topic, side_id=self.side.id, comment_text='Great topic!')
        self.comment = self.topic.comments.first()

    def test_side_str(self):
        """ทดสอบ String Representation ของ Side ให้ตรงกับรูปแบบ 'Topic - Side'"""
        self.assertEqual(str(self.side), 'Sample Topic - Agree')

    def test_comment_str(self):
        """ทดสอบ String Representation ของ Comment"""
        self.assertTrue(str(self.comment))


class TopicFormTest(TestCase):
    def test_topic_form_valid(self):
        """ทดสอบ Form เมื่อกรอกข้อมูลถูกต้อง"""
        form_data = {
            'title': 'Django vs FastAPI',
            'description': 'Which is better for APIs?',
            'is_anonymous': False,
            'tags_string': 'python, backend'
        }
        form = TopicForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_topic_form_invalid_missing_title(self):
        """ทดสอบ Form เมื่อไม่ใส่ชื่อหัวข้อ (ควรไม่ Valid)"""
        form_data = {
            'title': '',
            'description': 'Missing title',
            'is_anonymous': False
        }
        form = TopicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class DebatesServiceAndSelectorTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

    def test_create_topic_with_sides_service(self):
        """ทดสอบ Service การสร้าง Topic พร้อม Side และ Tag"""
        form_data = {
            'title': 'Cats vs Dogs',
            'description': 'Which pet is better?',
            'is_anonymous': True,
            'tags_string': 'pets, animals'
        }
        form = TopicForm(data=form_data)
        self.assertTrue(form.is_valid())

        topic = services.create_topic_with_sides(self.user1, form, ['Cats', 'Dogs'])
        
        self.assertEqual(topic.title, 'Cats vs Dogs')
        self.assertTrue(topic.is_anonymous)
        self.assertEqual(topic.sides.count(), 2)
        self.assertEqual(topic.tags.count(), 2)

    def test_submit_vote_and_validation(self):
        """ทดสอบการโหวตและการดักจับข้อผิดพลาดห้ามโหวตซ้ำ"""
        topic = Topic.objects.create(title='Vote Test', description='Desc', created_by=self.user1)
        side1 = Side.objects.create(topic=topic, name='Yes')
        side2 = Side.objects.create(topic=topic, name='No')

        services.submit_vote(user=self.user2, topic=topic, side_id=side1.id, comment_text='I agree')
        self.assertEqual(topic.comments.count(), 1)

        with self.assertRaises(ValidationError):
            services.submit_vote(user=self.user2, topic=topic, side_id=side2.id, comment_text='Changed mind')

    def test_expired_topic_voting_validation(self):
        """ทดสอบการห้ามโหวตหัวข้อที่หมดเวลาแล้ว"""
        past_time = timezone.now() - timedelta(hours=2)
        topic = Topic.objects.create(title='Expired Topic', description='Desc', created_by=self.user1, end_date=past_time)
        side = Side.objects.create(topic=topic, name='A')

        with self.assertRaises(ValidationError):
            services.submit_vote(user=self.user2, topic=topic, side_id=side.id, comment_text='Too late')

    def test_selectors_search_and_user_topics(self):
        """ทดสอบ Selectors ค้นหากระทู้และดึงกระทู้ของผู้ใช้"""
        t1 = Topic.objects.create(title='Python Programming', description='Desc', created_by=self.user1)
        t2 = Topic.objects.create(title='Web Design', description='Desc', created_by=self.user1)

        results = selectors.get_topics(search_query='Python', hide_expired=False)
        self.assertIn(t1, results)
        self.assertNotIn(t2, results)

        user_topics = selectors.get_user_topics(self.user1)
        self.assertEqual(user_topics.count(), 2)


class DebatesViewClientTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='viewuser', password='password123')
        self.client = Client()
        self.topic = Topic.objects.create(title='View Topic', description='Desc', created_by=self.user)
        self.side = Side.objects.create(topic=self.topic, name='Option 1')

    def test_topic_list_view_get(self):
        """ทดสอบหน้าแสดงรายการ Topic (GET)"""
        response = self.client.get(reverse('topic_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'View Topic')

    def test_topic_list_view_with_search(self):
        """ทดสอบหน้าแสดงรายการ Topic พร้อม Query ค้นหา"""
        response = self.client.get(reverse('topic_list'), {'q': 'View Topic'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'View Topic')

    def test_topic_detail_view(self):
        """ทดสอบหน้าแสดงรายละเอียด Topic และการคอมเมนต์"""
        services.submit_vote(user=self.user, topic=self.topic, side_id=self.side.id, comment_text='Testing detail view')
        response = self.client.get(reverse('topic_detail', args=[self.topic.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Testing detail view')

    def test_topic_detail_view_filtered(self):
        """ทดสอบการกรองคอมเมนต์ตาม side_filter ในหน้า Detail"""
        services.submit_vote(user=self.user, topic=self.topic, side_id=self.side.id, comment_text='Filtered comment')
        response = self.client.get(reverse('topic_detail', args=[self.topic.id]), {'side_filter': self.side.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Filtered comment')

    def test_create_topic_view_access(self):
        """ทดสอบการเข้าถึงหน้าสร้างกระทู้ (ต้องล็อกอิน)"""
        response = self.client.get(reverse('create_topic'))
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='viewuser', password='password123')
        response = self.client.get(reverse('create_topic'))
        self.assertEqual(response.status_code, 200)

    def test_edit_topic_view_permissions(self):
        """ทดสอบสิทธิ์การแก้ไขกระทู้ (เฉพาะเจ้าของ)"""
        other_user = User.objects.create_user(username='otheruser', password='password123')
        self.client.login(username='otheruser', password='password123')
        
        response = self.client.get(reverse('edit_topic', args=[self.topic.id]))
        self.assertNotEqual(response.status_code, 200)

    def test_delete_topic_view(self):
        """ทดสอบการลบกระทู้โดยเจ้าของ"""
        self.client.login(username='viewuser', password='password123')
        response = self.client.post(reverse('delete_topic', args=[self.topic.id]))
        self.assertRedirects(response, reverse('topic_list'))
        self.assertEqual(Topic.objects.count(), 0)