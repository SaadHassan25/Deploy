"""
SEO-related views for robots.txt, redirects, and other SEO functionality
"""

from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import redirect
from django.views.decorators.cache import cache_page
from django.conf import settings


@cache_page(86400)  # Cache for 24 hours
def robots_txt(request):
    """Generate robots.txt dynamically"""
    base_url = f"{request.scheme}://{request.get_host()}"
    
    content = f"""User-agent: *
Allow: /

# Sitemaps
Sitemap: {base_url}/sitemap.xml

# Disallow admin and private areas
Disallow: /admin/
Disallow: /ckeditor/
Disallow: /accounts/
Disallow: /media/uploads/
Disallow: /static/

# Allow important pages
Allow: /static/css/
Allow: /static/js/
Allow: /static/images/
Allow: /media/blog_images/

# Crawl delay (optional)
Crawl-delay: 1

# Google-specific directives
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

# Block known bad bots
User-agent: SemrushBot
Disallow: /

User-agent: AhrefsBot
Disallow: /

User-agent: MJ12bot
Disallow: /
"""
    
    return HttpResponse(content, content_type='text/plain')


def redirect_old_urls(request, old_path):
    """Handle redirects from old URL structure"""
    # Example redirects - customize based on your old URL structure
    redirect_map = {
        'old-blog-url': '/blog/new-blog-url/',
        'category/old-category': '/category/new-category/',
        # Add more redirects as needed
    }
    
    if old_path in redirect_map:
        return HttpResponsePermanentRedirect(redirect_map[old_path])
    
    # If no specific redirect found, redirect to home
    return redirect('blog:home')


@cache_page(3600)  # Cache for 1 hour
def security_txt(request):
    """Generate security.txt for responsible disclosure"""
    content = """Contact: mailto:security@ai-bytes.tech
Expires: 2025-12-31T23:59:59.000Z
Encryption: https://ai-bytes.tech/pgp-key.txt
Acknowledgments: https://ai-bytes.tech/terms/
Policy: https://ai-bytes.tech/privacy/

"""
    
    return HttpResponse(content, content_type='text/plain')


def ads_txt(request):
    """Generate ads.txt for ad networks"""
    # Customize based on your advertising partners
    content = """# AI Bytes ads.txt
# Direct relationships only
# google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
# Add your advertising relationships here
"""
    
    return HttpResponse(content, content_type='text/plain')