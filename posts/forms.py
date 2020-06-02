from django import forms
from django.forms import Textarea
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Содержание записи',
            'group': 'Группа',
            'image': 'Изображение'
        }
        help_texts = {
            'text': 'Пишите в этом окне',
            'group': 'Здесь можно выбрать группу (необязательно)',
            'image': 'Здесь можно загрузить изображение (необязательно)'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Комментируйте в этом окне'
        }
        labels = {
            'text': 'Текст комментария',
        }
        widgets = {
            'text': Textarea(attrs={'cols': 100, 'rows': 10}),
        }
