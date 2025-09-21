"""
Performance optimization middleware and utilities
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.conf import settings
import gzip
import re
from io import BytesIO


class HTMLMinifyMiddleware(MiddlewareMixin):
    """Middleware to minify HTML response for better performance"""
    
    def process_response(self, request, response):
        if (response.status_code == 200 and 
            response.get('Content-Type', '').startswith('text/html') and
            hasattr(response, 'content')):
            
            # Only minify in production or when explicitly enabled
            if not settings.DEBUG or getattr(settings, 'MINIFY_HTML', False):
                minified_content = self.minify_html(response.content.decode('utf-8'))
                response.content = minified_content.encode('utf-8')
                response['Content-Length'] = str(len(response.content))
        
        return response
    
    def minify_html(self, html):
        """Minify HTML by removing unnecessary whitespace and comments"""
        # Remove HTML comments (but keep IE conditional comments)
        html = re.sub(r'<!--(?!\s*(?:\[if\s|\]|<!)).*?-->', '', html, flags=re.DOTALL)
        
        # Remove extra whitespace between tags
        html = re.sub(r'>\s+<', '><', html)
        
        # Remove leading/trailing whitespace on lines
        html = re.sub(r'^\s+|\s+$', '', html, flags=re.MULTILINE)
        
        # Collapse multiple whitespace characters into single space
        html = re.sub(r'\s{2,}', ' ', html)
        
        # Remove whitespace around specific tags
        html = re.sub(r'\s*(</?(?:br|hr|img|input|meta|link)\s*/?>\s*)', r'\1', html, flags=re.IGNORECASE)
        
        return html.strip()


class CompressionMiddleware(MiddlewareMixin):
    """Middleware to compress responses with gzip"""
    
    def process_response(self, request, response):
        # Check if compression is acceptable
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        
        if ('gzip' in accept_encoding.lower() and
            response.status_code == 200 and
            len(response.content) > 200 and  # Only compress if content is larger than 200 bytes
            not response.get('Content-Encoding') and
            self.should_compress(response)):
            
            # Compress the content
            compressed_content = self.compress_content(response.content)
            if compressed_content:
                response.content = compressed_content
                response['Content-Encoding'] = 'gzip'
                response['Content-Length'] = str(len(response.content))
                response['Vary'] = 'Accept-Encoding'
        
        return response
    
    def should_compress(self, response):
        """Determine if response should be compressed"""
        content_type = response.get('Content-Type', '').lower()
        
        # Compress text-based content types
        compressible_types = [
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/json',
            'application/xml',
            'text/xml',
            'application/rss+xml',
            'application/atom+xml'
        ]
        
        return any(ct in content_type for ct in compressible_types)
    
    def compress_content(self, content):
        """Compress content using gzip"""
        try:
            buffer = BytesIO()
            with gzip.GzipFile(fileobj=buffer, mode='wb') as gz_file:
                gz_file.write(content)
            return buffer.getvalue()
        except Exception:
            return None


class CacheControlMiddleware(MiddlewareMixin):
    """Middleware to add appropriate cache headers"""
    
    def process_response(self, request, response):
        if response.status_code == 200:
            # Set cache headers based on content type and URL
            path = request.path
            
            if self.is_static_content(path, response):
                # Static content - cache for 1 year
                response['Cache-Control'] = 'public, max-age=31536000, immutable'
            elif self.is_blog_content(path):
                # Blog content - cache for 1 hour
                response['Cache-Control'] = 'public, max-age=3600'
            elif self.is_api_content(path):
                # API content - cache for 5 minutes
                response['Cache-Control'] = 'public, max-age=300'
            else:
                # Default - cache for 5 minutes
                response['Cache-Control'] = 'public, max-age=300'
        
        return response
    
    def is_static_content(self, path, response):
        """Check if this is static content"""
        static_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2']
        return any(path.endswith(ext) for ext in static_extensions)
    
    def is_blog_content(self, path):
        """Check if this is blog content"""
        return path.startswith('/blog/') or path == '/'
    
    def is_api_content(self, path):
        """Check if this is API content"""
        return path.startswith('/api/')


def add_performance_headers(get_response):
    """Middleware function to add performance-related headers"""
    
    def middleware(request):
        response = get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add performance hints
        if response.get('Content-Type', '').startswith('text/html'):
            # Preconnect to external domains
            response['Link'] = ', '.join([
                '<https://fonts.googleapis.com>; rel=preconnect',
                '<https://fonts.gstatic.com>; rel=preconnect; crossorigin',
                '<https://cdn.jsdelivr.net>; rel=preconnect',
                '<https://cdnjs.cloudflare.com>; rel=preconnect'
            ])
        
        return response
    
    return middleware