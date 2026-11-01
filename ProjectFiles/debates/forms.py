from django import forms
from .models import Topic

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        # ตรง fields ต้องมีวงเล็บเหลี่ยมแค่ชั้นเดียวแบบนี้ครับ
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
