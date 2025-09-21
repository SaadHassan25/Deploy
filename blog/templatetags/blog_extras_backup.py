from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
import re
import math
import calendar
import json
from ..seo_utils import StructuredDataGenerator, MetaTagGenerator, SEOAnalyzer

register = template.Library()

@register.filter
def reading_time(content):
    """
    Calculate reading time for given content
    Usage: {{ post.content|reading_time }}
    """
    if not content:
        return "1 min read"
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', str(content))
    
    # Count words
    word_count = len(text.split())
    
    # Calculate reading time (200 words per minute)
    minutes = math.ceil(word_count / 200)
    
    # Return formatted string
    if minutes <= 1:
        return "1 min read"
    else:
        return f"{minutes} min read"

@register.filter
def word_count(content):
    """
    Count words in content
    Usage: {{ post.content|word_count }}
    """
    if not content:
        return 0
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', str(content))
    
    # Count words
    return len(text.split())

@register.inclusion_tag('blog/comment_thread.html')
def render_comments(comments, max_depth=3):
    """
    Render threaded comments recursively
    Usage: {% render_comments comments %}
    """
    return {'comments': comments, 'max_depth': max_depth}

@register.inclusion_tag('blog/comment_single.html')
def render_comment(comment, depth=0, max_depth=3):
    """
    Render a single comment with its replies
    Usage: {% render_comment comment depth max_depth %}
    """
    return {
        'comment': comment,
        'depth': depth,
        'max_depth': max_depth,
        'can_reply': depth < max_depth
    }

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """Subtract the argument from the value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value

@register.filter 
def add(value, arg):
    """Add the argument to the value"""
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value

@register.simple_tag
def reading_stats(content):
    """
    Get comprehensive reading statistics
    Usage: {% reading_stats post.content as stats %}
    """
    if not content:
        return {'words': 0, 'reading_time': 1, 'reading_time_display': '1 min read'}
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', str(content))
    
    # Count words
    word_count = len(text.split())
    
    # Calculate reading time
    minutes = math.ceil(word_count / 200)
    minutes = max(1, minutes)
    
    # Format display
    if minutes == 1:
        display = "1 min read"
    else:
        display = f"{minutes} min read"
    
    return {
        'words': word_count,
        'reading_time': minutes,
        'reading_time_display': display
    }

@register.filter
def month_name(month_num):
    """
    Convert month number to month name
    Usage: {{ month_number|month_name }}
    """
    try:
        month_num = int(month_num)
        if 1 <= month_num <= 12:
            return calendar.month_name[month_num]
        return str(month_num)
    except (ValueError, TypeError):
        return str(month_num)

# SEO Template Tags

@register.inclusion_tag('blog/seo/meta_tags.html', takes_context=True)
def render_meta_tags(context, obj=None):
    """Render comprehensive meta tags for SEO"""
    request = context['request']
    
    if obj and hasattr(obj, 'get_seo_title'):
        # Blog post or page with SEO fields
        meta_tags = MetaTagGenerator.generate_basic_meta(obj, request)
        og_tags = MetaTagGenerator.generate_og_meta(obj, request)
        twitter_tags = MetaTagGenerator.generate_twitter_meta(obj, request)
    else:
        # Default site meta tags
        base_url = f"{request.scheme}://{request.get_host()}"
        meta_tags = {
            'title': 'AI Bytes - Exploring AI, ML, and Emerging Technologies',
            'description': 'Discover the latest insights in artificial intelligence, machine learning, and emerging technologies. Expert articles, tutorials, and research.',
            'keywords': 'artificial intelligence, machine learning, AI, ML, deep learning, technology blog',
            'canonical': f"{base_url}{request.path}",
            'robots': 'index, follow'
        }
        og_tags = {
            'og:title': meta_tags['title'],
            'og:description': meta_tags['description'],
            'og:type': 'website',
            'og:url': meta_tags['canonical'],
            'og:site_name': 'AI Bytes',
            'og:image': f"{base_url}/static/images/icon.png"
        }
        twitter_tags = {
            'twitter:card': 'summary',
            'twitter:title': meta_tags['title'],
            'twitter:description': meta_tags['description'],
            'twitter:site': '@aibytes',
            'twitter:image': f"{base_url}/static/images/icon.png"
        }
    
    return {
        'meta_tags': meta_tags,
        'og_tags': og_tags,
        'twitter_tags': twitter_tags
    }

@register.inclusion_tag('blog/seo/structured_data.html', takes_context=True)
def render_structured_data(context, obj=None, schema_type='article'):
    """Render JSON-LD structured data"""
    request = context['request']
    schemas = []
    
    # Always include organization schema
    organization_schema = StructuredDataGenerator.generate_organization_schema(request)
    schemas.append(organization_schema)
    
    if obj and hasattr(obj, 'get_seo_title'):
        if schema_type == 'article':
            article_schema = StructuredDataGenerator.generate_article_schema(obj, request)
            schemas.append(article_schema)
        
        # Add breadcrumb schema if we have breadcrumbs in context
        breadcrumbs = context.get('breadcrumbs')
        if breadcrumbs:
            breadcrumb_schema = StructuredDataGenerator.generate_breadcrumb_schema(breadcrumbs, request)
            schemas.append(breadcrumb_schema)
    
    return {'schemas': schemas}

@register.filter
def json_ld(value):
    """Convert Python dict to JSON-LD format"""
    return mark_safe(json.dumps(value, indent=2, ensure_ascii=False))

@register.simple_tag
def seo_score_color(score):
    """Return color class based on SEO score"""
    if score >= 80:
        return 'success'
    elif score >= 60:
        return 'warning'
    else:
        return 'danger'

@register.simple_tag
def seo_score_text(score):
    """Return text description based on SEO score"""
    if score >= 90:
        return 'Excellent'
    elif score >= 80:
        return 'Good'
    elif score >= 60:
        return 'Needs Improvement'
    elif score >= 40:
        return 'Poor'
    else:
        return 'Very Poor'

@register.filter
def truncate_chars(value, length):
    """Truncate string to specified length"""
    if len(value) <= length:
        return value
    return value[:length] + '...'

@register.filter
def highlight_keyword(text, keyword):
    """Highlight keyword in text"""
    if not keyword or not text:
        return text
    
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    highlighted = pattern.sub(f'<mark>{keyword}</mark>', text)
    return mark_safe(highlighted)

@register.simple_tag
def get_page_title(obj=None, default_title="AI Bytes"):
    """Get page title for SEO"""
    if obj and hasattr(obj, 'get_seo_title'):
        return obj.get_seo_title()
    return default_title

@register.simple_tag
def get_page_description(obj=None, default_description=""):
    """Get page description for SEO"""
    if obj and hasattr(obj, 'get_meta_description'):
        return obj.get_meta_description()
    return default_description

@register.filter
def reading_time(content):
    """
    Calculate reading time for given content
    Usage: {{ post.content|reading_time }}
    """
    if not content:
        return "1 min read"
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', str(content))
    
    # Count words
    word_count = len(text.split())
    
    # Calculate reading time (200 words per minute)
    minutes = math.ceil(word_count / 200)
    
    # Return formatted string
    if minutes <= 1:
        return "1 min read"
    else:
        return f"{minutes} min read"

@register.filter
def word_count(content):
    """
    Count words in content
    Usage: {{ post.content|word_count }}
    """
    if not content:
        return 0
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', str(content))
    
    # Count words
    return len(text.split())

@register.inclusion_tag('blog/comment_thread.html')
def render_comments(comments, max_depth=3):
    """
    Render threaded comments recursively
    Usage: {% render_comments comments %}
    """
    return {'comments': comments, 'max_depth': max_depth}

@register.inclusion_tag('blog/comment_single.html')
def render_comment(comment, depth=0, max_depth=3):
    """
    Render a single comment with its replies
    Usage: {% render_comment comment depth max_depth %}
    """
    return {
        'comment': comment,
        'depth': depth,
        'max_depth': max_depth,
        'can_reply': depth < max_depth
    }

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """Subtract the argument from the value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value

@register.filter 
def add(value, arg):
    """Add the argument to the value"""
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value

@register.simple_tag
def reading_stats(content):
    """
    Get comprehensive reading statistics
    Usage: {% reading_stats post.content as stats %}
    """
    if not content:
        return {'words': 0, 'reading_time': 1, 'reading_time_display': '1 min read'}
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', str(content))
    
    # Count words
    word_count = len(text.split())
    
    # Calculate reading time
    minutes = math.ceil(word_count / 200)
    minutes = max(1, minutes)
    
    # Format display
    if minutes == 1:
        display = "1 min read"
    else:
        display = f"{minutes} min read"
    
    return {
        'words': word_count,
        'reading_time': minutes,
        'reading_time_display': display
    }

@register.filter
def month_name(month_num):
    """
    Convert month number to month name
    Usage: {{ month_number|month_name }}
    """
    try:
        month_num = int(month_num)
        if 1 <= month_num <= 12:
            return calendar.month_name[month_num]
        return str(month_num)
    except (ValueError, TypeError):
        return str(month_num)
