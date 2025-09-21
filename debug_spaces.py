"""
Debug script to check DigitalOcean Spaces configuration
Run this in Django shell: python manage.py shell

Then run:
exec(open('debug_spaces.py').read())
"""

import os
from django.conf import settings

print("=== DigitalOcean Spaces Debug Information ===")
print()

# Check environment variables
print("1. Environment Variables:")
spaces_vars = [
    'USE_SPACES',
    'SPACES_ACCESS_KEY', 
    'SPACES_SECRET_KEY',
    'SPACES_BUCKET_NAME',
    'SPACES_REGION'
]

for var in spaces_vars:
    value = os.environ.get(var, 'NOT SET')
    if 'KEY' in var and value != 'NOT SET':
        value = f"{value[:4]}...{value[-4:]}"  # Hide most of the key
    print(f"  {var}: {value}")

print()

# Check Django settings
print("2. Django Settings:")
if hasattr(settings, 'USE_SPACES'):
    print(f"  USE_SPACES: {settings.USE_SPACES}")
    
    if settings.USE_SPACES:
        aws_settings = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY', 
            'AWS_STORAGE_BUCKET_NAME',
            'AWS_S3_REGION_NAME',
            'AWS_S3_ENDPOINT_URL',
            'AWS_S3_CUSTOM_DOMAIN'
        ]
        
        for setting in aws_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                if 'KEY' in setting and value:
                    value = f"{value[:4]}...{value[-4:]}"  # Hide most of the key
                print(f"  {setting}: {value}")
            else:
                print(f"  {setting}: NOT SET")
    else:
        print("  USE_SPACES is False - using local storage")
else:
    print("  USE_SPACES setting not found!")

print()

# Test connection
if hasattr(settings, 'USE_SPACES') and settings.USE_SPACES:
    print("3. Testing Spaces Connection:")
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # Create client
        client = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        # Test connection
        response = client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            MaxKeys=1
        )
        print("  ✅ Connection successful!")
        print(f"  ✅ Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' is accessible")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"  ❌ Connection failed: {error_code}")
        print(f"  ❌ Error: {e}")
        
        if error_code == 'InvalidAccessKeyId':
            print("  🔧 Fix: Check your SPACES_ACCESS_KEY")
        elif error_code == 'SignatureDoesNotMatch':
            print("  🔧 Fix: Check your SPACES_SECRET_KEY")
        elif error_code == 'NoSuchBucket':
            print("  🔧 Fix: Check your SPACES_BUCKET_NAME")
            
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")

print()
print("=== End Debug Information ===")