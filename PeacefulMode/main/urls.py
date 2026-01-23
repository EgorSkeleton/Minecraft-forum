from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('articles/', views.articles, name='articles'),
    path('forum/', views.forum, name='forum'),
    path('articles/add/', views.article_create, name='article_add'),
    path('update/<int:pk>/', views.article_update, name='article_update'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
]