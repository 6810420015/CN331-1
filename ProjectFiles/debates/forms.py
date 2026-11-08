from django import forms
from .models import Topic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe  

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'description', 'end_date'] 
        
        labels = {
            'title': 'ชื่อหัวข้อใหม่',
            'description': 'รายละเอียด',
            'end_date': 'เวลาปิดรับโหวต (ปล่อยว่างได้ถ้าไม่จำกัด)',
        }
        widgets = {
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        }

class EditTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["title", "description"]


class CustomSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username"] 
        labels = {
            'username': 'ชื่อผู้ใช้',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        password_help_html = """
        <ul style="padding-left: 20px; margin-top: 5px; color: #6c757d; font-size: 0.9em;">
            <li>รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร</li>
            <li>รหัสผ่านต้องไม่ประกอบด้วยตัวเลขเพียงอย่างเดียว</li>
        </ul>
        """
        self.fields['password1'].help_text = mark_safe(password_help_html)
        self.fields['password2'].help_text = mark_safe('<span style="color: #6c757d; font-size: 0.9em;">กรอกรหัสผ่านอีกครั้ง</span>')