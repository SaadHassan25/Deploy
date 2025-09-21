"""
SEO Sitemaps for AI Blog
Dynamic XML sitemaps for better search engine crawling
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost, Category, Tag


class BlogPostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    
    def items(self):
        return BlogPost.objects.filter(is_published=True).order_by('-updated_at')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    
    def items(self):
        return Category.objects.all()
    
    def location(self, obj):
        return reverse('blog:category_posts', kwargs={'category_name': obj.name})


class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    
    def items(self):
        return Tag.objects.all()
    
    def location(self, obj):
        return obj.get_absolute_url()


class StaticPageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    
    def items(self):
        return [
            'blog:home',
            'blog:blog_list',
            'blog:all_tags',
            'blog:about_us',
            'blog:privacy_policy',
            'blog:terms_conditions',
        ]
    
    def location(self, item):
        return reverse(item)