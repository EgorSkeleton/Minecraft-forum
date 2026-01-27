from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import transaction
from django.contrib import messages

# Модели
from .models import (
    Articles, TagOfGanre, TagOfVersion, ArticleImage, 
    ForumCategory, ForumTopic, ForumPost, Profile
)
# Формы
from .forms import ArticlesForm, NewTopicForm

# --- ГЛАВНАЯ И СТАТЬИ ---

def home(request):
    return render(request, 'main/home.html')

def articles(request):
    articles_list = Articles.objects.all().order_by('-id')
    current_genres = request.GET.getlist('genre')
    current_version = request.GET.get('version')
    active_filters = []

    if current_genres:
        for g_slug in current_genres:
            genre_obj = TagOfGanre.objects.filter(ganre=g_slug).first()
            if genre_obj:
                articles_list = articles_list.filter(ganre_tags=genre_obj)
                active_filters.append(genre_obj.get_ganre_display())

    if current_version:
        version_obj = TagOfVersion.objects.filter(edition=current_version).first()
        if version_obj:
            articles_list = articles_list.filter(version_tag=version_obj)
            active_filters.append(version_obj.get_edition_display())

    return render(request, 'main/articles.html', {
        'articles': articles_list.distinct(),
        'active_filters': active_filters,
        'selected_genres': current_genres,
        'selected_version': current_version
    })

# --- АДМИН-ПАНЕЛЬ И УПРАВЛЕНИЕ СТАТЬЯМИ ---

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    articles = Articles.objects.all().order_by('-id')
    return render(request, 'main/dashboard.html', {'articles': articles})

@user_passes_test(lambda u: u.is_superuser)
def article_create(request):
    if request.method == 'POST':
        form = ArticlesForm(request.POST, request.FILES)
        # Получаем список файлов из нашего мульти-поля
        screenshots = request.FILES.getlist('screenshots')
        
        if form.is_valid():
            # Сохраняем статью (логотип сохранится автоматически, так как он в модели)
            article = form.save() 
            
            # Сохраняем скриншоты (модель ArticleImage)
            for file in screenshots[:10]: # Ограничение 10 штук
                ArticleImage.objects.create(article=article, image=file)
                
            messages.success(request, "Статья успешно создана!")
            return redirect('dashboard')
    else:
        form = ArticlesForm()
    
    return render(request, 'main/article_create.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def article_update(request, pk):
    article = get_object_or_404(Articles, pk=pk)
    
    if request.method == 'POST':
        form = ArticlesForm(request.POST, request.FILES, instance=article)
        screenshots = request.FILES.getlist('screenshots')
        
        if form.is_valid():
            form.save()
            
            # Если загружены новые скриншоты, добавляем их
            if screenshots:
                for file in screenshots[:10]:
                    ArticleImage.objects.create(article=article, image=file)
            
            messages.success(request, "Статья обновлена!")
            return redirect('dashboard')
    else:
        form = ArticlesForm(instance=article)
    
    return render(request, 'main/article_update.html', {
        'form': form, 
        'article': article
    })

# --- ФОРУМ ---
# (Оставляю без изменений, так как там логика не менялась)
def forum(request):
    categories = ForumCategory.objects.all()
    return render(request, 'main/forum.html', {'categories': categories})

def category_detail(request, slug):
    category = get_object_or_404(ForumCategory, slug=slug)
    topics = category.topics.all().order_by('-created_at')
    return render(request, 'main/category_detail.html', {'category': category, 'topics': topics})

def topic_detail(request, slug):
    topic = get_object_or_404(ForumTopic, slug=slug)
    posts = topic.posts.all().order_by('created_at')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('account_login')
        content = request.POST.get('content')
        if content:
            ForumPost.objects.create(topic=topic, author=request.user, content=content)
            return redirect('topic_detail', slug=slug)

    return render(request, 'main/topic_detail.html', {'topic': topic, 'posts': posts})

@login_required
def create_topic(request, category_slug):
    category = get_object_or_404(ForumCategory, slug=category_slug)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    topic = form.save(commit=False)
                    topic.category = category
                    topic.author = request.user
                    topic.save() 
                    ForumPost.objects.create(
                        topic=topic, 
                        author=request.user, 
                        content=form.cleaned_data.get('content')
                    )
                return redirect('topic_detail', slug=topic.slug)
            except Exception as e:
                form.add_error(None, f"Ошибка при создании темы: {e}")
    else:
        form = NewTopicForm()
    return render(request, 'main/create_topic.html', {'form': form, 'category': category})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(ForumPost, pk=pk)
    topic = post.topic
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "У вас нет прав.")
        return redirect('topic_detail', slug=topic.slug)

    first_post = topic.posts.all().order_by('created_at').first()
    if post == first_post:
        topic.delete()
        return redirect('category_detail', slug=topic.category.slug)
    else:
        post.delete()
        return redirect('topic_detail', slug=topic.slug)

# --- ПРОФИЛЬ ---

@login_required
def profile_view(request):
    user = request.user
    topics_count = ForumTopic.objects.filter(author=user).count()
    posts_count = ForumPost.objects.filter(author=user).count()
    context = {
        'user': user,
        'topics_count': topics_count,
        'posts_count': posts_count,
    }
    return render(request, 'main/profile.html', context)