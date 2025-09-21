"""
Custom Django Admin Widget for SEO
Provides Yoast-like SEO preview and analysis
"""

from django import forms
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.utils.html import escape
import json


class SEOPreviewWidget(Widget):
    """Custom widget for SEO preview similar to Yoast"""
    
    template_name = 'admin/seo_preview_widget.html'
    
    class Media:
        css = {
            'all': ('admin/css/seo_preview.css',)
        }
        js = ('admin/js/seo_preview.js',)
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'seo-preview-widget'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def format_value(self, value):
        if value is None:
            return ''
        return value
    
    def render(self, name, value, attrs=None, renderer=None):
        context = {
            'widget': {
                'name': name,
                'value': self.format_value(value),
                'attrs': attrs,
            }
        }
        
        return mark_safe(f'''
        <div class="seo-preview-container">
            <div class="seo-tabs">
                <button type="button" class="seo-tab-btn active" data-tab="google">Google Preview</button>
                <button type="button" class="seo-tab-btn" data-tab="facebook">Facebook Preview</button>
                <button type="button" class="seo-tab-btn" data-tab="twitter">Twitter Preview</button>
            </div>
            
            <div class="seo-tab-content active" id="google-preview">
                <div class="google-preview">
                    <div class="google-url" id="google-url">ai-bytes.tech › blog › sample-post</div>
                    <div class="google-title" id="google-title">Sample Blog Post Title</div>
                    <div class="google-description" id="google-description">This is a sample meta description for the blog post...</div>
                </div>
            </div>
            
            <div class="seo-tab-content" id="facebook-preview">
                <div class="facebook-preview">
                    <div class="facebook-image" id="facebook-image">
                        <div class="facebook-image-placeholder">No image selected</div>
                    </div>
                    <div class="facebook-content">
                        <div class="facebook-title" id="facebook-title">Sample Blog Post Title</div>
                        <div class="facebook-description" id="facebook-description">This is a sample meta description...</div>
                        <div class="facebook-url" id="facebook-url">AI-BYTES.TECH</div>
                    </div>
                </div>
            </div>
            
            <div class="seo-tab-content" id="twitter-preview">
                <div class="twitter-preview">
                    <div class="twitter-image" id="twitter-image">
                        <div class="twitter-image-placeholder">No image selected</div>
                    </div>
                    <div class="twitter-content">
                        <div class="twitter-title" id="twitter-title">Sample Blog Post Title</div>
                        <div class="twitter-description" id="twitter-description">This is a sample meta description...</div>
                        <div class="twitter-url" id="twitter-url">ai-bytes.tech</div>
                    </div>
                </div>
            </div>
        </div>
        ''')


class SEOAnalysisWidget(Widget):
    """Widget for displaying SEO analysis and recommendations"""
    
    def render(self, name, value, attrs=None, renderer=None):
        return mark_safe(f'''
        <div class="seo-analysis-container">
            <div class="seo-score-circle">
                <div class="seo-score" id="seo-score">0</div>
                <div class="seo-score-label">SEO Score</div>
            </div>
            
            <div class="seo-checks">
                <h4>SEO Analysis</h4>
                <div class="seo-check-list" id="seo-check-list">
                    <div class="seo-check pending">
                        <i class="fas fa-clock"></i>
                        <span>Analysis will update automatically when you make changes</span>
                    </div>
                </div>
            </div>
            
            <div class="seo-recommendations">
                <h4>Recommendations</h4>
                <div class="seo-recommendation-list" id="seo-recommendation-list">
                    <div class="seo-recommendation">
                        <i class="fas fa-lightbulb"></i>
                        <span>Set a focus keyword to get personalized recommendations</span>
                    </div>
                </div>
            </div>
        </div>
        ''')


class KeywordDensityWidget(Widget):
    """Widget for displaying keyword density analysis"""
    
    def render(self, name, value, attrs=None, renderer=None):
        return mark_safe(f'''
        <div class="keyword-density-container">
            <div class="keyword-stats">
                <div class="keyword-stat">
                    <div class="keyword-stat-number" id="keyword-count">0</div>
                    <div class="keyword-stat-label">Keyword Uses</div>
                </div>
                <div class="keyword-stat">
                    <div class="keyword-stat-number" id="keyword-density">0%</div>
                    <div class="keyword-stat-label">Density</div>
                </div>
                <div class="keyword-stat">
                    <div class="keyword-stat-number" id="word-count">0</div>
                    <div class="keyword-stat-label">Total Words</div>
                </div>
            </div>
            
            <div class="keyword-density-bar">
                <div class="density-bar-fill" id="density-bar-fill" style="width: 0%"></div>
                <div class="density-markers">
                    <span class="density-marker" style="left: 20%;">0.5%</span>
                    <span class="density-marker" style="left: 50%;">1.25%</span>
                    <span class="density-marker" style="left: 80%;">2.5%</span>
                </div>
            </div>
            
            <div class="density-status" id="density-status">
                <i class="fas fa-info-circle"></i>
                <span>Optimal keyword density is between 0.5% and 2.5%</span>
            </div>
        </div>
        ''')


class ReadabilityWidget(Widget):
    """Widget for displaying readability analysis"""
    
    def render(self, name, value, attrs=None, renderer=None):
        return mark_safe(f'''
        <div class="readability-container">
            <div class="readability-score">
                <div class="flesch-score" id="flesch-score">0</div>
                <div class="readability-level" id="readability-level">Unknown</div>
            </div>
            
            <div class="readability-details">
                <div class="readability-detail">
                    <span class="readability-label">Flesch-Kincaid Grade:</span>
                    <span class="readability-value" id="flesch-kincaid">0</span>
                </div>
                <div class="readability-detail">
                    <span class="readability-label">Average Words per Sentence:</span>
                    <span class="readability-value" id="avg-words-sentence">0</span>
                </div>
                <div class="readability-detail">
                    <span class="readability-label">Complex Words:</span>
                    <span class="readability-value" id="complex-words">0%</span>
                </div>
            </div>
            
            <div class="readability-recommendations" id="readability-recommendations">
                <h5>Readability Tips:</h5>
                <ul>
                    <li>Use shorter sentences (aim for 15-20 words per sentence)</li>
                    <li>Use simpler words when possible</li>
                    <li>Break up long paragraphs</li>
                    <li>Use bullet points and headings</li>
                </ul>
            </div>
        </div>
        ''')