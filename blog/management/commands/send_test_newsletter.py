from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

class Command(BaseCommand):
    help = 'Send a test newsletter welcome email'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address to send test newsletter to'
        )

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            # Get current site URL for email links
            site_url = 'http://127.0.0.1:8000'  # In production, use your actual domain
            
            context = {
                'site_url': site_url,
            }
            
            # Render HTML and text versions
            html_content = render_to_string('email/newsletter_welcome.html', context)
            text_content = render_to_string('email/newsletter_welcome.txt', context)
            
            # Create the email
            subject = '🧠 Welcome to AI Blog Newsletter - Your Journey into AI Begins!'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [email]
            
            # Create EmailMultiAlternatives object for HTML email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email
            )
            
            # Attach HTML version
            msg.attach_alternative(html_content, "text/html")
            
            # Send the email
            msg.send()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Newsletter welcome email sent successfully to {email}!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to send email to {email}: {str(e)}')
            )
