"""
SEO Utilities for AI Blog
Comprehensive SEO analysis and optimization tools similar to Yoast SEO
"""

import re
import json
from django.utils.text import slugify
from django.conf import settings
from textstat import flesch_reading_ease, flesch_kincaid_grade
import requests
from urllib.parse import urljoin, urlparse


class SEOAnalyzer:
    """Advanced SEO analysis class"""
    
    def __init__(self, post):
        self.post = post
        self.content_text = self.strip_html(post.content)
        self.word_count = len(self.content_text.split())
        
    def strip_html(self, html_content):
        """Remove HTML tags from content"""
        return re.sub(r'<[^>]*>', '', html_content)
    
    def calculate_keyword_density(self, keyword=None):
        """Calculate keyword density in content"""
        if not keyword:
            keyword = self.post.focus_keyword
        
        if not keyword or self.word_count == 0:
            return 0
        
        keyword_count = self.content_text.lower().count(keyword.lower())
        return (keyword_count / self.word_count) * 100
    
    def get_readability_score(self):
        """Calculate readability scores"""
        if not self.content_text:
            return {'flesch_ease': 0, 'flesch_kincaid': 0, 'level': 'Unknown'}
        
        try:
            flesch_ease = flesch_reading_ease(self.content_text)
            flesch_kincaid = flesch_kincaid_grade(self.content_text)
            
            # Determine reading level
            if flesch_ease >= 90:
                level = 'Very Easy'
            elif flesch_ease >= 80:
                level = 'Easy'
            elif flesch_ease >= 70:
                level = 'Fairly Easy'
            elif flesch_ease >= 60:
                level = 'Standard'
            elif flesch_ease >= 50:
                level = 'Fairly Difficult'
            elif flesch_ease >= 30:
                level = 'Difficult'
            else:
                level = 'Very Difficult'
                
            return {
                'flesch_ease': round(flesch_ease, 1),
                'flesch_kincaid': round(flesch_kincaid, 1),
                'level': level
            }
        except:
            return {'flesch_ease': 0, 'flesch_kincaid': 0, 'level': 'Unknown'}
    
    def analyze_headings(self):
        """Analyze heading structure (H1, H2, H3, etc.)"""
        headings = {
            'h1': re.findall(r'<h1[^>]*>(.*?)</h1>', self.post.content, re.IGNORECASE | re.DOTALL),
            'h2': re.findall(r'<h2[^>]*>(.*?)</h2>', self.post.content, re.IGNORECASE | re.DOTALL),
            'h3': re.findall(r'<h3[^>]*>(.*?)</h3>', self.post.content, re.IGNORECASE | re.DOTALL),
            'h4': re.findall(r'<h4[^>]*>(.*?)</h4>', self.post.content, re.IGNORECASE | re.DOTALL),
            'h5': re.findall(r'<h5[^>]*>(.*?)</h5>', self.post.content, re.IGNORECASE | re.DOTALL),
            'h6': re.findall(r'<h6[^>]*>(.*?)</h6>', self.post.content, re.IGNORECASE | re.DOTALL),
        }
        
        # Count headings with focus keyword
        keyword_in_headings = 0
        if self.post.focus_keyword:
            for level, heading_list in headings.items():
                for heading in heading_list:
                    heading_text = self.strip_html(heading)
                    if self.post.focus_keyword.lower() in heading_text.lower():
                        keyword_in_headings += 1
        
        return {
            'structure': headings,
            'total_headings': sum(len(h) for h in headings.values()),
            'keyword_in_headings': keyword_in_headings
        }
    
    def analyze_links(self):
        """Analyze internal and external links"""
        links = re.findall(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', 
                          self.post.content, re.IGNORECASE | re.DOTALL)
        
        internal_links = []
        external_links = []
        
        for href, text in links:
            if href.startswith(('http://', 'https://')):
                domain = urlparse(href).netloc
                if 'ai-bytes.tech' in domain or 'localhost' in domain:
                    internal_links.append({'url': href, 'text': self.strip_html(text)})
                else:
                    external_links.append({'url': href, 'text': self.strip_html(text)})
            elif href.startswith('/'):
                internal_links.append({'url': href, 'text': self.strip_html(text)})
        
        return {
            'internal_links': internal_links,
            'external_links': external_links,
            'total_links': len(links),
            'internal_count': len(internal_links),
            'external_count': len(external_links)
        }
    
    def analyze_images(self):
        """Analyze images in content"""
        images = re.findall(r'<img[^>]*>', self.post.content, re.IGNORECASE)
        
        images_with_alt = 0
        images_with_title = 0
        keyword_in_alt = 0
        
        for img in images:
            if 'alt=' in img:
                images_with_alt += 1
                alt_match = re.search(r'alt=["\']([^"\']*)["\']', img, re.IGNORECASE)
                if alt_match and self.post.focus_keyword:
                    alt_text = alt_match.group(1)
                    if self.post.focus_keyword.lower() in alt_text.lower():
                        keyword_in_alt += 1
            
            if 'title=' in img:
                images_with_title += 1
        
        return {
            'total_images': len(images),
            'images_with_alt': images_with_alt,
            'images_with_title': images_with_title,
            'keyword_in_alt': keyword_in_alt,
            'alt_percentage': (images_with_alt / len(images) * 100) if images else 0
        }
    
    def get_comprehensive_analysis(self):
        """Get complete SEO analysis"""
        keyword_density = self.calculate_keyword_density()
        readability = self.get_readability_score()
        headings = self.analyze_headings()
        links = self.analyze_links()
        images = self.analyze_images()
        
        return {
            'basic': {
                'word_count': self.word_count,
                'character_count': len(self.content_text),
                'paragraph_count': len(self.content_text.split('\n\n')),
                'sentence_count': len(re.split(r'[.!?]+', self.content_text))
            },
            'keyword_analysis': {
                'focus_keyword': self.post.focus_keyword,
                'keyword_density': round(keyword_density, 2),
                'keyword_count': self.content_text.lower().count(self.post.focus_keyword.lower()) if self.post.focus_keyword else 0,
                'optimal_density': 0.5 <= keyword_density <= 2.5 if keyword_density else False
            },
            'readability': readability,
            'headings': headings,
            'links': links,
            'images': images,
            'seo_score': self.post.seo_score
        }


