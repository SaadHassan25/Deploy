from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    Custom storage class for media files using DigitalOcean Spaces
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    endpoint_url = settings.AWS_S3_ENDPOINT_URL
    region_name = settings.AWS_S3_REGION_NAME
    default_acl = 'public-read'
    file_overwrite = False
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    location = ''  # Store files in root of bucket (no subfolder)
    
    def url(self, name):
        """Generate the URL for accessing the file"""
        # Clean up the name to handle spaces and special characters
        import urllib.parse
        if self.custom_domain:
            # Ensure the name doesn't start with a slash
            clean_name = name.lstrip('/')
            return f"https://{self.custom_domain}/{urllib.parse.quote(clean_name)}"
        return super().url(name)
    
    def _save(self, name, content):
        """Override save to ensure proper file path handling"""
        # Clean the name to avoid path issues
        name = name.lstrip('/')
        return super()._save(name, content)


class StaticStorage(S3Boto3Storage):
    """
    Custom storage class for static files using DigitalOcean Spaces
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    endpoint_url = settings.AWS_S3_ENDPOINT_URL
    region_name = settings.AWS_S3_REGION_NAME
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True  # Static files can be overwritten
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN