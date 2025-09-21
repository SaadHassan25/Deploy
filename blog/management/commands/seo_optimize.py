"""
Django management command for SEO operations
Usage: python manage.py seo_optimize [options]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Avg
from blog.models import BlogPost
from blog.seo_utils import SEOAnalyzer, validate_seo_requirements
import csv
from io import StringIO


class Command(BaseCommand):
    help = 'Perform SEO optimization and analysis tasks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            choices=['analyze', 'update-scores', 'audit', 'export'],
            default='analyze',
            help='Action to perform'
        )
        
        parser.add_argument(
            '--post-id',
            type=int,
            help='Specific post ID to analyze'
        )
        
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Automatically fix common SEO issues where possible'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path for export'
        )
        
        parser.add_argument(
            '--min-score',
            type=int,
            default=0,
            help='Minimum SEO score to include in results'
        )
        
        parser.add_argument(
            '--max-score',
            type=int,
            default=100,
            help='Maximum SEO score to include in results'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'analyze':
            self.analyze_posts(options)
        elif action == 'update-scores':
            self.update_seo_scores(options)
        elif action == 'audit':
            self.perform_audit(options)
        elif action == 'export':
            self.export_seo_data(options)
    
    def analyze_posts(self, options):
        """Analyze SEO for posts"""
        queryset = BlogPost.objects.filter(is_published=True)
        
        if options['post_id']:
            queryset = queryset.filter(id=options['post_id'])
        
        # Filter by score range
        queryset = queryset.filter(
            seo_score__gte=options['min_score'],
            seo_score__lte=options['max_score']
        )
        
        self.stdout.write(self.style.SUCCESS(f'Analyzing {queryset.count()} posts...\n'))
        
        total_score = 0
        issue_count = 0
        
        for post in queryset:
            analyzer = SEOAnalyzer(post)
            analysis = analyzer.get_comprehensive_analysis()
            seo_issues = post.get_seo_analysis()
            
            self.stdout.write(f'\n--- {post.title} ---')
            self.stdout.write(f'SEO Score: {post.seo_score}/100')
            self.stdout.write(f'Word Count: {analysis["basic"]["word_count"]}')
            self.stdout.write(f'Reading Time: {post.get_reading_time_display()}')
            
            if analysis["keyword_analysis"]["focus_keyword"]:
                self.stdout.write(f'Focus Keyword: {analysis["keyword_analysis"]["focus_keyword"]}')
                self.stdout.write(f'Keyword Density: {analysis["keyword_analysis"]["keyword_density"]}%')
            
            self.stdout.write(f'Readability: {analysis["readability"]["level"]} (Flesch: {analysis["readability"]["flesch_ease"]})')
            
            # Show issues
            if seo_issues['issues']:
                self.stdout.write(self.style.ERROR('\nIssues:'))
                for issue in seo_issues['issues']:
                    self.stdout.write(f'  - {issue}')
                    issue_count += 1
            
            # Show recommendations
            if seo_issues['recommendations']:
                self.stdout.write(self.style.WARNING('\nRecommendations:'))
                for rec in seo_issues['recommendations']:
                    self.stdout.write(f'  - {rec}')
            
            # Show good practices
            if seo_issues['good_practices']:
                self.stdout.write(self.style.SUCCESS('\nGood Practices:'))
                for practice in seo_issues['good_practices']:
                    self.stdout.write(f'  - {practice}')
            
            total_score += post.seo_score
            
            # Auto-fix issues if requested
            if options['fix_issues']:
                self.auto_fix_issues(post)
        
        # Summary
        avg_score = total_score / queryset.count() if queryset.count() > 0 else 0
        self.stdout.write(self.style.SUCCESS(f'\n=== SUMMARY ==='))
        self.stdout.write(f'Posts analyzed: {queryset.count()}')
        self.stdout.write(f'Average SEO score: {avg_score:.1f}/100')
        self.stdout.write(f'Total issues found: {issue_count}')
    
    def update_seo_scores(self, options):
        """Recalculate SEO scores for all posts"""
        queryset = BlogPost.objects.filter(is_published=True)
        
        if options['post_id']:
            queryset = queryset.filter(id=options['post_id'])
        
        self.stdout.write(f'Updating SEO scores for {queryset.count()} posts...')
        
        updated_count = 0
        for post in queryset:
            old_score = post.seo_score
            post.seo_score = post.calculate_seo_score()
            post.save(update_fields=['seo_score'])
            
            if old_score != post.seo_score:
                updated_count += 1
                self.stdout.write(f'{post.title}: {old_score} -> {post.seo_score}')
        
        self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} posts'))
    
    def perform_audit(self, options):
        """Perform comprehensive SEO audit"""
        self.stdout.write(self.style.SUCCESS('=== SEO AUDIT REPORT ===\n'))
        
        posts = BlogPost.objects.filter(is_published=True)
        total_posts = posts.count()
        
        # Basic metrics
        self.stdout.write('BASIC METRICS:')
        self.stdout.write(f'Total published posts: {total_posts}')
        
        if total_posts > 0:
            avg_score = posts.aggregate(avg=Avg('seo_score'))['avg'] or 0
            self.stdout.write(f'Average SEO score: {avg_score:.1f}/100')
            
            # Score distribution
            excellent = posts.filter(seo_score__gte=90).count()
            good = posts.filter(seo_score__gte=80, seo_score__lt=90).count()
            needs_work = posts.filter(seo_score__gte=60, seo_score__lt=80).count()
            poor = posts.filter(seo_score__lt=60).count()
            
            self.stdout.write(f'Score distribution:')
            self.stdout.write(f'  Excellent (90-100): {excellent} ({excellent/total_posts*100:.1f}%)')
            self.stdout.write(f'  Good (80-89): {good} ({good/total_posts*100:.1f}%)')
            self.stdout.write(f'  Needs work (60-79): {needs_work} ({needs_work/total_posts*100:.1f}%)')
            self.stdout.write(f'  Poor (<60): {poor} ({poor/total_posts*100:.1f}%)')
        
        # Common issues
        self.stdout.write('\nCOMMON ISSUES:')
        
        missing_meta = posts.filter(meta_description='').count()
        if missing_meta > 0:
            self.stdout.write(self.style.ERROR(f'Missing meta descriptions: {missing_meta}'))
        
        missing_keywords = posts.filter(focus_keyword='').count()
        if missing_keywords > 0:
            self.stdout.write(self.style.ERROR(f'Missing focus keywords: {missing_keywords}'))
        
        missing_images = posts.filter(featured_image='').count()
        if missing_images > 0:
            self.stdout.write(self.style.WARNING(f'Missing featured images: {missing_images}'))
        
        # Title length issues
        short_titles = posts.extra(where=["LENGTH(title) < 30"]).count()
        long_titles = posts.extra(where=["LENGTH(title) > 60"]).count()
        
        if short_titles > 0:
            self.stdout.write(self.style.WARNING(f'Titles too short (<30 chars): {short_titles}'))
        
        if long_titles > 0:
            self.stdout.write(self.style.WARNING(f'Titles too long (>60 chars): {long_titles}'))
        
        # Posts needing immediate attention
        critical_posts = posts.filter(seo_score__lt=50).order_by('seo_score')[:10]
        if critical_posts:
            self.stdout.write(self.style.ERROR('\nPOSTS NEEDING IMMEDIATE ATTENTION:'))
            for post in critical_posts:
                self.stdout.write(f'  - {post.title} (Score: {post.seo_score})')
    
    def export_seo_data(self, options):
        """Export SEO data to CSV"""
        output_file = options.get('output', 'seo_export.csv')
        
        posts = BlogPost.objects.filter(is_published=True).order_by('-seo_score')
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Title', 'URL', 'SEO Score', 'Focus Keyword', 'Meta Description Length',
            'Word Count', 'Reading Time', 'Featured Image', 'Created Date'
        ])
        
        # Data rows
        for post in posts:
            analyzer = SEOAnalyzer(post)
            
            writer.writerow([
                post.title,
                post.get_absolute_url(),
                post.seo_score,
                post.focus_keyword,
                len(post.get_meta_description()),
                analyzer.word_count,
                post.get_reading_time(),
                'Yes' if post.featured_image else 'No',
                post.created_at.strftime('%Y-%m-%d')
            ])
        
        # Write to file
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            f.write(output.getvalue())
        
        self.stdout.write(self.style.SUCCESS(f'SEO data exported to {output_file}'))
    
    def auto_fix_issues(self, post):
        """Automatically fix common SEO issues where possible"""
        fixed_issues = []
        
        # Generate meta description from excerpt if missing
        if not post.meta_description and post.excerpt:
            if len(post.excerpt) <= 160:
                post.meta_description = post.excerpt
                fixed_issues.append('Added meta description from excerpt')
            else:
                post.meta_description = post.excerpt[:157] + '...'
                fixed_issues.append('Added truncated meta description from excerpt')
        
        # Generate SEO title from title if missing
        if not post.seo_title:
            if len(post.title) <= 60:
                post.seo_title = post.title
                fixed_issues.append('Added SEO title from post title')
        
        # Save changes if any fixes were made
        if fixed_issues:
            post.save()
            self.stdout.write(self.style.SUCCESS(f'Auto-fixed: {", ".join(fixed_issues)}'))
        
        return fixed_issues