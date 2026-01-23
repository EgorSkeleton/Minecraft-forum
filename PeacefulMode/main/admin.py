from django.contrib import admin
from .models import Articles, ArticleImage, TagOfVersion, TagOfGanre
from .models import ForumCategory, ForumTopic, ForumPost

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

class PostInline(admin.TabularInline):
    model = ForumPost
    extra = 1

@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'slug')

@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'category', 'author', 'created_at')
    list_filter = ('category', 'author') # Фильтры справа

@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('author', 'topic', 'created_at')
    # Поиск по тексту сообщений
    search_fields = ('content', 'author__username')