// SEO Admin JavaScript - Real-time SEO analysis and preview

(function($) {
    'use strict';

    class SEOAnalyzer {
        constructor() {
            this.initEventListeners();
            this.updatePreviews();
        }

        initEventListeners() {
            // Listen for changes in SEO-related fields
            $('input[name="title"], input[name="seo_title"], textarea[name="meta_description"], input[name="focus_keyword"], textarea[name="content"]').on('input', () => {
                this.updatePreviews();
                this.analyzeContent();
            });

            // Tab switching
            $('.seo-tab-btn').on('click', (e) => {
                this.switchTab($(e.target).data('tab'));
            });

            // Initialize content analysis
            this.analyzeContent();
        }

        switchTab(tabName) {
            $('.seo-tab-btn').removeClass('active');
            $(`.seo-tab-btn[data-tab="${tabName}"]`).addClass('active');
            
            $('.seo-tab-content').removeClass('active');
            $(`#${tabName}-preview`).addClass('active');
        }

        updatePreviews() {
            this.updateGooglePreview();
            this.updateFacebookPreview();
            this.updateTwitterPreview();
        }

        updateGooglePreview() {
            const title = this.getSEOTitle();
            const description = this.getMetaDescription();
            const url = this.generateURL();

            $('#google-title').text(title);
            $('#google-description').text(description);
            $('#google-url').text(url);
        }

        updateFacebookPreview() {
            const title = this.getOGTitle();
            const description = this.getOGDescription();

            $('#facebook-title').text(title);
            $('#facebook-description').text(description);
            
            // Update image if available
            const featuredImage = $('input[name="featured_image"]').val();
            if (featuredImage) {
                $('#facebook-image').html(`<img src="${featuredImage}" alt="Featured image" style="width: 100%; height: 100%; object-fit: cover;">`);
            }
        }

        updateTwitterPreview() {
            const title = this.getTwitterTitle();
            const description = this.getTwitterDescription();

            $('#twitter-title').text(title);
            $('#twitter-description').text(description);
            
            // Update image if available
            const featuredImage = $('input[name="featured_image"]').val();
            if (featuredImage) {
                $('#twitter-image').html(`<img src="${featuredImage}" alt="Featured image" style="width: 100%; height: 100%; object-fit: cover;">`);
            }
        }

        analyzeContent() {
            const analysis = this.performSEOAnalysis();
            this.updateSEOScore(analysis.score);
            this.updateSEOChecks(analysis.checks);
            this.updateKeywordDensity(analysis.keyword);
            this.updateReadability(analysis.readability);
        }

        performSEOAnalysis() {
            const title = this.getSEOTitle();
            const description = this.getMetaDescription();
            const content = this.getContent();
            const focusKeyword = this.getFocusKeyword();

            let score = 0;
            let checks = [];

            // Title analysis
            if (title.length >= 30 && title.length <= 60) {
                score += 20;
                checks.push({type: 'good', text: 'SEO title length is optimal'});
            } else if (title.length < 30) {
                checks.push({type: 'warning', text: 'SEO title is too short'});
            } else {
                checks.push({type: 'error', text: 'SEO title is too long'});
            }

            // Description analysis
            if (description.length >= 120 && description.length <= 160) {
                score += 20;
                checks.push({type: 'good', text: 'Meta description length is optimal'});
            } else if (description.length === 0) {
                checks.push({type: 'error', text: 'Meta description is missing'});
            } else if (description.length < 120) {
                checks.push({type: 'warning', text: 'Meta description is too short'});
            } else {
                checks.push({type: 'error', text: 'Meta description is too long'});
            }

            // Focus keyword analysis
            if (focusKeyword) {
                if (title.toLowerCase().includes(focusKeyword.toLowerCase())) {
                    score += 15;
                    checks.push({type: 'good', text: 'Focus keyword found in title'});
                } else {
                    checks.push({type: 'warning', text: 'Focus keyword not found in title'});
                }

                const keywordAnalysis = this.analyzeKeywordDensity(content, focusKeyword);
                if (keywordAnalysis.density >= 0.5 && keywordAnalysis.density <= 2.5) {
                    score += 15;
                    checks.push({type: 'good', text: 'Keyword density is optimal'});
                } else if (keywordAnalysis.density < 0.5) {
                    checks.push({type: 'warning', text: 'Keyword density is too low'});
                } else {
                    checks.push({type: 'error', text: 'Keyword density is too high (keyword stuffing)'});
                }
            } else {
                checks.push({type: 'warning', text: 'No focus keyword set'});
            }

            // Content length analysis
            const wordCount = this.getWordCount(content);
            if (wordCount >= 300) {
                score += 10;
                checks.push({type: 'good', text: 'Content length is good for SEO'});
            } else {
                checks.push({type: 'warning', text: 'Content is too short for optimal SEO'});
            }

            // Image analysis
            const featuredImage = $('input[name="featured_image"]').val();
            if (featuredImage) {
                score += 10;
                checks.push({type: 'good', text: 'Featured image is set'});
            } else {
                checks.push({type: 'warning', text: 'No featured image set'});
            }

            return {
                score: Math.min(score, 100),
                checks: checks,
                keyword: this.analyzeKeywordDensity(content, focusKeyword),
                readability: this.analyzeReadability(content)
            };
        }

        analyzeKeywordDensity(content, keyword) {
            if (!keyword || !content) {
                return {count: 0, density: 0, wordCount: 0};
            }

            const text = this.stripHTML(content).toLowerCase();
            const words = text.split(/\s+/).filter(word => word.length > 0);
            const keywordCount = text.split(keyword.toLowerCase()).length - 1;
            const density = words.length > 0 ? (keywordCount / words.length) * 100 : 0;

            return {
                count: keywordCount,
                density: density,
                wordCount: words.length
            };
        }

        analyzeReadability(content) {
            const text = this.stripHTML(content);
            const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
            const words = text.split(/\s+/).filter(word => word.length > 0);
            
            const avgWordsPerSentence = sentences.length > 0 ? words.length / sentences.length : 0;
            const complexWords = words.filter(word => word.length > 6).length;
            const complexWordPercentage = words.length > 0 ? (complexWords / words.length) * 100 : 0;

            // Simple Flesch Reading Ease approximation
            const fleschScore = 206.835 - (1.015 * avgWordsPerSentence) - (84.6 * (complexWordPercentage / 100));
            
            let level = 'Unknown';
            if (fleschScore >= 90) level = 'Very Easy';
            else if (fleschScore >= 80) level = 'Easy';
            else if (fleschScore >= 70) level = 'Fairly Easy';
            else if (fleschScore >= 60) level = 'Standard';
            else if (fleschScore >= 50) level = 'Fairly Difficult';
            else if (fleschScore >= 30) level = 'Difficult';
            else level = 'Very Difficult';

            return {
                fleschScore: Math.max(0, Math.round(fleschScore)),
                level: level,
                avgWordsPerSentence: Math.round(avgWordsPerSentence * 10) / 10,
                complexWordPercentage: Math.round(complexWordPercentage * 10) / 10
            };
        }

        updateSEOScore(score) {
            $('#seo-score').text(score);
            
            // Update score circle color
            const scoreElement = $('.seo-score');
            scoreElement.removeClass('score-good score-average score-poor');
            
            if (score >= 80) {
                scoreElement.addClass('score-good');
            } else if (score >= 60) {
                scoreElement.addClass('score-average');
            } else {
                scoreElement.addClass('score-poor');
            }
        }

        updateSEOChecks(checks) {
            const checkList = $('#seo-check-list');
            checkList.empty();

            checks.forEach(check => {
                const icon = this.getCheckIcon(check.type);
                const checkElement = $(`
                    <div class="seo-check ${check.type}">
                        <i class="${icon}"></i>
                        <span>${check.text}</span>
                    </div>
                `);
                checkList.append(checkElement);
            });
        }

        updateKeywordDensity(keywordData) {
            $('#keyword-count').text(keywordData.count);
            $('#keyword-density').text(keywordData.density.toFixed(1) + '%');
            $('#word-count').text(keywordData.wordCount);

            // Update density bar
            const maxDensity = 3.0; // 3% max for visualization
            const barWidth = Math.min((keywordData.density / maxDensity) * 100, 100);
            $('#density-bar-fill').css('width', barWidth + '%');

            // Update status
            const statusElement = $('#density-status');
            if (keywordData.density >= 0.5 && keywordData.density <= 2.5) {
                statusElement.html('<i class="fas fa-check-circle" style="color: #28a745;"></i> <span>Keyword density is optimal</span>');
            } else if (keywordData.density < 0.5) {
                statusElement.html('<i class="fas fa-exclamation-triangle" style="color: #ffc107;"></i> <span>Keyword density is too low</span>');
            } else {
                statusElement.html('<i class="fas fa-times-circle" style="color: #dc3545;"></i> <span>Keyword density is too high</span>');
            }
        }

        updateReadability(readabilityData) {
            $('#flesch-score').text(readabilityData.fleschScore);
            $('#readability-level').text(readabilityData.level);
            $('#avg-words-sentence').text(readabilityData.avgWordsPerSentence);
            $('#complex-words').text(readabilityData.complexWordPercentage + '%');
        }

        getCheckIcon(type) {
            switch(type) {
                case 'good': return 'fas fa-check-circle';
                case 'warning': return 'fas fa-exclamation-triangle';
                case 'error': return 'fas fa-times-circle';
                default: return 'fas fa-clock';
            }
        }

        // Utility methods
        getSEOTitle() {
            return $('input[name="seo_title"]').val() || $('input[name="title"]').val() || 'Sample Blog Post Title';
        }

        getMetaDescription() {
            return $('textarea[name="meta_description"]').val() || $('textarea[name="excerpt"]').val() || 'This is a sample meta description for the blog post...';
        }

        getOGTitle() {
            return $('input[name="og_title"]').val() || this.getSEOTitle();
        }

        getOGDescription() {
            return $('textarea[name="og_description"]').val() || this.getMetaDescription();
        }

        getTwitterTitle() {
            return $('input[name="twitter_title"]').val() || this.getSEOTitle();
        }

        getTwitterDescription() {
            return $('textarea[name="twitter_description"]').val() || this.getMetaDescription();
        }

        getContent() {
            // Try to get content from CKEditor or regular textarea
            const ckeditorInstance = window.CKEDITOR && CKEDITOR.instances.id_content;
            if (ckeditorInstance) {
                return ckeditorInstance.getData();
            }
            return $('textarea[name="content"]').val() || '';
        }

        getFocusKeyword() {
            return $('input[name="focus_keyword"]').val() || '';
        }

        generateURL() {
            const slug = $('input[name="slug"]').val() || 'sample-post';
            return `ai-bytes.tech › blog › ${slug}`;
        }

        stripHTML(html) {
            const div = document.createElement('div');
            div.innerHTML = html;
            return div.textContent || div.innerText || '';
        }

        getWordCount(content) {
            const text = this.stripHTML(content);
            return text.split(/\s+/).filter(word => word.length > 0).length;
        }
    }

    // Initialize SEO Analyzer when document is ready
    $(document).ready(function() {
        if ($('.seo-preview-container, .seo-analysis-container').length > 0) {
            new SEOAnalyzer();
        }
    });

})(django.jQuery);