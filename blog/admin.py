from django.contrib import admin
from .models import Category, BlogPost, Comment, Newsletter, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    readonly_fields = ['created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_name_display']
    search_fields = ['name']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'get_tags_display', 'get_reading_time_display', 'is_published', 'created_at']
    list_filter = ['category', 'tags', 'is_published', 'created_at', 'author']
    search_fields = ['title', 'content', 'tags__name']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['get_reading_time_display']
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
    )
    
    def get_reading_time_display(self, obj):
        return obj.get_reading_time_display()
    get_reading_time_display.short_description = 'Reading Time'
    
    def get_tags_display(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()[:3]])  # Show first 3 tags
    get_tags_display.short_description = 'Tags'

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
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriptions were activated.')
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriptions were deactivated.')
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"
