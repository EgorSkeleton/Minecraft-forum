from django import forms
from django.forms import ModelForm
from .models import Articles, ArticleImage, TagOfGanre
from .models import ForumTopic, ForumPost

class ArticlesForm(forms.ModelForm):
    class Meta:
        model = Articles
        # Перечисляем поля, которые хотим видеть в форме
        fields = ['title', 'author', 'version', 'status', 'short_text', 'full_text', 'version_tag', 'ganre_tags']
        
        # Добавляем стили каждому полю
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-warning border-secondary', }),
            'author': forms.TextInput(attrs={'class': 'form-control bg-dark text-warning border-secondary'}),
            'version': forms.TextInput(attrs={'class': 'form-control bg-dark text-warning border-secondary'}),
            'status': forms.Select(attrs={'class': 'form-select bg-dark text-warning border-secondary'}),
            'short_text': forms.Textarea(attrs={'class': 'form-control bg-dark text-warning border-secondary', 'rows': 3}),
            'full_text': forms.Textarea(attrs={'class': 'form-control bg-dark text-warning border-secondary', 'rows': 10}),
            'version_tag': forms.Select(attrs={'class': 'form-select bg-dark text-warning border-secondary'}),
            'ganre_tags': forms.SelectMultiple(attrs={
                'class': 'form-select select2-special', 
                'multiple': 'multiple'
            }),
        }

# Форма для одного изображения
class ImageForm(forms.ModelForm):
    class Meta:
        model = ArticleImage
        fields = ['image', 'image_type', 'alt_text']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control bg-dark text-warning border-secondary'}),
            'image_type': forms.Select(attrs={'class': 'form-select bg-dark text-warning border-secondary'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control bg-dark text-warning border-secondary', 'placeholder': 'Описание фото'}),
        }

# Создаем Formset (набор форм) для картинок
ImageFormSet = forms.inlineformset_factory(
    Articles, ArticleImage, form=ImageForm, extra=3, can_delete=True
)

class NewTopicForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Текст вашего первого сообщения...'}),
        label="Сообщение"
    )

    class Meta:
        model = ForumTopic
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Заголовок темы'}),
        }