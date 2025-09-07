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
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:tag_posts', kwargs={'slug': self.slug})
    
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
    
    class Meta:
        verbose_name_plural = "Categories"
    
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
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
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
