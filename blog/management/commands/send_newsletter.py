from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from blog.models import Newsletter

class Command(BaseCommand):
    help = 'Send newsletter to all active subscribers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--subject',
            type=str,
            required=True,
            help='Subject line for the newsletter'
        )
        parser.add_argument(
            '--preview',
            action='store_true',
            help='Preview mode - show how many emails would be sent without actually sending'
        )

    def handle(self, *args, **options):
        subject = options['subject']
        preview = options['preview']
        
        # Get all active subscribers
        subscribers = Newsletter.objects.filter(is_active=True)
        
        if preview:
            self.stdout.write(
                self.style.WARNING(f'📧 PREVIEW MODE: Would send newsletter to {subscribers.count()} subscribers')
            )
            for subscriber in subscribers:
                self.stdout.write(f'  - {subscriber.email}')
            return
        
        if subscribers.count() == 0:
            self.stdout.write(
                self.style.WARNING('No active subscribers found.')
            )
            return
        
        sent_count = 0
        failed_count = 0
        
        for subscriber in subscribers:
            try:
                # You can create a newsletter template here
                # For now, we'll send a simple message
                text_content = f"""
Hello from AI Blog!

This is a newsletter update.

Thank you for being part of our community!

Best regards,
The AI Blog Team

---
Unsubscribe: http://127.0.0.1:8000/
"""
                
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[subscriber.email]
                )
                
                msg.send()
                sent_count += 1
                
                self.stdout.write(f'✅ Sent to {subscriber.email}')
                
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to send to {subscriber.email}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'📧 Newsletter sent! Success: {sent_count}, Failed: {failed_count}')
        )
