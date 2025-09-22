from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import logging

logger = logging.getLogger(__name__)


class MediaStorage(S3Boto3Storage):
    """
    Custom storage class for media files using DigitalOcean Spaces
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = ''  # Store files in root of bucket (no subfolder)
    default_acl = 'public-read'
    file_overwrite = False
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"MediaStorage initialized with bucket: {self.bucket_name}")
        print(f"MediaStorage endpoint: {getattr(settings, 'AWS_S3_ENDPOINT_URL', 'Not set')}")
    
    def url(self, name):
        """Generate the URL for accessing the file"""
        # Clean up the name to handle spaces and special characters
        import urllib.parse
        if self.custom_domain:
            # Ensure the name doesn't start with a slash
            clean_name = name.lstrip('/')
            url = f"https://{self.custom_domain}/{urllib.parse.quote(clean_name)}"
            print(f"MediaStorage.url() generated: {url}")
            return url
        return super().url(name)
    
    def _save(self, name, content):
        """Override save to ensure proper file path handling"""
        # Clean the name to avoid path issues
        name = name.lstrip('/')
        print(f"MediaStorage._save() called with name: {name}")
        try:
            result = super()._save(name, content)
            print(f"MediaStorage._save() successful, returned: {result}")
            return result
        except Exception as e:
            print(f"MediaStorage._save() failed: {str(e)}")
            raise


class StaticStorage(S3Boto3Storage):
    """
    Custom storage class for static files using DigitalOcean Spaces
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True  # Static files can be overwritten
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN