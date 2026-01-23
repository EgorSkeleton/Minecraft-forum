from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('articles/', views.articles, name='articles'),
    path('forum/', views.forum, name='forum'),
    path('articles/add/', views.article_create, name='article_add'),
    path('update/<int:pk>/', views.article_update, name='article_update'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('forum/<slug:slug>/', views.category_detail, name='category_detail'),
    path('forum/topic/<slug:slug>/', views.topic_detail, name='topic_detail'),
    path('forum/<slug:category_slug>/new/', views.create_topic, name='create_topic'),
]