from django.shortcuts import render, get_object_or_404, redirect
from .models import Articles
from .forms import ArticlesForm, ImageFormSet
from .forms import NewTopicForm
from django.views.generic import DetailView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from .models import ForumCategory, ForumTopic, ForumPost
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

def home(request):
    return render(request, 'main/home.html')

def articles(request):
    return render(request, 'main/articles.html')

def forum(request):
    categories = ForumCategory.objects.all()
    return render(request, 'main/forum.html', {'categories': categories})

@user_passes_test(lambda u: u.is_superuser)
def article_create(request):
    if request.method == 'POST':
        form = ArticlesForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            article = form.save()
            formset.instance = article
            formset.save()
            return redirect('dashboard')
    else:
        form = ArticlesForm()
        formset = ImageFormSet()
    return render(request, 'main/article_create.html', {'form': form, 'formset': formset})

@user_passes_test(lambda u: u.is_superuser)
def article_update(request, pk):
    article = get_object_or_404(Articles, pk=pk)
    if request.method == 'POST':
        form = ArticlesForm(request.POST, instance=article)
        formset = ImageFormSet(request.POST, request.FILES, instance=article)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('dashboard')
    else:
        form = ArticlesForm(instance=article)
        formset = ImageFormSet(instance=article)
    return render(request, 'main/article_update.html', {'form': form, 'formset': formset})

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    articles = Articles.objects.all().order_by('-id')
    return render(request, 'main/dashboard.html', {'articles': articles})

def category_detail(request, slug):
    category = get_object_or_404(ForumCategory, slug=slug)
    topics = category.topics.all().order_by('-created_at')
    return render(request, 'main/category_detail.html', {'category': category, 'topics': topics})

def category_detail(request, slug):
    category = get_object_or_404(ForumCategory, slug=slug)
    topics = category.topics.all().order_by('-created_at')
    return render(request, 'main/category_detail.html', {
        'category': category, 
        'topics': topics
    })

# Просмотр темы и отправка сообщения
def topic_detail(request, slug):
    topic = get_object_or_404(ForumTopic, slug=slug)
    posts = topic.posts.all().order_by('created_at')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('account_login')
        
        content = request.POST.get('content')
        if content:
            ForumPost.objects.create(
                topic=topic,
                author=request.user,
                content=content
            )
            return redirect('topic_detail', slug=slug)

    return render(request, 'main/topic_detail.html', {
        'topic': topic,
        'posts': posts
    })

@login_required
def create_topic(request, category_slug):
    category = get_object_or_404(ForumCategory, slug=category_slug)
    
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            with transaction.atomic(): # Гарантируем, что либо создастся всё, либо ничего
                # 1. Создаем тему
                topic = form.save(commit=False)
                topic.category = category
                topic.author = request.user
                topic.save()
                
                # 2. Создаем первый пост в этой теме
                ForumPost.objects.create(
                    topic=topic,
                    author=request.user,
                    content=form.cleaned_data.get('content')
                )
                
            return redirect('topic_detail', slug=topic.slug)
    else:
        form = NewTopicForm()
    
    return render(request, 'main/create_topic.html', {'form': form, 'category': category})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(ForumPost, pk=pk)
    topic = post.topic
    
    # ПРОВЕРКА ПРАВ: только автор или модератор (is_staff)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "У вас нет прав для удаления этого сообщения.")
        return redirect('topic_detail', slug=topic.slug)

    # ЛОГИКА: Если это первый пост в теме — удаляем всю тему
    first_post = topic.posts.all().order_by('created_at').first()
    
    if post == first_post:
        topic.delete()
        messages.success(request, "Тема удалена, так как был удален первый пост.")
        return redirect('category_detail', slug=topic.category.slug)
    else:
        post.delete()
        messages.success(request, "Сообщение удалено.")
        return redirect('topic_detail', slug=topic.slug)
    
