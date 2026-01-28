from django.urls import path
from . import views
from allauth.account.views import LoginView, SignupView


urlpatterns = [
    path('', views.home, name='home'),
    path('articles/', views.articles, name='articles'),
    path('forum/', views.forum, name='forum'),
    path('articles/add/', views.article_create, name='article_add'),
    path('update/<int:pk>/', views.article_update, name='article_update'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('forum/<slug:slug>/', views.category_detail, name='category_detail'),
    path('forum/topic/<slug:slug>/', views.topic_detail, name='topic_detail'),
    path('forum/<slug:category_slug>/new/', views.create_topic, name='create_topic'),
    path('login/', LoginView.as_view(template_name='account/login.html'), name='account_login'),
    path('signup/', SignupView.as_view(template_name='account/signup.html'), name='account_signup'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
]