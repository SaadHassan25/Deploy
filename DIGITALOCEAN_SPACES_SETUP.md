# DigitalOcean Spaces Setup Guide - UPDATED

## Issue Fix: InvalidAccessKeyId Error

Based on your setup, here's the corrected configuration:

## Step 1: Verify Your DigitalOcean Spaces

From your URLs, I can see:
- **Bucket Name**: `django-blog-images`
- **Region**: `nyc3`
- **CDN URL**: `https://django-blog-images.nyc3.cdn.digitaloceanspaces.com`
- **Direct URL**: `https://django-blog-images.nyc3.digitaloceanspaces.com`

## Step 2: Environment Variables (CRITICAL)

Set these EXACT environment variables in your DigitalOcean App Platform:

```bash
USE_SPACES=true
SPACES_ACCESS_KEY=your_actual_access_key_here
SPACES_SECRET_KEY=your_actual_secret_key_here
SPACES_BUCKET_NAME=django-blog-images
SPACES_REGION=nyc3
```

⚠️ **IMPORTANT**: 
- Make sure there are NO quotes around the values
- Make sure there are NO extra spaces
- The keys must be EXACTLY as shown above

## Step 3: Test Your Configuration

1. Deploy your app with the environment variables
2. Run this debug script to check your configuration:

```bash
python manage.py shell
exec(open('debug_spaces.py').read())
```

This will show you exactly what's wrong with your configuration.

## Step 4: Common Fixes

### If you get "InvalidAccessKeyId: None":
- Your `SPACES_ACCESS_KEY` environment variable is not set correctly
- Check for typos in the variable name
- Make sure you're setting it in the right environment (production, not development)

### If you get "SignatureDoesNotMatch":
- Your `SPACES_SECRET_KEY` is incorrect
- Regenerate your Spaces keys and update them

### If you get "NoSuchBucket":
- Your `SPACES_BUCKET_NAME` is incorrect
- Make sure it matches exactly: `django-blog-images`

## Step 5: Verify CORS Configuration

In your DigitalOcean Spaces dashboard, make sure CORS is configured:

```xml
<CORSConfiguration>
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <AllowedMethod>POST</AllowedMethod>
        <AllowedMethod>PUT</AllowedMethod>
        <AllowedMethod>DELETE</AllowedMethod>
        <AllowedMethod>HEAD</AllowedMethod>
        <AllowedHeader>*</AllowedHeader>
    </CORSRule>
</CORSConfiguration>
```

## Step 6: Test Upload

After fixing the environment variables:
1. Redeploy your app
2. Try uploading an image through CKEditor
3. Check if it appears in your Spaces bucket
4. Verify the image loads correctly on your website

## Troubleshooting Commands

Run these in your Django shell to debug:

```python
# Check if USE_SPACES is working
from django.conf import settings
print(f"USE_SPACES: {settings.USE_SPACES}")

# Check if AWS settings are loaded
print(f"Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"Region: {settings.AWS_S3_REGION_NAME}")
print(f"Endpoint: {settings.AWS_S3_ENDPOINT_URL}")

# Test file upload
from django.core.files.storage import default_storage
print(f"Storage backend: {default_storage.__class__}")
```