class StructuredDataGenerator:
    """Generate JSON-LD structured data for SEO"""
    
    @staticmethod
    def generate_article_schema(post, request=None):
        """Generate Article schema for blog posts"""
        base_url = 'https://ai-bytes.tech' if request is None else f"{request.scheme}://{request.get_host()}"
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": post.get_seo_title(),
            "description": post.get_meta_description(),
            "image": [],
            "author": {
                "@type": "Person",
                "name": post.author.get_full_name() or post.author.username,
                "url": f"{base_url}/author/{post.author.username}/"
            },
            "publisher": {
                "@type": "Organization",
                "name": "AI Bytes",
                "url": base_url,
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{base_url}/static/images/icon.png"
                }
            },
            "datePublished": post.created_at.isoformat(),
            "dateModified": post.updated_at.isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{base_url}{post.get_absolute_url()}"
            }
        }
        
        # Add images
        if post.featured_image:
            schema["image"].append(f"{base_url}{post.featured_image.url}")
        if post.og_image:
            schema["image"].append(f"{base_url}{post.og_image.url}")
        
        # Add article section
        if post.category:
            schema["articleSection"] = post.category.get_name_display()
        
        # Add keywords
        if post.tags.exists():
            schema["keywords"] = [tag.name for tag in post.tags.all()]
        
        return schema
    
    @staticmethod
    def generate_organization_schema(request=None):
        """Generate Organization schema"""
        base_url = 'https://ai-bytes.tech' if request is None else f"{request.scheme}://{request.get_host()}"
        
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "AI Bytes",
            "url": base_url,
            "logo": f"{base_url}/static/images/icon.png",
            "description": "Exploring the frontiers of artificial intelligence, machine learning, and emerging technologies through insightful articles and research.",
            "sameAs": [
                # Add your social media URLs here
                # "https://twitter.com/aibytes",
                # "https://linkedin.com/company/aibytes"
            ]
        }
    
    @staticmethod
    def generate_breadcrumb_schema(breadcrumbs, request=None):
        """Generate BreadcrumbList schema"""
        base_url = 'https://ai-bytes.tech' if request is None else f"{request.scheme}://{request.get_host()}"
        
        breadcrumb_list = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": []
        }
        
        for index, (name, url) in enumerate(breadcrumbs, 1):
            item = {
                "@type": "ListItem",
                "position": index,
                "name": name,
                "item": f"{base_url}{url}" if url.startswith('/') else url
            }
            breadcrumb_list["itemListElement"].append(item)
        
        return breadcrumb_list


