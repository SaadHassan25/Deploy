"""
Image optimization utilities for better performance
"""

from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import io
import os


class ImageOptimizer:
    """Optimize images for web performance"""
    
    def __init__(self):
        self.quality_settings = {
            'high': 95,
            'medium': 85,
            'low': 75
        }
        
        self.size_limits = {
            'featured': (1200, 630),  # Optimal for social sharing
            'thumbnail': (400, 300),
            'small': (200, 150)
        }
    
    def optimize_image(self, image_file, size_type='featured', quality='medium'):
        """Optimize an image file for web use"""
        try:
            # Open the image
            image = Image.open(image_file)
            
            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Get target size
            target_size = self.size_limits.get(size_type, self.size_limits['featured'])
            
            # Resize image while maintaining aspect ratio
            image = ImageOps.fit(image, target_size, Image.Resampling.LANCZOS)
            
            # Optimize and save
            output = io.BytesIO()
            image.save(
                output,
                format='JPEG',
                quality=self.quality_settings.get(quality, 85),
                optimize=True,
                progressive=True
            )
            output.seek(0)
            
            return ContentFile(output.getvalue())
            
        except Exception as e:
            print(f"Error optimizing image: {e}")
            return image_file
    
    def create_webp_version(self, image_file):
        """Create a WebP version of the image for modern browsers"""
        try:
            image = Image.open(image_file)
            
            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Save as WebP
            output = io.BytesIO()
            image.save(
                output,
                format='WEBP',
                quality=85,
                optimize=True
            )
            output.seek(0)
            
            return ContentFile(output.getvalue())
            
        except Exception as e:
            print(f"Error creating WebP version: {e}")
            return None
    
    def generate_responsive_images(self, image_file, filename_base):
        """Generate multiple sizes for responsive images"""
        sizes = {
            'small': (400, 300),
            'medium': (800, 600),
            'large': (1200, 900),
            'xlarge': (1600, 1200)
        }
        
        generated_images = {}
        
        try:
            original_image = Image.open(image_file)
            
            for size_name, (width, height) in sizes.items():
                # Skip if original is smaller than target size
                if (original_image.width < width or original_image.height < height):
                    continue
                
                # Resize image
                resized = ImageOps.fit(original_image, (width, height), Image.Resampling.LANCZOS)
                
                # Save JPEG version
                jpeg_output = io.BytesIO()
                resized.save(
                    jpeg_output,
                    format='JPEG',
                    quality=85,
                    optimize=True,
                    progressive=True
                )
                jpeg_output.seek(0)
                
                jpeg_filename = f"{filename_base}_{size_name}.jpg"
                generated_images[f"{size_name}_jpeg"] = {
                    'file': ContentFile(jpeg_output.getvalue()),
                    'filename': jpeg_filename
                }
                
                # Save WebP version
                webp_output = io.BytesIO()
                resized.save(
                    webp_output,
                    format='WEBP',
                    quality=85,
                    optimize=True
                )
                webp_output.seek(0)
                
                webp_filename = f"{filename_base}_{size_name}.webp"
                generated_images[f"{size_name}_webp"] = {
                    'file': ContentFile(webp_output.getvalue()),
                    'filename': webp_filename
                }
            
            return generated_images
            
        except Exception as e:
            print(f"Error generating responsive images: {e}")
            return {}


def lazy_load_images(content):
    """Add lazy loading attributes to images in HTML content"""
    import re
    
    # Pattern to match img tags
    img_pattern = re.compile(r'<img([^>]*?)>', re.IGNORECASE)
    
    def add_lazy_loading(match):
        img_attrs = match.group(1)
        
        # Skip if already has loading attribute
        if 'loading=' in img_attrs:
            return match.group(0)
        
        # Add lazy loading and decoding attributes
        img_attrs += ' loading="lazy" decoding="async"'
        
        return f'<img{img_attrs}>'
    
    return img_pattern.sub(add_lazy_loading, content)


def add_responsive_images(content):
    """Add responsive image attributes to HTML content"""
    import re
    
    # Pattern to match img tags with src
    img_pattern = re.compile(r'<img([^>]*?)src=["\']([^"\']*?)["\']([^>]*?)>', re.IGNORECASE)
    
    def add_srcset(match):
        before_src = match.group(1)
        src_url = match.group(2)
        after_src = match.group(3)
        
        # Skip if already has srcset
        if 'srcset=' in before_src or 'srcset=' in after_src:
            return match.group(0)
        
        # Generate srcset for different sizes
        base_url = src_url.rsplit('.', 1)[0] if '.' in src_url else src_url
        ext = src_url.rsplit('.', 1)[1] if '.' in src_url else 'jpg'
        
        srcset_urls = [
            f"{base_url}_small.{ext} 400w",
            f"{base_url}_medium.{ext} 800w",
            f"{base_url}_large.{ext} 1200w",
            f"{base_url}_xlarge.{ext} 1600w"
        ]
        
        srcset = ', '.join(srcset_urls)
        sizes = '(max-width: 400px) 400px, (max-width: 800px) 800px, (max-width: 1200px) 1200px, 1600px'
        
        return f'<img{before_src}src="{src_url}" srcset="{srcset}" sizes="{sizes}"{after_src}>'
    
    return img_pattern.sub(add_srcset, content)


def optimize_css_delivery(html_content):
    """Optimize CSS delivery by inlining critical CSS and deferring non-critical CSS"""
    import re
    
    # Pattern to match external CSS links
    css_pattern = re.compile(r'<link([^>]*?)rel=["\']stylesheet["\']([^>]*?)>', re.IGNORECASE)
    
    def defer_css(match):
        attrs = match.group(1) + match.group(2)
        
        # Skip if already has media="print"
        if 'media=' in attrs and 'print' in attrs:
            return match.group(0)
        
        # Add media="print" and onload handler to defer CSS
        return f'<link{match.group(1)}rel="preload" as="style" onload="this.onload=null;this.rel=\'stylesheet\'" media="print"{match.group(2)}>'
    
    return css_pattern.sub(defer_css, html_content)


def add_preload_hints(html_content, resources):
    """Add preload hints for critical resources"""
    head_pattern = re.compile(r'(<head[^>]*>)', re.IGNORECASE)
    
    preload_tags = []
    for resource in resources:
        resource_type = resource.get('type', 'script')
        href = resource.get('href', '')
        crossorigin = ' crossorigin' if resource.get('crossorigin') else ''
        
        preload_tags.append(f'<link rel="preload" as="{resource_type}" href="{href}"{crossorigin}>')
    
    if preload_tags:
        preload_html = '\n    ' + '\n    '.join(preload_tags)
        return head_pattern.sub(r'\1' + preload_html, html_content)
    
    return html_content