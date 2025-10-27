"""
Import/Export resources for blog models
"""
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget, BooleanWidget
from .models import BlogPost, Category, Tag, Comment, Newsletter
from django.contrib.auth.models import User


class TagResource(resources.ModelResource):
    """Resource for Tag model import/export"""
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'description', 'seo_title', 'meta_description', 'created_at')
        export_order = ('id', 'name', 'slug', 'description', 'seo_title', 'meta_description', 'created_at')
        import_id_fields = ['slug']  # Use slug as unique identifier for imports
        skip_unchanged = True
        report_skipped = True


class CategoryResource(resources.ModelResource):
    """Resource for Category model import/export"""
    
    name_display = fields.Field(column_name='category_display', attribute='get_name_display', readonly=True)
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'name_display', 'description', 'seo_title', 'meta_description')
        export_order = ('id', 'name', 'name_display', 'description', 'seo_title', 'meta_description')
        import_id_fields = ['name']
        skip_unchanged = True
        report_skipped = True


class BlogPostResource(resources.ModelResource):
    """Resource for BlogPost model import/export - includes ALL fields"""
    
    # Custom fields with widgets for relationships
    author = fields.Field(
        column_name='author',
        attribute='author',
        widget=ForeignKeyWidget(User, 'username')
    )
    
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    
    tags = fields.Field(
        column_name='tags',
        attribute='tags',
        widget=ManyToManyWidget(Tag, field='name', separator=',')
    )
    
    # Boolean fields with proper widget
    is_published = fields.Field(
        column_name='is_published',
        attribute='is_published',
        widget=BooleanWidget()
    )
    
    noindex = fields.Field(
        column_name='noindex',
        attribute='noindex',
        widget=BooleanWidget()
    )
    
    nofollow = fields.Field(
        column_name='nofollow',
        attribute='nofollow',
        widget=BooleanWidget()
    )
    
    # Image fields - exported as file paths
    featured_image = fields.Field(
        column_name='featured_image',
        attribute='featured_image'
    )
    
    og_image = fields.Field(
        column_name='og_image',
        attribute='og_image'
    )
    
    # Computed fields (readonly)
    reading_time = fields.Field(column_name='reading_time', readonly=True)
    
    class Meta:
        model = BlogPost
        # Include ALL fields from the model
        fields = (
            'id', 'title', 'slug', 'author', 'category', 'tags', 'content', 'excerpt',
            'featured_image', 'created_at', 'updated_at', 'is_published',
            'seo_title', 'meta_description', 'focus_keyword', 'seo_score',
            'og_title', 'og_description', 'og_image',
            'twitter_title', 'twitter_description',
            'canonical_url', 'noindex', 'nofollow', 'reading_time'
        )
        export_order = (
            'id', 'title', 'slug', 'author', 'category', 'tags', 'excerpt', 'content',
            'featured_image', 'is_published', 'created_at', 'updated_at', 'reading_time',
            'seo_title', 'meta_description', 'focus_keyword', 'seo_score',
            'og_title', 'og_description', 'og_image',
            'twitter_title', 'twitter_description',
            'canonical_url', 'noindex', 'nofollow'
        )
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True
    
    def dehydrate_reading_time(self, post):
        """Get reading time for export"""
        return post.get_reading_time_display()
    
    def before_import_row(self, row, **kwargs):
        """Pre-process row data before import"""
        # Ensure slug is generated if not provided
        if not row.get('slug') and row.get('title'):
            from django.utils.text import slugify
            row['slug'] = slugify(row['title'])
    
    def after_save_instance(self, instance, row, using_transactions, dry_run, **kwargs):
        """Post-process after saving instance"""
        if not dry_run:
            # Recalculate SEO score after import
            instance.seo_score = instance.calculate_seo_score()
            instance.save()


class CommentResource(resources.ModelResource):
    """Resource for Comment model import/export"""
    
    post = fields.Field(
        column_name='post',
        attribute='post',
        widget=ForeignKeyWidget(BlogPost, 'slug')
    )
    
    parent = fields.Field(
        column_name='parent_id',
        attribute='parent',
        widget=ForeignKeyWidget(Comment, 'id')
    )
    
    is_approved = fields.Field(
        column_name='is_approved',
        attribute='is_approved',
        widget=BooleanWidget()
    )
    
    class Meta:
        model = Comment
        fields = ('id', 'post', 'parent', 'name', 'email', 'content', 'created_at', 'is_approved')
        export_order = ('id', 'post', 'parent_id', 'name', 'email', 'content', 'created_at', 'is_approved')
        import_id_fields = ['id']
        skip_unchanged = True
        report_skipped = True


class NewsletterResource(resources.ModelResource):
    """Resource for Newsletter model import/export"""
    
    is_active = fields.Field(
        column_name='is_active',
        attribute='is_active',
        widget=BooleanWidget()
    )
    
    class Meta:
        model = Newsletter
        fields = ('id', 'email', 'subscribed_at', 'is_active')
        export_order = ('id', 'email', 'subscribed_at', 'is_active')
        import_id_fields = ['email']
        skip_unchanged = True
        report_skipped = True
