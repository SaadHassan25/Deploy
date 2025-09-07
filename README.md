# AI Blog - Django Blog Website

A modern, responsive blog website built with Django focusing on AI, Machine Learning, Deep Learning, Computer Vision, and Natural Language Processing topics.

## Features

- 🏠 **Home Page**: Beautiful landing page with recent posts
- 📝 **Blog Listing**: Paginated blog posts (20 per page)
- 📖 **Blog Detail**: Individual blog post pages with full content
- 🏷️ **Categories**: Five predefined categories (AI, ML, DL, CV, NLP)
- ⏱️ **Reading Time**: Automatic calculation and display of estimated reading time
- ℹ️ **About Us**: Informative about page
- 📋 **Terms & Conditions**: Legal terms page
- 🔧 **Admin Panel**: Easy content management
- 📱 **Responsive Design**: Works on all devices
- 🎨 **Modern UI**: Bootstrap-based design with custom styling

## Categories

- **AI** - Artificial Intelligence
- **ML** - Machine Learning
- **DL** - Deep Learning
- **CV** - Computer Vision
- **NLP** - Natural Language Processing

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd aiBlogs
   ```

2. **Activate your virtual environment** (if using one):
   ```bash
   # Windows
   myenv\Scripts\activate
   
   # macOS/Linux
   source myenv/bin/activate
   ```

3. **Install required packages**:
   ```bash
   pip install Django Pillow
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create initial categories**:
   ```bash
   python manage.py create_categories
   ```

6. **Create sample blog posts** (optional):
   ```bash
   python manage.py create_sample_posts
   ```

7. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   Or use the custom command:
   ```bash
   python manage.py create_admin --username admin --email admin@example.com --password admin123
   ```

8. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

9. **Visit the website**:
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### Adding Blog Posts

1. Go to the admin panel: http://127.0.0.1:8000/admin/
2. Login with your superuser credentials
3. Click on "Blog posts" under the "BLOG" section
4. Click "Add blog post"
5. Fill in the required fields:
   - **Title**: The blog post title
   - **Slug**: URL-friendly version (auto-generated if left blank)
   - **Author**: Select the author
   - **Category**: Choose from AI, ML, DL, CV, NLP
   - **Excerpt**: Brief description (max 300 characters)
   - **Content**: Full blog post content
   - **Featured image**: Optional cover image
   - **Is published**: Check to make the post visible

### Managing Categories

Categories are pre-configured, but you can:
1. Go to admin panel → Categories
2. Edit descriptions for existing categories
3. Add new categories if needed (remember to update the choices in models.py)

### Customization

#### Adding New Categories
1. Edit `blog/models.py` - update `CATEGORY_CHOICES`
2. Create and run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Reading Time Feature

The blog automatically calculates and displays estimated reading time for each post:

- **Calculation**: Based on average reading speed of 200 words per minute
- **Display**: Shows in "X min read" format
- **Locations**: Visible on home page, blog list, blog detail, and category pages
- **Admin Panel**: Reading time is also displayed in the admin interface

The reading time is calculated by:
1. Removing HTML tags from content
2. Counting words in the cleaned text
3. Dividing by 200 (average words per minute)
4. Rounding up to the nearest minute (minimum 1 minute)

#### Customization
To change the reading speed calculation, edit the `get_reading_time()` method in `blog/models.py` and modify the divisor (currently 200).

#### Styling
- Main CSS file: `static/css/style.css`
- Uses Bootstrap 5 with custom overrides
- Fully responsive design

## File Structure

```
aiBlogs/
├── aiBlogs/                    # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── blog/                       # Main blog app
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── urls.py                # URL patterns
│   ├── admin.py               # Admin configuration
│   └── management/commands/   # Custom management commands
├── templates/blog/            # HTML templates
│   ├── base.html              # Base template
│   ├── home.html              # Home page
│   ├── blog_list.html         # Blog listing
│   ├── blog_detail.html       # Individual blog post
│   ├── about_us.html          # About page
│   ├── terms_conditions.html  # Terms page
│   └── category_posts.html    # Category filtering
├── static/css/                # Static files
│   └── style.css              # Custom CSS
└── media/                     # User uploads (images)
```

## Pages

1. **Home (/)**: Landing page with recent posts and feature showcase
2. **Blogs (/blogs/)**: Paginated list of all blog posts
3. **Blog Detail (/blog/slug/)**: Individual blog post pages
4. **About (/about/)**: About us page with team and mission info
5. **Terms (/terms/)**: Terms and conditions page
6. **Category (/category/category-name/)**: Posts filtered by category

## Management Commands

- `create_categories`: Creates the initial blog categories
- `create_sample_posts`: Creates sample blog posts for testing
- `create_admin`: Creates additional admin users

## Deployment Considerations

For production deployment:

1. **Update settings.py**:
   - Set `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Use a production database
   - Configure static file serving

2. **Security**:
   - Change the `SECRET_KEY`
   - Use environment variables for sensitive data
   - Enable HTTPS

3. **Static Files**:
   ```bash
   python manage.py collectstatic
   ```

## Support

The website includes:
- Responsive design for mobile/tablet/desktop
- SEO-friendly URLs
- Admin interface for easy content management
- Modern, accessible UI design
- Error handling and user feedback

## License

This project is open source and available under the MIT License.
