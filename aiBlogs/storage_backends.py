from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    Custom storage class for media files using DigitalOcean Spaces
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False


class StaticStorage(S3Boto3Storage):
    """
    Custom storage class for static files using DigitalOcean Spaces
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True  # Static files can be overwritten