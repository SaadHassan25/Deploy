from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from blog.models import BlogPost, Category, Comment, Newsletter, Tag


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='AI', description='Artificial Intelligence')

    def test_category_str(self):
        """Category __str__ returns full display name"""
        self.assertEqual(str(self.category), 'Artificial Intelligence')

    def test_get_seo_title_default(self):
        """SEO title falls back to category display name"""
        self.assertEqual(self.category.get_seo_title(), 'Artificial Intelligence - AI Blog')

    def test_get_seo_title_custom(self):
        """Custom SEO title is used when set"""
        self.category.seo_title = 'Custom AI Title'
        self.assertEqual(self.category.get_seo_title(), 'Custom AI Title')

    def test_get_meta_description_default(self):
        """Meta description falls back to auto-generated text"""
        desc = self.category.get_meta_description()
        self.assertIn('Artificial Intelligence', desc)

    def test_get_meta_description_custom(self):
        """Custom meta description is used when set"""
        self.category.meta_description = 'Custom description'
        self.assertEqual(self.category.get_meta_description(), 'Custom description')


class TagModelTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name='Python')

    def test_tag_str(self):
        self.assertEqual(str(self.tag), 'Python')

    def test_slug_auto_generated(self):
        """Slug is auto-generated from name"""
        self.assertEqual(self.tag.slug, 'python')

    def test_get_absolute_url(self):
        url = self.tag.get_absolute_url()
        self.assertEqual(url, '/tag/python/')

    def test_get_seo_title_default(self):
        self.assertEqual(self.tag.get_seo_title(), 'Python - AI Blog Posts')


class BlogPostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.category = Category.objects.create(name='AI', description='AI')
        self.post = BlogPost.objects.create(
            title='Test Blog Post',
            author=self.user,
            category=self.category,
            content='<p>This is test content for the blog post.</p>',
            excerpt='Test excerpt',
        )

    def test_slug_auto_generated(self):
        """Slug is auto-generated from title"""
        self.assertEqual(self.post.slug, 'test-blog-post')

    def test_str(self):
        self.assertEqual(str(self.post), 'Test Blog Post')

    def test_get_absolute_url(self):
        url = self.post.get_absolute_url()
        self.assertEqual(url, '/blog/test-blog-post/')

    def test_get_seo_title_default(self):
        """SEO title falls back to post title"""
        self.assertEqual(self.post.get_seo_title(), 'Test Blog Post')

    def test_get_seo_title_custom(self):
        self.post.seo_title = 'Custom SEO Title'
        self.assertEqual(self.post.get_seo_title(), 'Custom SEO Title')

    def test_get_meta_description_default(self):
        """Meta description falls back to excerpt"""
        self.assertEqual(self.post.get_meta_description(), 'Test excerpt')

    def test_seo_score_calculated_on_save(self):
        """SEO score is recalculated on save"""
        self.post.seo_title = 'A well-optimized SEO title for testing'
        self.post.meta_description = (
            'This is a well-crafted meta description that is long enough '
            'to be considered optimal by search engines and provides good context.'
        )
        self.post.focus_keyword = 'testing'
        self.post.save()
        self.assertGreater(self.post.seo_score, 0)

    def test_is_published_default(self):
        self.assertTrue(self.post.is_published)

    def test_ordering(self):
        """Posts are ordered by -created_at by default"""
        post2 = BlogPost.objects.create(
            title='Second Post',
            author=self.user,
            category=self.category,
            content='Content',
            excerpt='Excerpt',
        )
        posts = list(BlogPost.objects.all())
        self.assertEqual(posts[0], post2)
        self.assertEqual(posts[1], self.post)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.category = Category.objects.create(name='AI', description='AI')
        self.post = BlogPost.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            content='Content',
            excerpt='Excerpt',
        )
        self.comment = Comment.objects.create(
            post=self.post,
            name='Commenter',
            email='commenter@example.com',
            content='Great post!',
            is_approved=True,
        )

    def test_str(self):
        self.assertEqual(str(self.comment), 'Comment by Commenter on Test Post')

    def test_is_parent(self):
        self.assertTrue(self.comment.is_parent())

    def test_reply(self):
        reply = Comment.objects.create(
            post=self.post,
            parent=self.comment,
            name='Replier',
            content='Thanks!',
            is_approved=True,
        )
        self.assertFalse(reply.is_parent())
        self.assertEqual(reply.get_thread_level(), 1)
        self.assertIn(reply, self.comment.get_replies())

    def test_default_not_approved(self):
        comment = Comment.objects.create(
            post=self.post, name='New', content='New comment'
        )
        self.assertFalse(comment.is_approved)


