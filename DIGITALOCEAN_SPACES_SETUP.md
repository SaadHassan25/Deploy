# DigitalOcean Spaces Setup Guide

## Step 1: Create DigitalOcean Spaces Bucket

1. Log in to your DigitalOcean account
2. Go to "Spaces" in the left sidebar
3. Click "Create Space"
4. Choose a region (e.g., NYC3, SFO3, etc.)
5. Choose a unique bucket name (e.g., "yourblog-media")
6. Set "File Listing" to "Public" (so your images are accessible)
7. Click "Create Space"

## Step 2: Generate API Keys

1. Go to "API" in the DigitalOcean dashboard
2. Click "Generate New Token" in the "Spaces access keys" section
3. Give it a name (e.g., "blog-spaces-access")
4. Save both the Access Key and Secret Key securely

## Step 3: Configure CORS Policy (Important!)

In your DigitalOcean Spaces dashboard:
1. Go to your created Space
2. Click on "Settings" tab
3. Scroll down to "CORS Configurations"
4. Add this configuration:

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

## Step 4: Set Environment Variables in DigitalOcean App Platform

In your DigitalOcean App Platform dashboard:

1. Go to your app
2. Click on "Settings" tab
3. Scroll down to "Environment Variables"
4. Add these variables:

```
USE_SPACES=true
SPACES_ACCESS_KEY=your_access_key_here
SPACES_SECRET_KEY=your_secret_key_here
SPACES_BUCKET_NAME=your_bucket_name_here
SPACES_REGION=nyc3  (or your chosen region)
```

## Step 5: Deploy Your App

After setting the environment variables, trigger a new deployment. Your images will now be stored in DigitalOcean Spaces and will persist across rebuilds.

## Testing

1. Upload an image through your Django admin
2. Check if it appears in your DigitalOcean Spaces bucket
3. Verify the image loads correctly on your website
4. Rebuild your app - the images should still be there!

## Troubleshooting

- If images don't upload: Check your API keys and CORS configuration
- If images don't display: Verify your bucket is set to "Public" file listing
- If you get permission errors: Make sure your API key has write permissions to Spaces

## Optional: Static Files in Spaces

If you also want to serve static files (CSS, JS) from Spaces, uncomment these lines in settings.py:

```python
STATICFILES_STORAGE = 'aiBlogs.storage_backends.StaticStorage'
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
```

Then run `python manage.py collectstatic` to upload your static files to Spaces.