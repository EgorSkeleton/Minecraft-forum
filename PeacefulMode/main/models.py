from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from transliterate import slugify as translit_slugify

class TagOfVersion(models.Model):
    class GameEditions(models.TextChoices):
        JAVA = 'Java Edition'
        BEDROCK = 'Bedrock Edition'
        BOTH = 'Java & Bedrock Editions'

    edition = models.CharField(max_length=30,  choices=GameEditions.choices,default=GameEditions.JAVA,blank=False)

    def __str__(self):
        return f"{self.edition}"

    
class TagOfGanre(models.Model):
    class Ganre(models.TextChoices):
        HARDCORE = 'Hardcore', 'Хардкор'
        RPG = 'RPG', 'РПГ'
        ADVENTURE = 'Adventure', 'Приключение'
        TECH = 'Technology', 'Технологии'
        FANTASY = 'Fantasy', 'Фэнтези'
        SKYBLOCK = 'SkyBlock', 'СкайБлок'
        VANILLA_PLUSS = 'Vanilla+', 'Ванилла+'
        PVP = 'PVP', 'ПВП'
        PVE = 'PVE', 'ПВЕ'

    ganre = models.CharField(max_length=20, choices=Ganre.choices, blank=False, unique=True)

    def __str__(self):
        return self.ganre


class ArticleImage(models.Model):
    class ImageType(models.TextChoices):
        LOGO = 'logo', 'Логотип'
        SCREENSHOT = 'screenshot', 'Скриншот'

    article = models.ForeignKey('Articles', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='media/')
    alt_text = models.CharField(max_length=100, blank=True)
    image_type = models.CharField(max_length=20, choices=ImageType.choices, default=ImageType.SCREENSHOT)

    def __str__(self):
        return f"{self.article} - {self.image_type}"

class Articles(models.Model):
    class Status(models.TextChoices):
        ABANDONED = 'abandoned', 'Заброшен'
        ACTIVE = 'active', 'Разрабатывается'
        UNKNOWN = 'unknown', 'Неизвестно'

    title = models.CharField('Название', max_length=50, blank=False, null=False)
    author = models.CharField('Автор сборки', max_length=50, blank=True, null=True)
    date = models.DateField('Дата выхода сборки', null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNKNOWN, blank=False)
    version_tag = models.ForeignKey(TagOfVersion, on_delete=models.PROTECT, null=True)
    version = models.CharField('Версия игры', max_length=10, blank=False, null=True)
    ganre_tags = models.ManyToManyField(TagOfGanre, blank=True)
    short_text = models.TextField('Краткое описание', blank=False, null=False, default='Краткое описание')
    full_text = models.TextField('Статья', blank=False, null=False, default='Полное описание')
    is_approved = models.BooleanField('Проверено модерацией', default=False)
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/news/{self.id}' 

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

class ForumCategory(models.Model):
    title = models.CharField('Название категории', max_length=100)
    description = models.TextField('Описание', blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = translit_slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Категория форума"
        verbose_name = "Категории форума"

class ForumTopic(models.Model):
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField('Заголовок темы', max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)
    is_closed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Если название на русском, используем транслитерацию
            self.slug = translit_slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ForumPost(models.Model):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField('Сообщение')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Пост от {self.author} в теме {self.topic}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")
    discord_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

# Автоматическое создание профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()