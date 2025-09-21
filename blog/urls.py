from django.urls import path
from . import views
from .seo_views import robots_txt, security_txt, ads_txt, redirect_old_urls

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
    
    # SEO-related URLs
    path('robots.txt', robots_txt, name='robots_txt'),
    path('.well-known/security.txt', security_txt, name='security_txt'),
    path('ads.txt', ads_txt, name='ads_txt'),
    path('redirect/<path:old_path>/', redirect_old_urls, name='redirect_old_urls'),
]
