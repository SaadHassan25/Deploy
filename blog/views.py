from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import BlogPost, Category, Comment, Newsletter, Tag
from .forms import CommentForm, NewsletterForm
import calendar

def home(request):
    """Home page with recent blog posts"""
    recent_posts = BlogPost.objects.filter(is_published=True)[:6]
    featured_post = BlogPost.objects.filter(is_published=True).first()
    total_posts = BlogPost.objects.filter(is_published=True).count()
    
    # Get post counts by category
    try:
        ai_count = BlogPost.objects.filter(category__name='AI', is_published=True).count()
        ml_count = BlogPost.objects.filter(category__name='ML', is_published=True).count()
        dl_count = BlogPost.objects.filter(category__name='DL', is_published=True).count()
        cv_count = BlogPost.objects.filter(category__name='CV', is_published=True).count()
        nlp_count = BlogPost.objects.filter(category__name='NLP', is_published=True).count()
    except Category.DoesNotExist:
        ai_count = ml_count = dl_count = cv_count = nlp_count = 0
    
    context = {
        'recent_posts': recent_posts,
        'featured_post': featured_post,
        'total_posts': total_posts,
        'ai_count': ai_count,
        'ml_count': ml_count,
        'dl_count': dl_count,
        'cv_count': cv_count,
        'nlp_count': nlp_count,
    }
    
    return render(request, 'blog/home.html', context)

def blog_list(request):
    """Blog listing page with pagination, search, and filtering"""
    blog_posts = BlogPost.objects.filter(is_published=True)
    
    # Handle search query
    query = request.GET.get('q')
    if query:
        blog_posts = blog_posts.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    # Handle category filtering
    category_filter = request.GET.get('category')
    if category_filter and category_filter != 'all':
        blog_posts = blog_posts.filter(category__name=category_filter)
    
    # Handle tag filtering
    tag_filter = request.GET.get('tag')
    if tag_filter:
        blog_posts = blog_posts.filter(tags__slug=tag_filter)
    
    # Handle month/year filtering for archives
    month = request.GET.get('month')
    year = request.GET.get('year')
    if month and year:
        blog_posts = blog_posts.filter(
            created_at__month=month,
            created_at__year=year
        )
    
    # Handle sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'oldest':
        blog_posts = blog_posts.order_by('created_at')
    elif sort_by == 'newest':
        blog_posts = blog_posts.order_by('-created_at')
    elif sort_by == 'title_asc':
        blog_posts = blog_posts.order_by('title')
    elif sort_by == 'title_desc':
        blog_posts = blog_posts.order_by('-title')
    elif sort_by == 'popular':
        # Order by comment count (most commented posts first)
        blog_posts = blog_posts.annotate(
            comment_count=Count('comment', filter=Q(comment__is_approved=True))
        ).order_by('-comment_count', '-created_at')
    
    # Sidebar data
    # Categories with post count
    categories = Category.objects.annotate(
        post_count=Count('blogpost', filter=Q(blogpost__is_published=True))
    ).filter(post_count__gt=0)
    
    # Archives - group posts by month/year
    archives_data = BlogPost.objects.filter(is_published=True).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        post_count=Count('id')
    ).order_by('-month')[:12]  # Last 12 months
    
    # Format archives data
    archives = []
    for archive in archives_data:
        month_date = archive['month']
        archives.append({
            'month': month_date.month,
            'year': month_date.year,
            'month_name': calendar.month_name[month_date.month],
            'post_count': archive['post_count']
        })
    
    # Featured posts (latest 3 posts)
    featured_posts = BlogPost.objects.filter(
        is_published=True
    ).order_by('-created_at')[:3]
    
    # Popular tags with post count
    popular_tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__is_published=True))
    ).filter(post_count__gt=0).order_by('-post_count', 'name')[:20]
    
    # Handle reading time filter (applied after getting queryset)
    reading_time_filter = request.GET.get('reading_time')
    if reading_time_filter:
        filtered_posts = []
        for post in blog_posts:
            reading_time = post.get_reading_time()
            if reading_time_filter == 'quick' and reading_time < 3:
                filtered_posts.append(post.id)
            elif reading_time_filter == 'medium' and 3 <= reading_time <= 7:
                filtered_posts.append(post.id)
            elif reading_time_filter == 'long' and reading_time > 7:
                filtered_posts.append(post.id)
        blog_posts = blog_posts.filter(id__in=filtered_posts)
    
    paginator = Paginator(blog_posts, 12)  # Show 12 posts per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'current_category': category_filter,
        'current_tag': tag_filter,
        'current_sort': sort_by,
        'current_reading_time': reading_time_filter,
        'categories': categories,
        'popular_tags': popular_tags,
        'archives': archives,
        'featured_posts': featured_posts,
        'total_posts': blog_posts.count(),
    }
    
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    """Individual blog post detail page with comments and sidebar"""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Get top-level approved comments for this post (comments without parent)
    comments = Comment.objects.filter(
        post=post, 
        is_approved=True, 
        parent=None
    ).order_by('created_at').prefetch_related('replies')
    
    # Handle comment form submission
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            
            # Handle reply to another comment
            parent_id = comment_form.cleaned_data.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id, post=post)
                    new_comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass
            
            new_comment.save()
            messages.success(request, 'Your comment has been submitted and is awaiting approval.')
            return redirect('blog:blog_detail', slug=post.slug)
    else:
        comment_form = CommentForm()
    
    # Calculate total comments count (including replies)
    total_comments_count = Comment.objects.filter(post=post, is_approved=True).count()
    
    # Sidebar data
    # Categories with post count
    categories = Category.objects.annotate(
        post_count=Count('blogpost', filter=Q(blogpost__is_published=True))
    ).filter(post_count__gt=0)
    
    # Archives - group posts by month/year
    archives_data = BlogPost.objects.filter(is_published=True).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        post_count=Count('id')
    ).order_by('-month')[:12]  # Last 12 months
    
    # Format archives data
    archives = []
    for archive in archives_data:
        month_date = archive['month']
        archives.append({
            'month': month_date.month,
            'year': month_date.year,
            'month_name': calendar.month_name[month_date.month],
            'post_count': archive['post_count']
        })
    
    # Featured posts (latest 2 posts excluding current)
    featured_posts = BlogPost.objects.filter(
        is_published=True
    ).exclude(slug=post.slug).order_by('-created_at')[:2]
    
    # Popular tags with post count
    popular_tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__is_published=True))
    ).filter(post_count__gt=0).order_by('-post_count', 'name')[:20]
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'comments_count': total_comments_count,
        'categories': categories,
        'popular_tags': popular_tags,
        'archives': archives,
        'featured_posts': featured_posts,
    }
    
    return render(request, 'blog/blog_detail.html', context)

