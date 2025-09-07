from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('blogs/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('about/', views.about_us, name='about_us'),
    path('terms/', views.terms_conditions, name='terms_conditions'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('category/<str:category_name>/', views.category_posts, name='category_posts'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    path('tags/', views.all_tags, name='all_tags'),
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
]
