from django.contrib import admin
from .models import Articles, ArticleImage, TagOfVersion, TagOfGanre

# Позволяет добавлять картинки прямо внутри страницы статьи
class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 3  # Сколько пустых полей для картинок выводить сразу

@admin.register(Articles)
class ArticlesAdmin(admin.ModelAdmin):
    # Что отображать в списке всех статей
    list_display = ('title', 'author', 'status', 'version')
    # По каким полям можно фильтровать
    list_filter = ('status', 'version_tag', 'ganre_tags')
    # По каким полям искать
    search_fields = ('title', 'short_text')
    # Подключаем картинки
    inlines = [ArticleImageInline]

admin.site.register(TagOfVersion)
admin.site.register(TagOfGanre)