def about_us(request):
    """About us page"""
    return render(request, 'blog/about_us.html')

def terms_conditions(request):
    """Terms and conditions page"""
    return render(request, 'blog/terms_conditions.html')

def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'blog/privacy_policy.html')

def category_posts(request, category_name):
    """Posts filtered by category"""
    category = get_object_or_404(Category, name=category_name)
    blog_posts = BlogPost.objects.filter(category=category, is_published=True)
    paginator = Paginator(blog_posts, 20)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/category_posts.html', {
        'page_obj': page_obj,
        'category': category
    })

@require_POST
def newsletter_signup(request):
    """Handle newsletter subscription via AJAX"""
    form = NewsletterForm(request.POST)
    
    if form.is_valid():
        email = form.cleaned_data['email']
        
        # Check if email already exists
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if created:
            # New subscription - send welcome email
            email_sent = send_welcome_email(email)
            
            if email_sent:
                return JsonResponse({
                    'success': True,
                    'message': 'Welcome aboard! 🎉 Check your email for a special welcome message with exclusive AI insights!'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for subscribing! You\'re now part of our AI community. (Welcome email will arrive shortly)'
                })
                
        elif newsletter.is_active:
            return JsonResponse({
                'success': False,
                'message': 'You\'re already part of our AI community! 🤖 Keep an eye on your inbox for our latest updates.'
            })
        else:
            # Reactivate inactive subscription
            newsletter.is_active = True
            newsletter.save()
            
            email_sent = send_welcome_email(email)
            
            if email_sent:
                return JsonResponse({
                    'success': True,
                    'message': 'Welcome back! 🎉 Your subscription has been reactivated. Check your email for our latest AI insights!'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'Welcome back! Your subscription has been reactivated. (Welcome email will arrive shortly)'
                })
    else:
        errors = []
        for field, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(error)
        
        return JsonResponse({
            'success': False,
            'message': ' '.join(errors) if errors else 'Please enter a valid email address.'
        })

def send_welcome_email(email):
    """Send beautifully formatted welcome email to new newsletter subscriber"""
    try:
        # Get current site URL for email links
        site_url = 'http://127.0.0.1:8000'  # In production, use your actual domain
        
        context = {
            'site_url': site_url,
        }
        
        # Render HTML and text versions
        html_content = render_to_string('email/newsletter_welcome.html', context)
        text_content = render_to_string('email/newsletter_welcome.txt', context)
        
        # Create the email
        subject = '🧠 Welcome to AI Blog Newsletter - Your Journey into AI Begins!'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]
        
        # Create EmailMultiAlternatives object for HTML email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email
        )
        
        # Attach HTML version
        msg.attach_alternative(html_content, "text/html")
        
        # Send the email
        msg.send()
        
        return True
        
    except Exception as e:
        # Log the error in production
        print(f"Failed to send welcome email to {email}: {str(e)}")
        return False

def tag_posts(request, slug):
    """Posts filtered by tag"""
    tag = get_object_or_404(Tag, slug=slug)
    blog_posts = BlogPost.objects.filter(tags=tag, is_published=True)
    
    # Sidebar data similar to blog_list
    categories = Category.objects.annotate(
        post_count=Count('blogpost', filter=Q(blogpost__is_published=True))
    ).filter(post_count__gt=0)
    
    popular_tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__is_published=True))
    ).filter(post_count__gt=0).order_by('-post_count', 'name')[:20]
    
    paginator = Paginator(blog_posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tag': tag,
        'categories': categories,
        'popular_tags': popular_tags,
        'total_posts': blog_posts.count(),
    }
    
    return render(request, 'blog/tag_posts.html', context)

def all_tags(request):
    """Display all tags with post counts"""
    tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__is_published=True))
    ).filter(post_count__gt=0).order_by('name')
    
    context = {
        'tags': tags,
    }
    
    return render(request, 'blog/all_tags.html', context)
