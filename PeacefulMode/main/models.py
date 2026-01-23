from django.db import models

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