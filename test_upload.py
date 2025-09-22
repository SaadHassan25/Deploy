"""
Simple test script to check if storage backend is working
Run this as: python test_upload.py
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiBlogs.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def main():
    print("Testing Digital Ocean Spaces Upload...")
    print(f"USE_SPACES: {getattr(settings, 'USE_SPACES', 'Not set')}")
    print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")
    print(f"Storage backend type: {type(default_storage)}")
    print()
    
    # Create test content
    test_content = ContentFile(b"This is a test file content for Digital Ocean Spaces", name="test.txt")
    
    try:
        # Try to save the file
        print("Attempting to save file...")
        filename = default_storage.save("uploads/test_file.txt", test_content)
        print(f"✅ File saved successfully: {filename}")
        
        # Generate URL
        url = default_storage.url(filename)
        print(f"✅ URL generated: {url}")
        
        # Check if file exists
        exists = default_storage.exists(filename)
        print(f"File exists check: {exists}")
        
        # # Clean up
        # if exists:
        #     default_storage.delete(filename)
        #     print("✅ Test file deleted")
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()