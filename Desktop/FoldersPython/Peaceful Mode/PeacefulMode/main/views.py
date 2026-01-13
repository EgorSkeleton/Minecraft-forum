from django.shortcuts import render, get_object_or_404, redirect
from .models import Articles
from .forms import ArticlesForm, ImageFormSet
from django.views.generic import DetailView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

def home(request):
    return render(request, 'main/home.html')

def articles(request):
    return render(request, 'main/articles.html')

def forum(request):
    return render(request, 'main/forum.html')

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