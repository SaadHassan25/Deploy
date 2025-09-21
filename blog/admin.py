from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Category, BlogPost, Comment, Newsletter, Tag
from .admin_widgets import SEOPreviewWidget, SEOAnalysisWidget, KeywordDensityWidget, ReadabilityWidget
from .seo_utils import SEOAnalyzer

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('SEO Settings', {
            'fields': ('seo_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_name_display']
    search_fields = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('SEO Settings', {
            'fields': ('seo_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )

class SEOInline(admin.StackedInline):
    """Inline for SEO-related fields"""
    model = BlogPost
    fields = []
    template = 'admin/seo_inline.html'
    extra = 0
    max_num = 0
    can_delete = False
    
    class Media:
        css = {
            'all': ('admin/css/seo_admin.css',)
        }
        js = ('admin/js/seo_admin.js',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'get_tags_display', 'get_seo_score_display', 'get_reading_time_display', 'is_published', 'created_at']
    list_filter = ['category', 'tags', 'is_published', 'created_at', 'author', 'seo_score']
    search_fields = ['title', 'content', 'tags__name', 'focus_keyword']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['get_reading_time_display', 'seo_score', 'get_seo_analysis_display']
    filter_horizontal = ['tags']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image', 'get_reading_time_display')
        }),
        ('Tags & Publishing', {
            'fields': ('tags', 'is_published')
        }),
        ('SEO Optimization', {
            'fields': (
                'focus_keyword', 
                'seo_title', 
                'meta_description',
                'seo_score',
                'get_seo_analysis_display'
            ),
            'classes': ('wide',)
        }),
        ('Open Graph & Social Media', {
            'fields': (
                'og_title',
                'og_description', 
                'og_image',
                'twitter_title',
                'twitter_description'
            ),
            'classes': ('collapse', 'wide')
        }),
        ('Advanced SEO', {
            'fields': (
                'canonical_url',
                'noindex',
                'nofollow'
            ),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/seo_admin.css',)
        }
        js = ('admin/js/seo_admin.js',)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('seo-analysis/<int:post_id>/', self.admin_site.admin_view(self.seo_analysis_view), name='blog_blogpost_seo_analysis'),
        ]
        return custom_urls + urls
    
    def seo_analysis_view(self, request, post_id):
        """AJAX view for real-time SEO analysis"""
        post = get_object_or_404(BlogPost, id=post_id)
        analyzer = SEOAnalyzer(post)
        analysis = analyzer.get_comprehensive_analysis()
        
        return JsonResponse({
            'success': True,
            'analysis': analysis,
            'seo_issues': post.get_seo_analysis()
        })
    
    def get_reading_time_display(self, obj):
        return obj.get_reading_time_display()
    get_reading_time_display.short_description = 'Reading Time'
    
    def get_tags_display(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()[:3]])  # Show first 3 tags
    get_tags_display.short_description = 'Tags'
    
    def get_seo_score_display(self, obj):
        if obj.seo_score >= 80:
            color = '#28a745'  # Green
            icon = 'fas fa-check-circle'
        elif obj.seo_score >= 60:
            color = '#ffc107'  # Yellow
            icon = 'fas fa-exclamation-triangle'
        else:
            color = '#dc3545'  # Red
            icon = 'fas fa-times-circle'
        
        return format_html(
            '<span style="color: {}"><i class="{}"></i> {}/100</span>',
            color, icon, obj.seo_score
        )
    get_seo_score_display.short_description = 'SEO Score'
    get_seo_score_display.admin_order_field = 'seo_score'
    
    def get_seo_analysis_display(self, obj):
        """Display SEO analysis in admin"""
        if not obj.id:  # New object
            return "Save the post first to see SEO analysis"
        
        analysis = obj.get_seo_analysis()
        
        html = f'<div class="seo-analysis-admin">'
        html += f'<div class="seo-score-badge seo-score-{self.get_score_class(obj.seo_score)}">'
        html += f'<strong>SEO Score: {obj.seo_score}/100</strong>'
        html += f'</div>'
        
        if analysis['good_practices']:
            html += '<div class="seo-section seo-good">'
            html += '<h4><i class="fas fa-check text-success"></i> Good Practices</h4>'
            html += '<ul>'
            for practice in analysis['good_practices']:
                html += f'<li>{practice}</li>'
            html += '</ul></div>'
        
        if analysis['issues']:
            html += '<div class="seo-section seo-issues">'
            html += '<h4><i class="fas fa-times text-danger"></i> Issues to Fix</h4>'
            html += '<ul>'
            for issue in analysis['issues']:
                html += f'<li>{issue}</li>'
            html += '</ul></div>'
        
        if analysis['recommendations']:
            html += '<div class="seo-section seo-recommendations">'
            html += '<h4><i class="fas fa-lightbulb text-warning"></i> Recommendations</h4>'
            html += '<ul>'
            for rec in analysis['recommendations']:
                html += f'<li>{rec}</li>'
            html += '</ul></div>'
        
        html += '</div>'
        
        return mark_safe(html)
    
    get_seo_analysis_display.short_description = 'SEO Analysis'
    
    def get_score_class(self, score):
        if score >= 80:
            return 'good'
        elif score >= 60:
            return 'average'
        else:
            return 'poor'
    
    def save_model(self, request, obj, form, change):
        """Override save to update SEO score"""
        super().save_model(request, obj, form, change)
        # The SEO score is calculated automatically in the model's save method

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'email', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at', 'post']
    search_fields = ['name', 'email', 'content', 'post__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    actions = ['approve_comments', 'disapprove_comments']
    
    fieldsets = (
        (None, {
            'fields': ('post', 'name', 'email')
        }),
        ('Comment', {
            'fields': ('content',)
        }),
        ('Moderation', {
            'fields': ('is_approved', 'created_at')
        }),
    )
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments were approved.')
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments were disapproved.')
    disapprove_comments.short_description = "Disapprove selected comments"

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    list_editable = ['is_active']
    readonly_fields = ['subscribed_at']
    ordering = ['-subscribed_at']
    actions = ['activate_subscriptions', 'deactivate_subscriptions', 'export_emails']
    
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriptions were activated.')
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriptions were deactivated.')
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"
    
    def export_emails(self, request, queryset):
        """Export email addresses for marketing campaigns"""
        emails = [newsletter.email for newsletter in queryset if newsletter.is_active]
        self.message_user(request, f'Exported {len(emails)} active email addresses.')
    export_emails.short_description = "Export active emails"