class MetaTagGenerator:
    """Generate meta tags for SEO"""
    
    @staticmethod
    def generate_basic_meta(post, request=None):
        """Generate basic meta tags"""
        base_url = 'https://ai-bytes.tech' if request is None else f"{request.scheme}://{request.get_host()}"
        
        meta_tags = {
            'title': post.get_seo_title(),
            'description': post.get_meta_description(),
            'keywords': ', '.join([tag.name for tag in post.tags.all()]) if post.tags.exists() else '',
            'canonical': post.canonical_url or f"{base_url}{post.get_absolute_url()}",
            'robots': 'noindex, nofollow' if post.noindex or post.nofollow else 'index, follow'
        }
        
        return meta_tags
    
    @staticmethod
    def generate_og_meta(post, request=None):
        """Generate Open Graph meta tags"""
        base_url = 'https://ai-bytes.tech' if request is None else f"{request.scheme}://{request.get_host()}"
        
        og_tags = {
            'og:title': post.get_og_title(),
            'og:description': post.get_og_description(),
            'og:type': 'article',
            'og:url': f"{base_url}{post.get_absolute_url()}",
            'og:site_name': 'AI Bytes',
            'article:author': post.author.get_full_name() or post.author.username,
            'article:published_time': post.created_at.isoformat(),
            'article:modified_time': post.updated_at.isoformat(),
            'article:section': post.category.get_name_display() if post.category else ''
        }
        
        # Add image
        og_image_url = post.get_og_image_url()
        if og_image_url:
            og_tags['og:image'] = f"{base_url}{og_image_url}"
            og_tags['og:image:width'] = '1200'
            og_tags['og:image:height'] = '630'
        
        # Add tags
        if post.tags.exists():
            og_tags['article:tag'] = [tag.name for tag in post.tags.all()]
        
        return og_tags
    
    @staticmethod
    def generate_twitter_meta(post, request=None):
        """Generate Twitter Card meta tags"""
        base_url = 'https://ai-bytes.tech' if request is None else f"{request.scheme}://{request.get_host()}"
        
        twitter_tags = {
            'twitter:card': 'summary_large_image',
            'twitter:title': post.get_twitter_title(),
            'twitter:description': post.get_twitter_description(),
            'twitter:site': '@aibytes',  # Add your Twitter handle
            'twitter:creator': f'@{post.author.username}'
        }
        
        # Add image
        og_image_url = post.get_og_image_url()
        if og_image_url:
            twitter_tags['twitter:image'] = f"{base_url}{og_image_url}"
        
        return twitter_tags


def calculate_reading_time(content):
    """Calculate estimated reading time"""
    text = re.sub(r'<[^>]*>', '', content)
    word_count = len(text.split())
    # Average reading speed: 200 words per minute
    reading_time = max(1, round(word_count / 200))
    return reading_time


def generate_slug_suggestions(title, existing_slugs=None):
    """Generate SEO-friendly slug suggestions"""
    base_slug = slugify(title)
    suggestions = [base_slug]
    
    if existing_slugs and base_slug in existing_slugs:
        counter = 1
        while f"{base_slug}-{counter}" in existing_slugs:
            counter += 1
        suggestions.append(f"{base_slug}-{counter}")
    
    # Additional variations
    words = title.split()
    if len(words) > 3:
        # Shorter version with key words
        key_words = words[:3]
        short_slug = slugify(' '.join(key_words))
        if short_slug not in suggestions:
            suggestions.append(short_slug)
    
    return suggestions


def validate_seo_requirements(post):
    """Validate SEO requirements and return issues"""
    issues = []
    
    # Title validation
    title_length = len(post.get_seo_title())
    if title_length < 30:
        issues.append({'type': 'error', 'message': 'SEO title is too short (less than 30 characters)'})
    elif title_length > 60:
        issues.append({'type': 'warning', 'message': 'SEO title is too long (more than 60 characters)'})
    
    # Meta description validation
    meta_desc = post.get_meta_description()
    if not meta_desc:
        issues.append({'type': 'error', 'message': 'Meta description is missing'})
    elif len(meta_desc) < 120:
        issues.append({'type': 'warning', 'message': 'Meta description is too short'})
    elif len(meta_desc) > 160:
        issues.append({'type': 'warning', 'message': 'Meta description is too long'})
    
    # Focus keyword validation
    if not post.focus_keyword:
        issues.append({'type': 'warning', 'message': 'No focus keyword set'})
    
    # Content length validation
    content_words = len(re.sub(r'<[^>]*>', '', post.content).split())
    if content_words < 300:
        issues.append({'type': 'warning', 'message': 'Content is too short for optimal SEO (less than 300 words)'})
    
    # Image validation
    if not post.featured_image and not post.og_image:
        issues.append({'type': 'warning', 'message': 'No featured image set'})
    
    return issues