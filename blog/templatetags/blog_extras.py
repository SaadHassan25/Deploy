from django import template
import re
import math
import calendar

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