class NewsletterModelTest(TestCase):
    def test_create_newsletter(self):
        newsletter = Newsletter.objects.create(email='test@example.com')
        self.assertEqual(str(newsletter), 'test@example.com')
        self.assertTrue(newsletter.is_active)

    def test_unique_email(self):
        Newsletter.objects.create(email='test@example.com')
        with self.assertRaises(Exception):
            Newsletter.objects.create(email='test@example.com')


class HomeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.category = Category.objects.create(name='AI', description='AI')

    def test_home_page_status(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_page_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'blog/home.html')

    def test_home_page_with_posts(self):
        BlogPost.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            content='Content',
            excerpt='Excerpt',
        )
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')


class BlogListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.category = Category.objects.create(name='AI', description='AI')
        for i in range(15):
            BlogPost.objects.create(
                title=f'Post {i}',
                author=self.user,
                category=self.category,
                content=f'Content {i}',
                excerpt=f'Excerpt {i}',
            )

    def test_blog_list_status(self):
        response = self.client.get('/blogs/')
        self.assertEqual(response.status_code, 200)

    def test_blog_list_pagination(self):
        response = self.client.get('/blogs/')
        self.assertTrue(response.context['page_obj'].has_next())

    def test_blog_list_search(self):
        response = self.client.get('/blogs/', {'q': 'Post 1'})
        self.assertEqual(response.status_code, 200)

    def test_blog_list_category_filter(self):
        response = self.client.get('/blogs/', {'category': 'AI'})
        self.assertEqual(response.status_code, 200)

    def test_blog_list_sort_oldest(self):
        response = self.client.get('/blogs/', {'sort': 'oldest'})
        self.assertEqual(response.status_code, 200)


class BlogDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.category = Category.objects.create(name='AI', description='AI')
        self.post = BlogPost.objects.create(
            title='Detail Test Post',
            author=self.user,
            category=self.category,
            content='Detail content',
            excerpt='Detail excerpt',
        )

    def test_blog_detail_status(self):
        response = self.client.get(f'/blog/{self.post.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_blog_detail_template(self):
        response = self.client.get(f'/blog/{self.post.slug}/')
        self.assertTemplateUsed(response, 'blog/blog_detail.html')

    def test_blog_detail_404(self):
        response = self.client.get('/blog/nonexistent-slug/')
        self.assertEqual(response.status_code, 404)

    def test_blog_detail_comment_post(self):
        response = self.client.post(
            f'/blog/{self.post.slug}/',
            {'name': 'Test', 'email': 'test@test.com', 'content': 'Nice!'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(post=self.post).exists())


class StaticPageViewTest(TestCase):
    def test_about_us(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)

    def test_terms_conditions(self):
        response = self.client.get('/terms/')
        self.assertEqual(response.status_code, 200)

    def test_privacy_policy(self):
        response = self.client.get('/privacy/')
        self.assertEqual(response.status_code, 200)


class NewsletterSignupViewTest(TestCase):
    def test_newsletter_signup_success(self):
        response = self.client.post(
            '/newsletter/signup/',
            {'email': 'subscriber@example.com'},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(Newsletter.objects.filter(email='subscriber@example.com').exists())

    def test_newsletter_signup_duplicate(self):
        Newsletter.objects.create(email='dup@example.com', is_active=True)
        response = self.client.post(
            '/newsletter/signup/',
            {'email': 'dup@example.com'},
        )
        data = response.json()
        self.assertFalse(data['success'])

    def test_newsletter_signup_invalid_email(self):
        response = self.client.post(
            '/newsletter/signup/',
            {'email': 'not-an-email'},
        )
        data = response.json()
        self.assertFalse(data['success'])

    def test_newsletter_signup_get_not_allowed(self):
        response = self.client.get('/newsletter/signup/')
        self.assertEqual(response.status_code, 405)


class CategoryPostsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.category = Category.objects.create(name='ML', description='ML')

    def test_category_posts_status(self):
        response = self.client.get('/category/ML/')
        self.assertEqual(response.status_code, 200)

    def test_category_posts_404(self):
        response = self.client.get('/category/INVALID/')
        self.assertEqual(response.status_code, 404)


class TagPostsViewTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name='Django', slug='django')

    def test_tag_posts_status(self):
        response = self.client.get('/tag/django/')
        self.assertEqual(response.status_code, 200)

    def test_tag_posts_404(self):
        response = self.client.get('/tag/nonexistent/')
        self.assertEqual(response.status_code, 404)

    def test_all_tags(self):
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
