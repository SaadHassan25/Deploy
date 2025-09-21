from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
import re
import math

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # SEO fields for tag pages
    seo_title = models.CharField(
        max_length=60, 
        blank=True, 
        help_text="SEO title for tag page (60 chars max)"
    )
    meta_description = models.TextField(
        max_length=160, 
        blank=True, 
        help_text="Meta description for tag page (160 chars max)"
    )
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:tag_posts', kwargs={'slug': self.slug})
    
    def get_seo_title(self):
        """Get SEO title for tag page"""
        return self.seo_title or f"{self.name} - AI Blog Posts"
    
    def get_meta_description(self):
        """Get meta description for tag page"""
        if self.meta_description:
            return self.meta_description
        return f"Explore {self.name} articles on AI Blog. {self.description or 'Latest insights and tutorials.'}"
    
    def __str__(self):
        return self.name

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('AI', 'Artificial Intelligence'),
        ('ML', 'Machine Learning'),
        ('DL', 'Deep Learning'),
        ('CV', 'Computer Vision'),
        ('NLP', 'Natural Language Processing'),
    ]
    
    name = models.CharField(max_length=3, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)
    
    # SEO fields for category pages
    seo_title = models.CharField(
        max_length=60, 
        blank=True, 
        help_text="SEO title for category page (60 chars max)"
    )
    meta_description = models.TextField(
        max_length=160, 
        blank=True, 
        help_text="Meta description for category page (160 chars max)"
    )
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def get_seo_title(self):
        """Get SEO title for category page"""
        return self.seo_title or f"{self.get_name_display()} - AI Blog"
    
    def get_meta_description(self):
        """Get meta description for category page"""
        if self.meta_description:
            return self.meta_description
        return f"Discover {self.get_name_display()} articles and tutorials on AI-Bytes.tech. {self.description or 'Latest insights and expert analysis.'}"
    
    def __str__(self):
        return self.get_name_display()

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    content = RichTextUploadingField(config_name='blog_content')
    excerpt = models.TextField(max_length=300, help_text="Brief description of the blog post")
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    
    # SEO Fields (Yoast-like functionality)
    seo_title = models.CharField(
        max_length=60, 
        blank=True, 
        help_text="SEO title (60 chars max). Leave blank to use post title."
    )
    meta_description = models.TextField(
        max_length=160, 
        blank=True, 
        help_text="Meta description (160 chars max) for search engines."
    )
    focus_keyword = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Primary keyword to optimize this post for."
    )
    
    # Open Graph & Social Media
    og_title = models.CharField(
        max_length=95, 
        blank=True, 
        help_text="Facebook/Open Graph title (95 chars max)"
    )
    og_description = models.TextField(
        max_length=300, 
        blank=True, 
        help_text="Facebook/Open Graph description (300 chars max)"
    )
    og_image = models.ImageField(
        upload_to='blog_images/og/', 
        blank=True, 
        null=True,
        help_text="Facebook/Open Graph image (1200x630px recommended)"
    )
    
    # Twitter Card
    twitter_title = models.CharField(
        max_length=70, 
        blank=True, 
        help_text="Twitter card title (70 chars max)"
    )
    twitter_description = models.TextField(
        max_length=200, 
        blank=True, 
        help_text="Twitter card description (200 chars max)"
    )
    
    # Advanced SEO
    canonical_url = models.URLField(
        blank=True, 
        help_text="Canonical URL if different from default"
    )
    noindex = models.BooleanField(
        default=False, 
        help_text="Prevent search engines from indexing this post"
    )
    nofollow = models.BooleanField(
        default=False, 
        help_text="Prevent search engines from following links in this post"
    )
    
    # SEO Score (calculated automatically)
    seo_score = models.IntegerField(
        default=0, 
        help_text="SEO score out of 100 (calculated automatically)"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Calculate SEO score before saving
        self.seo_score = self.calculate_seo_score()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:blog_detail', kwargs={'slug': self.slug})
    
    def get_reading_time(self):
        """Calculate estimated reading time based on content length"""
        # Remove HTML tags if any
        text = re.sub(r'<[^>]*>', '', self.content)
        
        # Count words (average reading speed is 200-250 words per minute)
        word_count = len(text.split())
        
        # Calculate reading time (using 200 words per minute)
        reading_time_minutes = math.ceil(word_count / 200)
        
        # Return at least 1 minute
        return max(1, reading_time_minutes)
    
    def get_reading_time_display(self):
        """Get reading time in a user-friendly format"""
        minutes = self.get_reading_time()
        if minutes == 1:
            return "1 min read"
        else:
            return f"{minutes} min read"
    
    # SEO Utility Methods
    def get_seo_title(self):
        """Get SEO title, fallback to post title"""
        return self.seo_title or self.title
    
    def get_meta_description(self):
        """Get meta description, fallback to excerpt"""
        return self.meta_description or self.excerpt
    
    def get_og_title(self):
        """Get Open Graph title, fallback to SEO title"""
        return self.og_title or self.get_seo_title()
    
    def get_og_description(self):
        """Get Open Graph description, fallback to meta description"""
        return self.og_description or self.get_meta_description()
    
    def get_og_image_url(self):
        """Get Open Graph image URL, fallback to featured image"""
        if self.og_image:
            return self.og_image.url
        elif self.featured_image:
            return self.featured_image.url
        return None
    
    def get_twitter_title(self):
        """Get Twitter title, fallback to SEO title"""
        return self.twitter_title or self.get_seo_title()
    
    def get_twitter_description(self):
        """Get Twitter description, fallback to meta description"""
        return self.twitter_description or self.get_meta_description()
    
    def calculate_seo_score(self):
        """Calculate SEO score based on various factors"""
        score = 0
        
        # Title optimization (20 points)
        if self.seo_title:
            if 30 <= len(self.seo_title) <= 60:
                score += 20
            elif len(self.seo_title) < 30:
                score += 10
        elif 30 <= len(self.title) <= 60:
            score += 15
        
        # Meta description (20 points)
        if self.meta_description:
            if 120 <= len(self.meta_description) <= 160:
                score += 20
            elif len(self.meta_description) < 120:
                score += 10
        
        # Focus keyword in title (15 points)
        if self.focus_keyword:
            if self.focus_keyword.lower() in self.title.lower():
                score += 15
            elif self.seo_title and self.focus_keyword.lower() in self.seo_title.lower():
                score += 15
        
        # Focus keyword in content (15 points)
        if self.focus_keyword:
            content_text = re.sub(r'<[^>]*>', '', self.content).lower()
            keyword_count = content_text.count(self.focus_keyword.lower())
            content_words = len(content_text.split())
            if content_words > 0:
                keyword_density = (keyword_count / content_words) * 100
                if 0.5 <= keyword_density <= 2.5:  # Optimal keyword density
                    score += 15
                elif keyword_density > 0:
                    score += 8
        
        # Featured image (10 points)
        if self.featured_image or self.og_image:
            score += 10
        
        # Content length (10 points)
        content_words = len(re.sub(r'<[^>]*>', '', self.content).split())
        if content_words >= 300:
            score += 10
        elif content_words >= 150:
            score += 5
        
        # Slug optimization (5 points)
        if self.focus_keyword and self.focus_keyword.lower().replace(' ', '-') in self.slug:
            score += 5
        
        # Internal/External links (5 points)
        link_count = len(re.findall(r'<a[^>]*>', self.content))
        if link_count >= 3:
            score += 5
        elif link_count >= 1:
            score += 3
        
        return min(score, 100)  # Cap at 100
    
    def get_seo_analysis(self):
        """Get detailed SEO analysis"""
        analysis = {
            'score': self.seo_score,
            'issues': [],
            'recommendations': [],
            'good_practices': []
        }
        
        # Title analysis
        title_length = len(self.get_seo_title())
        if title_length < 30:
            analysis['issues'].append('SEO title is too short (less than 30 characters)')
            analysis['recommendations'].append('Consider expanding your title to 30-60 characters')
        elif title_length > 60:
            analysis['issues'].append('SEO title is too long (more than 60 characters)')
            analysis['recommendations'].append('Shorten your title to under 60 characters')
        else:
            analysis['good_practices'].append('SEO title length is optimal')
        
        # Meta description analysis
        meta_desc = self.get_meta_description()
        if not meta_desc:
            analysis['issues'].append('Meta description is missing')
            analysis['recommendations'].append('Add a compelling meta description (120-160 characters)')
        elif len(meta_desc) < 120:
            analysis['issues'].append('Meta description is too short')
            analysis['recommendations'].append('Expand meta description to 120-160 characters')
        elif len(meta_desc) > 160:
            analysis['issues'].append('Meta description is too long')
            analysis['recommendations'].append('Shorten meta description to under 160 characters')
        else:
            analysis['good_practices'].append('Meta description length is optimal')
        
        # Focus keyword analysis
        if not self.focus_keyword:
            analysis['issues'].append('No focus keyword set')
            analysis['recommendations'].append('Set a focus keyword to optimize this post')
        else:
            # Check keyword in title
            if self.focus_keyword.lower() not in self.get_seo_title().lower():
                analysis['issues'].append('Focus keyword not found in title')
                analysis['recommendations'].append('Include your focus keyword in the title')
            else:
                analysis['good_practices'].append('Focus keyword found in title')
            
            # Check keyword density
            content_text = re.sub(r'<[^>]*>', '', self.content).lower()
            keyword_count = content_text.count(self.focus_keyword.lower())
            content_words = len(content_text.split())
            if content_words > 0:
                keyword_density = (keyword_count / content_words) * 100
                if keyword_density < 0.5:
                    analysis['issues'].append('Focus keyword density is too low')
                    analysis['recommendations'].append('Use your focus keyword more frequently (aim for 0.5-2.5% density)')
                elif keyword_density > 2.5:
                    analysis['issues'].append('Focus keyword density is too high (keyword stuffing)')
                    analysis['recommendations'].append('Reduce focus keyword usage to avoid keyword stuffing')
                else:
                    analysis['good_practices'].append('Focus keyword density is optimal')
        
        # Content length analysis
        content_words = len(re.sub(r'<[^>]*>', '', self.content).split())
        if content_words < 300:
            analysis['issues'].append('Content is too short for good SEO')
            analysis['recommendations'].append('Aim for at least 300 words of quality content')
        else:
            analysis['good_practices'].append('Content length is good for SEO')
        
        # Image analysis
        if not self.featured_image and not self.og_image:
            analysis['issues'].append('No featured image set')
            analysis['recommendations'].append('Add a featured image to improve social sharing')
        else:
            analysis['good_practices'].append('Featured image is set')
        
        return analysis
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', blank=True, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']  # Changed to chronological order for threading
    
    def __str__(self):
        return f'Comment by {self.name} on {self.post.title}'
    
    def get_replies(self):
        """Get approved replies to this comment"""
        return self.replies.filter(is_approved=True).order_by('created_at')
    
    def is_parent(self):
        """Check if this is a parent comment (not a reply)"""
        return self.parent is None
    
    def get_thread_level(self):
        """Get the nesting level of this comment"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email
