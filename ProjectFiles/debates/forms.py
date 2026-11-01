from django import forms
from .models import Topic


class TopicForm(forms.ModelForm):
    side1 = forms.CharField(label="ตัวเลือกที่ 1 (เช่น เห็นด้วย)", max_length=100)
    side2 = forms.CharField(label="ตัวเลือกที่ 2 (เช่น ไม่เห็นด้วย)", max_length=100)

    class Meta:
        model = Topic
        fields = ["title", "description"]


class EditTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["title", "description"]
