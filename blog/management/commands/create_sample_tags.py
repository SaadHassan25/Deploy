from django.core.management.base import BaseCommand
from blog.models import Tag, BlogPost

class Command(BaseCommand):
    help = 'Create sample tags for testing'

    def handle(self, *args, **options):
        # Sample tags to create
        sample_tags = [
            {'name': 'Machine Learning', 'description': 'Posts about machine learning algorithms and techniques'},
            {'name': 'Deep Learning', 'description': 'Posts about neural networks and deep learning'},
            {'name': 'Computer Vision', 'description': 'Posts about image processing and computer vision'},
            {'name': 'Natural Language Processing', 'description': 'Posts about text processing and NLP'},
            {'name': 'Neural Networks', 'description': 'Posts about artificial neural networks'},
            {'name': 'TensorFlow', 'description': 'Posts about TensorFlow framework'},
            {'name': 'PyTorch', 'description': 'Posts about PyTorch framework'},
            {'name': 'Python', 'description': 'Posts about Python programming'},
            {'name': 'Data Science', 'description': 'Posts about data science and analytics'},
            {'name': 'AI Research', 'description': 'Posts about artificial intelligence research'},
            {'name': 'Algorithms', 'description': 'Posts about algorithms and data structures'},
            {'name': 'Automation', 'description': 'Posts about automation and AI applications'},
            {'name': 'Robotics', 'description': 'Posts about robotics and AI'},
            {'name': 'Ethics', 'description': 'Posts about AI ethics and responsible AI'},
            {'name': 'Tutorial', 'description': 'Step-by-step guides and tutorials'},
            {'name': 'Research', 'description': 'Latest research findings and papers'},
            {'name': 'Industry', 'description': 'Industry applications and case studies'},
            {'name': 'Beginner', 'description': 'Posts suitable for beginners'},
            {'name': 'Advanced', 'description': 'Advanced topics and techniques'},
            {'name': 'OpenAI', 'description': 'Posts about OpenAI and GPT models'},
        ]

        created_count = 0
        for tag_data in sample_tags:
            tag, created = Tag.objects.get_or_create(
                name=tag_data['name'],
                defaults={'description': tag_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created tag: {tag.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Tag already exists: {tag.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} new tags!')
        )
        
        # Add some tags to existing blog posts if they exist
        blog_posts = BlogPost.objects.all()
        if blog_posts.exists():
            self.stdout.write('\nAdding tags to existing blog posts...')
            
            # Get some common tags
            ml_tag = Tag.objects.filter(name='Machine Learning').first()
            dl_tag = Tag.objects.filter(name='Deep Learning').first()
            python_tag = Tag.objects.filter(name='Python').first()
            tutorial_tag = Tag.objects.filter(name='Tutorial').first()
            research_tag = Tag.objects.filter(name='Research').first()
            
            for i, post in enumerate(blog_posts[:10]):  # Limit to first 10 posts
                if i % 3 == 0 and ml_tag:
                    post.tags.add(ml_tag)
                if i % 4 == 0 and dl_tag:
                    post.tags.add(dl_tag)
                if i % 2 == 0 and python_tag:
                    post.tags.add(python_tag)
                if i % 5 == 0 and tutorial_tag:
                    post.tags.add(tutorial_tag)
                if i % 6 == 0 and research_tag:
                    post.tags.add(research_tag)
                
                self.stdout.write(f'Added tags to: {post.title}')
            
            self.stdout.write(
                self.style.SUCCESS('Tags added to existing blog posts!')
            )
