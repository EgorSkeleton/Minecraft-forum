from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from django.db.models.signals import post_delete
import os
from .models import ArticleImage, Profile

# Автоматическое удаление файла с диска при удалении записи из БД
@receiver(post_delete, sender=ArticleImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

# То же самое для аватарок
@receiver(post_delete, sender=Profile)
def auto_delete_avatar_on_delete(sender, instance, **kwargs):
    if instance.avatar and instance.avatar.name != 'avatars/default.png':
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        # Используем get_or_create вместо простого создания
        Profile.objects.get_or_create(user=instance)
    else:
        # Если профиль уже есть, просто сохраняем его
        if hasattr(instance, 'profile'):
            instance.profile.save()