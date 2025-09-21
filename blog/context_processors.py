"""
SEO Context Processors for AI Blog
Provides SEO-related context data to all templates
"""

from django.conf import settings
from .seo_utils import StructuredDataGenerator, MetaTagGenerator


def seo_context(request):
    """Add SEO-related context to all templates"""
    
    # Basic SEO information
    base_url = f"{request.scheme}://{request.get_host()}"
    
    # Default meta tags for pages without specific content
    default_meta = {
        'site_name': 'AI Bytes',
        'site_description': 'Exploring the frontiers of artificial intelligence, machine learning, and emerging technologies through insightful articles and research.',
        'site_url': base_url,
        'site_logo': f"{base_url}/static/images/icon.png",
        'twitter_site': '@aibytes',  # Update with your Twitter handle
        'facebook_app_id': '',  # Add your Facebook App ID if you have one
    }
    
    # Organization schema (for all pages)
    organization_schema = StructuredDataGenerator.generate_organization_schema(request)
    
    return {
        'seo_meta': default_meta,
        'organization_schema': organization_schema,
        'base_url': base_url,
    }