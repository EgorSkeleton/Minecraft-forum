from django import forms
from .models import Articles, ForumTopic
from .models import Profile
from django.contrib.auth.models import User

class ArticlesForm(forms.ModelForm):
    # Поле для множественной загрузки скриншотов
    # Мы объявляем его здесь, так как в самой модели Articles этого поля нет (оно для ArticleImage)
    screenshots = forms.ImageField(
        label='Скриншоты (до 10 шт.)',
        widget=forms.FileInput(attrs={
            'class': 'form-control bg-dark text-warning border-secondary',
        }),
        required=False
    )

    class Meta:
        model = Articles
        # Список всех полей, которые будут в форме
        fields = [
            'title', 'author', 'version', 'status', 
            'version_tag', 'ganre_tags', 'logo', 
            'short_text', 'full_text'
        ]
        
        # Стилизация полей через виджеты
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-warning border-secondary'}),
            'author': forms.TextInput(attrs={'class': 'form-control bg-dark text-warning border-secondary'}),
            'version': forms.TextInput(attrs={'class': 'form-control bg-dark text-warning border-secondary'}),
            'status': forms.Select(attrs={'class': 'form-select bg-dark text-warning border-secondary'}),
            'version_tag': forms.Select(attrs={'class': 'form-select bg-dark text-warning border-secondary'}),
            
            # Поле для логотипа (одиночный файл)
            'logo': forms.FileInput(attrs={'class': 'form-control bg-dark text-warning border-secondary'}),
            
            'short_text': forms.Textarea(attrs={'class': 'form-control bg-dark text-warning border-secondary', 'rows': 3}),
            'full_text': forms.Textarea(attrs={'class': 'form-control bg-dark text-warning border-secondary', 'rows': 10}),
            
            # Поле для тегов (использует select2-special из твоего шаблона)
            'ganre_tags': forms.SelectMultiple(attrs={
                'class': 'form-select select2-special', 
                'multiple': 'multiple'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Метод инициализации формы. 
        Здесь мы принудительно добавляем атрибут 'multiple' полю screenshots,
        чтобы Django не ругался при запуске сервера.
        """
        super().__init__(*args, **kwargs)
        # Этот хак позволяет загружать несколько файлов через одно поле
        self.fields['screenshots'].widget.attrs.update({'multiple': True})

class NewTopicForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-dark text-white border-secondary', # Добавил твои стили
            'rows': 5, 
            'placeholder': 'Текст вашего первого сообщения...'
        }),
        label="Сообщение",
        required=True
    )

    class Meta:
        model = ForumTopic
        fields = ['title'] 
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary', # Добавил твои стили
                'placeholder': 'Заголовок темы'
            }),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio'] # Добавь сюда поля, которые есть в твоей модели Profile
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control bg-dark text-warning border-secondary'}),
            'bio': forms.Textarea(attrs={'class': 'form-control bg-dark text-warning border-secondary', 'rows': 3, 'placeholder': 'Расскажите о себе...'}),
        }

# Если хочешь менять еще и ник/почту (модель User), добавим вторую форму
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control bg-dark text-warning border-secondary'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-warning border-secondary'}),
        }