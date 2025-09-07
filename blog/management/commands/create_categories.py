from django.core.management.base import BaseCommand
from blog.models import Category

class Command(BaseCommand):
    help = 'Create initial blog categories'

    def handle(self, *args, **options):
        categories = [
            ('AI', 'Explore the fascinating world of Artificial Intelligence, from basic concepts to advanced applications.'),
            ('ML', 'Dive deep into Machine Learning algorithms, techniques, and real-world implementations.'),
            ('DL', 'Discover Deep Learning architectures, neural networks, and cutting-edge research.'),
            ('CV', 'Learn about Computer Vision technologies, image processing, and visual recognition systems.'),
            ('NLP', 'Understand Natural Language Processing, text analysis, and language understanding systems.'),
        ]
        
        for name, description in categories:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created category "{category}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category "{category}" already exists')
                )
