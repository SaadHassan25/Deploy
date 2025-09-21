"""
SEO Analytics and Monitoring Dashboard
Track SEO performance, rankings, and optimization metrics
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import BlogPost, Category, Tag
from .seo_utils import SEOAnalyzer
import requests
import json


@staff_member_required
def seo_dashboard(request):
    """Main SEO dashboard view"""
    
    # Get overall SEO metrics
    posts = BlogPost.objects.filter(is_published=True)
    
    metrics = {
        'total_posts': posts.count(),
        'avg_seo_score': posts.aggregate(avg_score=Avg('seo_score'))['avg_score'] or 0,
        'posts_with_focus_keyword': posts.exclude(focus_keyword='').count(),
        'posts_with_meta_description': posts.exclude(meta_description='').count(),
        'posts_with_featured_image': posts.exclude(featured_image='').count(),
    }
    
    # SEO score distribution
    score_distribution = {
        'excellent': posts.filter(seo_score__gte=90).count(),
        'good': posts.filter(seo_score__gte=80, seo_score__lt=90).count(),
        'needs_improvement': posts.filter(seo_score__gte=60, seo_score__lt=80).count(),
        'poor': posts.filter(seo_score__lt=60).count(),
    }
    
    # Recent posts needing attention
    posts_needing_attention = posts.filter(seo_score__lt=70).order_by('seo_score')[:10]
    
    # Top performing posts
    top_posts = posts.filter(seo_score__gte=80).order_by('-seo_score')[:10]
    
    # Category performance
    category_performance = []
    for category in Category.objects.all():
        cat_posts = posts.filter(category=category)
        if cat_posts.exists():
            category_performance.append({
                'category': category,
                'post_count': cat_posts.count(),
                'avg_seo_score': cat_posts.aggregate(avg=Avg('seo_score'))['avg'] or 0,
                'needs_work': cat_posts.filter(seo_score__lt=70).count()
            })
    
    context = {
        'metrics': metrics,
        'score_distribution': score_distribution,
        'posts_needing_attention': posts_needing_attention,
        'top_posts': top_posts,
        'category_performance': category_performance,
    }
    
    return render(request, 'admin/seo_dashboard.html', context)


@staff_member_required
def seo_audit_report(request):
    """Generate comprehensive SEO audit report"""
    
    posts = BlogPost.objects.filter(is_published=True)
    
    # Common SEO issues
    issues = {
        'missing_meta_description': posts.filter(meta_description='').count(),
        'meta_description_too_short': posts.filter(
            meta_description__isnull=False
        ).exclude(meta_description='').extra(
            where=["LENGTH(meta_description) < 120"]
        ).count(),
        'meta_description_too_long': posts.filter(
            meta_description__isnull=False
        ).exclude(meta_description='').extra(
            where=["LENGTH(meta_description) > 160"]
        ).count(),
        'missing_focus_keyword': posts.filter(focus_keyword='').count(),
        'missing_featured_image': posts.filter(featured_image='').count(),
        'title_too_short': posts.extra(where=["LENGTH(title) < 30"]).count(),
        'title_too_long': posts.extra(where=["LENGTH(title) > 60"]).count(),
        'duplicate_meta_descriptions': get_duplicate_meta_descriptions(),
        'duplicate_titles': get_duplicate_titles(),
        'posts_with_noindex': posts.filter(noindex=True).count(),
    }
    
    # Recommendations
    recommendations = generate_seo_recommendations(issues)
    
    # Technical SEO checks
    technical_checks = perform_technical_seo_checks(request)
    
    context = {
        'issues': issues,
        'recommendations': recommendations,
        'technical_checks': technical_checks,
        'total_posts': posts.count(),
    }
    
    return render(request, 'admin/seo_audit_report.html', context)


@staff_member_required
def keyword_analysis(request):
    """Analyze keyword distribution and opportunities"""
    
    posts = BlogPost.objects.filter(is_published=True).exclude(focus_keyword='')
    
    # Keyword frequency
    keyword_frequency = {}
    for post in posts:
        if post.focus_keyword:
            keyword = post.focus_keyword.lower()
            keyword_frequency[keyword] = keyword_frequency.get(keyword, 0) + 1
    
    # Sort by frequency
    popular_keywords = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
    
    # Keyword cannibalization (multiple posts targeting same keyword)
    cannibalization_issues = [(k, v) for k, v in keyword_frequency.items() if v > 1]
    
    # Missing keywords (categories without focus keywords)
    categories_without_keywords = []
    for category in Category.objects.all():
        cat_posts = BlogPost.objects.filter(category=category, is_published=True)
        posts_with_keywords = cat_posts.exclude(focus_keyword='')
        if cat_posts.count() > 0 and posts_with_keywords.count() == 0:
            categories_without_keywords.append(category)
    
    context = {
        'popular_keywords': popular_keywords,
        'cannibalization_issues': cannibalization_issues,
        'categories_without_keywords': categories_without_keywords,
        'total_keywords': len(keyword_frequency),
    }
    
    return render(request, 'admin/keyword_analysis.html', context)


@staff_member_required
def performance_metrics(request):
    """Display performance and Core Web Vitals metrics"""
    
    # This would integrate with Google PageSpeed Insights API
    # For now, we'll provide placeholders and basic metrics
    
    # Get recent posts for analysis
    recent_posts = BlogPost.objects.filter(
        is_published=True,
        created_at__gte=timezone.now() - timedelta(days=30)
    )
    
    # Basic metrics
    metrics = {
        'posts_this_month': recent_posts.count(),
        'avg_word_count': get_average_word_count(recent_posts),
        'posts_with_images': recent_posts.exclude(featured_image='').count(),
        'avg_reading_time': get_average_reading_time(recent_posts),
    }
    
    # Simulated Core Web Vitals (in production, integrate with real APIs)
    core_web_vitals = {
        'lcp': 2.3,  # Largest Contentful Paint (seconds)
        'fid': 45,   # First Input Delay (milliseconds)
        'cls': 0.05, # Cumulative Layout Shift
    }
    
    context = {
        'metrics': metrics,
        'core_web_vitals': core_web_vitals,
        'recent_posts': recent_posts[:10],
    }
    
    return render(request, 'admin/performance_metrics.html', context)


def get_duplicate_meta_descriptions():
    """Find posts with duplicate meta descriptions"""
    from django.db.models import Count
    
    duplicates = BlogPost.objects.filter(
        is_published=True
    ).exclude(
        meta_description=''
    ).values(
        'meta_description'
    ).annotate(
        count=Count('meta_description')
    ).filter(count__gt=1)
    
    return duplicates.count()


def get_duplicate_titles():
    """Find posts with duplicate titles"""
    from django.db.models import Count
    
    duplicates = BlogPost.objects.filter(
        is_published=True
    ).values(
        'title'
    ).annotate(
        count=Count('title')
    ).filter(count__gt=1)
    
    return duplicates.count()


def generate_seo_recommendations(issues):
    """Generate actionable SEO recommendations based on issues"""
    recommendations = []
    
    if issues['missing_meta_description'] > 0:
        recommendations.append({
            'priority': 'high',
            'title': 'Add Meta Descriptions',
            'description': f"{issues['missing_meta_description']} posts are missing meta descriptions. This hurts click-through rates from search results.",
            'action': 'Add compelling meta descriptions (120-160 characters) to all posts.'
        })
    
    if issues['missing_focus_keyword'] > 0:
        recommendations.append({
            'priority': 'medium',
            'title': 'Set Focus Keywords',
            'description': f"{issues['missing_focus_keyword']} posts don't have focus keywords set.",
            'action': 'Research and set focus keywords for better content optimization.'
        })
    
    if issues['missing_featured_image'] > 0:
        recommendations.append({
            'priority': 'medium',
            'title': 'Add Featured Images',
            'description': f"{issues['missing_featured_image']} posts are missing featured images.",
            'action': 'Add relevant, optimized images to improve social sharing and engagement.'
        })
    
    if issues['duplicate_meta_descriptions'] > 0:
        recommendations.append({
            'priority': 'high',
            'title': 'Fix Duplicate Meta Descriptions',
            'description': 'Multiple posts have identical meta descriptions.',
            'action': 'Make each meta description unique and specific to the post content.'
        })
    
    if issues['title_too_short'] > 0:
        recommendations.append({
            'priority': 'medium',
            'title': 'Optimize Short Titles',
            'description': f"{issues['title_too_short']} posts have titles shorter than 30 characters.",
            'action': 'Expand titles to include more descriptive keywords (30-60 characters ideal).'
        })
    
    return recommendations


def perform_technical_seo_checks(request):
    """Perform technical SEO checks"""
    base_url = f"{request.scheme}://{request.get_host()}"
    
    checks = []
    
    # Check robots.txt
    try:
        robots_response = requests.get(f"{base_url}/robots.txt", timeout=5)
        checks.append({
            'name': 'Robots.txt',
            'status': 'pass' if robots_response.status_code == 200 else 'fail',
            'description': 'Robots.txt file is accessible' if robots_response.status_code == 200 else 'Robots.txt file not found'
        })
    except:
        checks.append({
            'name': 'Robots.txt',
            'status': 'fail',
            'description': 'Unable to access robots.txt file'
        })
    
    # Check sitemap.xml
    try:
        sitemap_response = requests.get(f"{base_url}/sitemap.xml", timeout=5)
        checks.append({
            'name': 'XML Sitemap',
            'status': 'pass' if sitemap_response.status_code == 200 else 'fail',
            'description': 'XML sitemap is accessible' if sitemap_response.status_code == 200 else 'XML sitemap not found'
        })
    except:
        checks.append({
            'name': 'XML Sitemap',
            'status': 'fail',
            'description': 'Unable to access XML sitemap'
        })
    
    # Check HTTPS
    checks.append({
        'name': 'HTTPS',
        'status': 'pass' if request.is_secure() else 'warning',
        'description': 'Site is using HTTPS' if request.is_secure() else 'Site should use HTTPS for better security and SEO'
    })
    
    return checks


def get_average_word_count(posts):
    """Calculate average word count for posts"""
    if not posts:
        return 0
    
    total_words = 0
    for post in posts:
        analyzer = SEOAnalyzer(post)
        total_words += analyzer.word_count
    
    return round(total_words / posts.count()) if posts.count() > 0 else 0


def get_average_reading_time(posts):
    """Calculate average reading time for posts"""
    if not posts:
        return 0
    
    total_time = sum(post.get_reading_time() for post in posts)
    return round(total_time / posts.count()) if posts.count() > 0 else 0