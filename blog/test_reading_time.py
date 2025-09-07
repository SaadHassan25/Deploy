from django.test import TestCase
from django.contrib.auth.models import User
from blog.models import Category, BlogPost

class ReadingTimeTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='AI',
            description='Test category'
        )

    def test_short_content_reading_time(self):
        """Test reading time for short content (should be minimum 1 minute)"""
        short_content = "This is a very short blog post with just a few words."
        
        post = BlogPost.objects.create(
            title='Short Post',
            author=self.user,
            category=self.category,
            content=short_content,
            excerpt='Short excerpt'
        )
        
        # Short content should still show at least 1 minute
        self.assertEqual(post.get_reading_time(), 1)
        self.assertEqual(post.get_reading_time_display(), "1 min read")

    def test_medium_content_reading_time(self):
        """Test reading time for medium length content"""
        # Create content with approximately 400 words (should be 2 minutes at 200 wpm)
        medium_content = " ".join(["word"] * 400)
        
        post = BlogPost.objects.create(
            title='Medium Post',
            author=self.user,
            category=self.category,
            content=medium_content,
            excerpt='Medium excerpt'
        )
        
        # 400 words / 200 wpm = 2 minutes
        self.assertEqual(post.get_reading_time(), 2)
        self.assertEqual(post.get_reading_time_display(), "2 min read")

    def test_long_content_reading_time(self):
        """Test reading time for long content"""
        # Create content with approximately 1000 words (should be 5 minutes at 200 wpm)
        long_content = " ".join(["word"] * 1000)
        
        post = BlogPost.objects.create(
            title='Long Post',
            author=self.user,
            category=self.category,
            content=long_content,
            excerpt='Long excerpt'
        )
        
        # 1000 words / 200 wpm = 5 minutes
        self.assertEqual(post.get_reading_time(), 5)
        self.assertEqual(post.get_reading_time_display(), "5 min read")

    def test_html_content_reading_time(self):
        """Test that HTML tags are properly removed from reading time calculation"""
        html_content = """
        <h1>This is a heading</h1>
        <p>This is a paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>
        <ul>
            <li>List item 1</li>
            <li>List item 2</li>
        </ul>
        <p>Another paragraph with some more content to test the word counting.</p>
        """
        
        post = BlogPost.objects.create(
            title='HTML Post',
            author=self.user,
            category=self.category,
            content=html_content,
            excerpt='HTML excerpt'
        )
        
        # Should count only text words, not HTML tags
        reading_time = post.get_reading_time()
        self.assertGreaterEqual(reading_time, 1)
        self.assertIn("min read", post.get_reading_time_display())
