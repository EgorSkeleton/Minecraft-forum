from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import transaction
from django.contrib import messages
from django.conf import settings
import requests
import time

# Модели
from .models import (
    Articles, TagOfGanre, TagOfVersion, ArticleImage, 
    ForumCategory, ForumTopic, ForumPost, Profile
)
# Формы
from .forms import ArticlesForm, NewTopicForm, UserUpdateForm, ProfileUpdateForm

# --- ГЛАВНАЯ И СТАТЬИ ---

def check_content_censorship(text):
    """
    Чистая нейросетевая модерация через RuBERT без жестких списков.
    """
    api_token = getattr(settings, 'HF_API_TOKEN', "").strip()
    
    # Актуальный адрес роутера для классификации
    API_URL = "https://router.huggingface.co/hf-inference/models/cointegrated/rubert-tiny-toxicity"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": text,
        "options": {"wait_for_model": True}
    }

    try:
        print(f"--- [API] Анализ текста: '{text[:30]}...' ---")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                predictions = result[0]
                
                # Находим метку с самым высоким весом
                top_prediction = max(predictions, key=lambda x: x['score'])
                label = top_prediction['label'].lower()
                score = top_prediction['score']
                
                print(f"--- [API SUCCESS] Вердикт: {label} (Уверенность: {score:.2f}) ---")

                # ЛОГИКА: Разрешаем публикацию ТОЛЬКО если главная метка 'non-toxic'
                # Если модель выбрала 'insult', 'toxic', 'threat' и т.д. как основные — блокируем.
                if label == 'non-toxic':
                    return True
                
                # Если мы здесь, значит главная метка — что-то плохое
                return False
            
            return True # Пропускаем, если формат ответа неожиданный

        print(f"--- [!] Ошибка API ({response.status_code}): {response.text} ---")
        return True

    except Exception as e:
        print(f"--- [!] Ошибка связи: {e} ---")
        return True

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
    first_post = topic.posts.all().order_by('created_at').first()
    replies = topic.posts.exclude(id=first_post.id).order_by('-created_at')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('account_login')
            
        content = request.POST.get('content')
        if content:
            # ПРОВЕРКА НЕЙРОСЕТЬЮ
            if check_content_censorship(content):
                ForumPost.objects.create(topic=topic, author=request.user, content=content)
                return redirect('topic_detail', slug=slug)
            else:
                messages.error(request, "Ваше сообщение не прошло модерацию (обнаружена токсичность или мат).")
                # Сообщение не сохраняется, пользователь видит ошибку

    return render(request, 'main/topic_detail.html', {
        'topic': topic,
        'first_post': first_post, # Передаем отдельно
        'replies': replies,       # Передаем отдельно
        'posts': topic.posts.all() # Оставляем для совместимости, если нужно
    })

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
def delete_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    
    # Проверяем, что удаляет автор или админ
    if post.author == request.user or request.user.is_superuser:
        topic_slug = post.topic.slug
        post.delete()
        return redirect('topic_detail', slug=topic_slug)
    
    # Если прав нет, просто возвращаем назад
    return redirect('forum')

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

@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        # Предполагаем, что связь Profile создается автоматически или уже существует
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Ваш профиль был обновлен!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'main/profile_edit.html', context)

def article_detail(request, pk):
    # Получаем статью или 404, если её нет
    article = get_object_or_404(Articles, pk=pk)
    # Скриншоты достаются через related_name='screenshots', который мы указывали в модели
    return render(request, 'main/article_detail.html', {
        'article': article,
    })

