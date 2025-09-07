from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Category, BlogPost
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Create sample blog posts'

    def handle(self, *args, **options):
        # Get or create a user for the blog posts
        user, created = User.objects.get_or_create(
            username='admin_blogger',
            defaults={
                'email': 'admin@aiblog.com',
                'first_name': 'AI',
                'last_name': 'Blogger',
                'is_staff': True
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created user: {user.username}')
            )

        # Sample blog posts data
        sample_posts = [
            {
                'title': 'Introduction to Artificial Intelligence',
                'category': 'AI',
                'excerpt': 'Discover the fundamentals of AI and how it\'s transforming our world.',
                'content': '''Artificial Intelligence (AI) has become one of the most transformative technologies of our time. From virtual assistants to autonomous vehicles, AI is reshaping industries and changing how we interact with technology.

## What is Artificial Intelligence?

AI refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. These systems can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation.

## Types of AI

1. **Narrow AI**: Designed to perform specific tasks
2. **General AI**: Hypothetical AI with human-like intelligence
3. **Superintelligence**: AI that surpasses human intelligence

## Applications of AI

- Healthcare: Disease diagnosis and drug discovery
- Finance: Fraud detection and algorithmic trading
- Transportation: Self-driving cars and traffic optimization
- Entertainment: Recommendation systems and content creation

The future of AI holds immense promise, but it also raises important questions about ethics, employment, and the role of humans in an AI-driven world.'''
            },
            {
                'title': 'Machine Learning Algorithms: A Comprehensive Guide',
                'category': 'ML',
                'excerpt': 'Explore the most important machine learning algorithms and when to use them.',
                'content': '''Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. Understanding different algorithms is crucial for successful ML implementations.

## Supervised Learning Algorithms

### Linear Regression
Perfect for predicting continuous values. Used in:
- Stock price prediction
- Sales forecasting
- Risk assessment

### Decision Trees
Easy to understand and interpret:
- Medical diagnosis
- Credit approval
- Feature selection

### Random Forest
Combines multiple decision trees:
- Reduces overfitting
- Handles missing values
- Provides feature importance

## Unsupervised Learning

### K-Means Clustering
Groups similar data points:
- Customer segmentation
- Image segmentation
- Anomaly detection

### Principal Component Analysis (PCA)
Dimensionality reduction technique:
- Data visualization
- Noise reduction
- Feature extraction

## Choosing the Right Algorithm

The choice depends on:
- Problem type (classification, regression, clustering)
- Data size and quality
- Interpretability requirements
- Performance needs

Understanding these algorithms is the foundation of successful machine learning projects.'''
            },
            {
                'title': 'Deep Learning: Neural Networks Explained',
                'category': 'DL',
                'excerpt': 'Dive deep into neural networks and understand how deep learning works.',
                'content': '''Deep Learning is a subset of machine learning that uses artificial neural networks with multiple layers to model and understand complex patterns in data.

## What Makes Deep Learning "Deep"?

The "deep" in deep learning refers to the number of layers in the neural network. Traditional neural networks had 2-3 layers, while deep networks can have dozens or even hundreds of layers.

## Key Components of Neural Networks

### Neurons (Nodes)
The basic processing units that:
- Receive inputs
- Apply weights and biases
- Use activation functions
- Produce outputs

### Layers
1. **Input Layer**: Receives raw data
2. **Hidden Layers**: Process and transform data
3. **Output Layer**: Produces final predictions

### Activation Functions
- **ReLU**: Most popular for hidden layers
- **Sigmoid**: Good for binary classification
- **Softmax**: Perfect for multi-class problems

## Popular Deep Learning Architectures

### Convolutional Neural Networks (CNNs)
Excellent for image processing:
- Image classification
- Object detection
- Medical imaging

### Recurrent Neural Networks (RNNs)
Great for sequential data:
- Natural language processing
- Time series analysis
- Speech recognition

### Transformers
State-of-the-art for language tasks:
- Machine translation
- Text summarization
- Question answering

Deep learning has revolutionized AI by enabling machines to automatically learn complex patterns from raw data.'''
            },
            {
                'title': 'Computer Vision: Seeing the World Through AI Eyes',
                'category': 'CV',
                'excerpt': 'Learn how computers can see and interpret visual information like humans.',
                'content': '''Computer Vision is a field of AI that enables computers to interpret and understand visual information from the world, much like human vision.

## How Computer Vision Works

### Image Processing Pipeline
1. **Image Acquisition**: Capturing digital images
2. **Preprocessing**: Noise reduction, normalization
3. **Feature Extraction**: Identifying important patterns
4. **Classification/Detection**: Making predictions

### Key Techniques

#### Edge Detection
Identifies boundaries in images:
- Sobel operators
- Canny edge detection
- Gradient-based methods

#### Object Detection
Locates and classifies objects:
- YOLO (You Only Look Once)
- R-CNN family
- SSD (Single Shot Detector)

#### Image Segmentation
Divides images into meaningful regions:
- Semantic segmentation
- Instance segmentation
- Panoptic segmentation

## Real-World Applications

### Autonomous Vehicles
- Lane detection
- Traffic sign recognition
- Pedestrian detection
- Obstacle avoidance

### Medical Imaging
- Cancer detection in X-rays
- MRI analysis
- Retinal disease diagnosis
- Surgical guidance

### Security and Surveillance
- Facial recognition
- Anomaly detection
- Crowd monitoring
- Access control

### Agriculture
- Crop monitoring
- Disease detection
- Yield prediction
- Automated harvesting

Computer vision continues to advance rapidly, with new applications emerging across industries.'''
            },
            {
                'title': 'Natural Language Processing: Teaching Machines to Understand Human Language',
                'category': 'NLP',
                'excerpt': 'Explore how AI systems can understand, interpret, and generate human language.',
                'content': '''Natural Language Processing (NLP) is the branch of AI that helps computers understand, interpret, and manipulate human language.

## Core NLP Tasks

### Text Processing
Fundamental preprocessing steps:
- **Tokenization**: Breaking text into words/tokens
- **Stemming**: Reducing words to root forms
- **Lemmatization**: Converting to dictionary forms
- **Stop word removal**: Filtering common words

### Part-of-Speech Tagging
Identifying grammatical roles:
- Nouns, verbs, adjectives
- Sentence structure analysis
- Grammar checking

### Named Entity Recognition (NER)
Identifying specific entities:
- Person names
- Organizations
- Locations
- Dates and times

## Advanced NLP Techniques

### Sentiment Analysis
Understanding emotions in text:
- Social media monitoring
- Customer feedback analysis
- Brand reputation management
- Political opinion tracking

### Machine Translation
Converting between languages:
- Google Translate
- Real-time conversation translation
- Document translation
- Multilingual content creation

### Text Summarization
Creating concise summaries:
- **Extractive**: Selecting important sentences
- **Abstractive**: Generating new summary text
- News summarization
- Document analysis

### Question Answering
Understanding and answering questions:
- Search engines
- Virtual assistants
- Customer support chatbots
- Educational systems

## Modern NLP with Transformers

### BERT (Bidirectional Encoder Representations)
- Understands context from both directions
- Pre-trained on large text corpora
- Fine-tuned for specific tasks

### GPT (Generative Pre-trained Transformer)
- Generates human-like text
- Powers chatbots and writing assistants
- Creates content and code

### Applications
- Content generation
- Code completion
- Creative writing
- Conversational AI

NLP continues to evolve rapidly, bringing us closer to truly natural human-computer interaction.'''
            },
            {
                'title': 'The Ethics of Artificial Intelligence',
                'category': 'AI',
                'excerpt': 'Examining the moral implications and responsibilities in AI development.',
                'content': '''As AI becomes more prevalent in our daily lives, it\'s crucial to consider the ethical implications of these powerful technologies.

## Key Ethical Concerns

### Bias and Fairness
AI systems can perpetuate or amplify human biases:
- **Training data bias**: Historical inequalities in data
- **Algorithmic bias**: Unfair treatment of certain groups
- **Representation bias**: Lack of diversity in datasets

### Privacy and Surveillance
AI enables unprecedented data collection:
- Facial recognition systems
- Behavioral tracking
- Personal data mining
- Predictive analytics

### Transparency and Explainability
"Black box" AI systems raise concerns:
- Decision-making processes unclear
- Difficulty in auditing AI systems
- Need for explainable AI (XAI)
- Accountability challenges

## Principles for Ethical AI

### Beneficence
AI should benefit humanity:
- Improve quality of life
- Solve global challenges
- Promote human welfare
- Reduce suffering

### Non-maleficence
"Do no harm" principle:
- Prevent misuse of AI
- Minimize negative consequences
- Consider long-term impacts
- Protect vulnerable populations

### Autonomy
Respect human agency:
- Preserve human decision-making
- Provide meaningful choices
- Avoid manipulation
- Maintain human oversight

### Justice
Ensure fair distribution of benefits:
- Equal access to AI benefits
- Prevent discrimination
- Address power imbalances
- Promote social justice

## Implementing Ethical AI

### Development Practices
- Diverse development teams
- Ethical review processes
- Bias testing and mitigation
- Regular audits and updates

### Governance and Regulation
- Industry standards
- Government policies
- International cooperation
- Professional codes of conduct

The future of AI depends on our ability to develop and deploy these technologies responsibly and ethically.'''
            }
        ]

        # Create sample posts
        for i, post_data in enumerate(sample_posts):
            category = Category.objects.get(name=post_data['category'])
            
            # Create posts with different dates
            created_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            blog_post, created = BlogPost.objects.get_or_create(
                title=post_data['title'],
                defaults={
                    'author': user,
                    'category': category,
                    'content': post_data['content'],
                    'excerpt': post_data['excerpt'],
                    'is_published': True,
                }
            )
            
            if created:
                # Update the created_at date
                blog_post.created_at = created_date
                blog_post.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Created blog post: "{blog_post.title}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Blog post "{blog_post.title}" already exists')
                )

        self.stdout.write(
            self.style.SUCCESS('Sample blog posts creation completed!')
        )
