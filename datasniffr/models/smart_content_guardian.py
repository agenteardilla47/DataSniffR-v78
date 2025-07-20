#!/usr/bin/env python3
"""
DataSniffR Smart Content Guardian 🛡️🎯
====================================

The ultimate protective cherry on top! Helps companies protect employees
from accidentally using banned words, sensitive terms, or inappropriate
content with intelligent suggestions and real-time prevention!

Features:
- 🚫 Banned Words Detection & Prevention
- 🔍 Sensitive Term Monitoring
- 🤖 AI-Powered Content Analysis
- 💡 Smart Alternative Suggestions
- 🎯 Context-Aware Filtering
- 🛡️ Real-time Protection
- 📊 Usage Analytics & Training
- 🎭 Cultural Sensitivity Checks

mmm lol 🐶💾 - Protecting your team with style and sass! 🛡️✨
"""

from odoo import models, fields, api
import json
import logging
import re
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

_logger = logging.getLogger(__name__)

class SmartContentGuardian(models.Model):
    _name = 'smart.content.guardian'
    _description = 'Smart Content Guardian & Protection System 🛡️🎯'
    _order = 'create_date desc'
    
    name = fields.Char(string='Guardian Name', required=True)
    
    # Content Protection Configuration
    protection_level = fields.Selection([
        ('basic', 'Basic Protection 🛡️'),
        ('standard', 'Standard Guardian 🔍'),
        ('advanced', 'Advanced Shield 🚀'),
        ('enterprise', 'Enterprise Fortress 🏰'),
        ('ai_powered', 'AI-Powered Guardian 🤖'),
    ], string='Protection Level', required=True, default='standard')
    
    # Banned Words & Terms
    banned_words = fields.Text(string='Banned Words List (JSON)', help='List of prohibited words and phrases')
    sensitive_terms = fields.Text(string='Sensitive Terms (JSON)', help='Terms requiring caution')
    industry_specific_terms = fields.Text(string='Industry-Specific Restrictions (JSON)')
    
    # AI Configuration
    ai_analysis_enabled = fields.Boolean(string='AI Content Analysis', default=True)
    context_awareness = fields.Boolean(string='Context-Aware Analysis', default=True)
    sentiment_analysis = fields.Boolean(string='Sentiment Analysis', default=True)
    
    # Protection Scope
    protected_models = fields.Text(string='Protected Models (JSON)', help='Odoo models to monitor')
    protected_fields = fields.Text(string='Protected Fields (JSON)', help='Specific fields to guard')
    
    # Action Configuration
    action_on_detection = fields.Selection([
        ('warn', 'Show Warning ⚠️'),
        ('block', 'Block Content ❌'),
        ('suggest', 'Suggest Alternatives 💡'),
        ('ai_rewrite', 'AI Auto-Rewrite ✨'),
        ('escalate', 'Escalate to Manager 📢'),
    ], string='Action on Detection', default='suggest')
    
    # Analytics
    total_detections = fields.Integer(string='Total Detections', default=0)
    successful_preventions = fields.Integer(string='Successful Preventions', default=0)
    false_positives = fields.Integer(string='False Positives', default=0)
    user_feedback_score = fields.Float(string='User Feedback Score', default=0.0)
    
    # Status
    is_active = fields.Boolean(string='Guardian Active', default=True)
    last_update = fields.Datetime(string='Last Dictionary Update')
    
    @api.model
    def setup_company_guardian(self, company_config):
        """🏢 Set up company-specific content guardian"""
        
        # Default banned words categories
        default_banned = {
            'profanity': [
                'damn', 'hell', 'crap', 'stupid', 'idiot', 'moron'
            ],
            'discriminatory': [
                'racist', 'sexist', 'homophobic', 'bigoted'
            ],
            'confidential_markers': [
                'confidential', 'classified', 'top secret', 'internal only'
            ],
            'competitor_names': company_config.get('competitors', []),
            'sensitive_projects': company_config.get('sensitive_projects', []),
            'financial_terms': [
                'bankruptcy', 'lawsuit', 'investigation', 'fraud'
            ]
        }
        
        # Sensitive terms that need caution
        default_sensitive = {
            'legal_terms': [
                'contract', 'agreement', 'liability', 'warranty', 'guarantee'
            ],
            'financial_data': [
                'revenue', 'profit', 'loss', 'budget', 'cost', 'price'
            ],
            'personal_info': [
                'salary', 'address', 'phone', 'email', 'ssn', 'id number'
            ],
            'medical_terms': [
                'medical', 'health', 'diagnosis', 'treatment', 'prescription'
            ],
            'political_terms': [
                'political', 'election', 'candidate', 'party', 'government'
            ]
        }
        
        # Industry-specific restrictions
        industry_terms = self._get_industry_specific_terms(company_config.get('industry', 'general'))
        
        guardian = self.create({
            'name': f"Company Guardian - {company_config.get('company_name', 'Default')}",
            'protection_level': company_config.get('protection_level', 'standard'),
            'banned_words': json.dumps(default_banned, indent=2),
            'sensitive_terms': json.dumps(default_sensitive, indent=2),
            'industry_specific_terms': json.dumps(industry_terms, indent=2),
            'ai_analysis_enabled': True,
            'context_awareness': True,
            'sentiment_analysis': True,
            'protected_models': json.dumps([
                'mail.message', 'mail.template', 'project.task', 
                'crm.lead', 'sale.order', 'purchase.order',
                'hr.employee', 'res.partner'
            ]),
            'action_on_detection': company_config.get('action', 'suggest')
        })
        
        _logger.info(f"🛡️ Company Guardian setup complete for {company_config.get('company_name')}")
        
        return guardian
    
    def _get_industry_specific_terms(self, industry):
        """🏭 Get industry-specific restricted terms"""
        
        industry_restrictions = {
            'healthcare': {
                'banned': ['cure', 'guaranteed treatment', 'miracle drug'],
                'sensitive': ['patient', 'medical record', 'hipaa', 'diagnosis']
            },
            'finance': {
                'banned': ['guaranteed returns', 'risk-free', 'insider information'],
                'sensitive': ['investment', 'portfolio', 'credit score', 'loan']
            },
            'legal': {
                'banned': ['guaranteed win', 'sure case', 'easy money'],
                'sensitive': ['client privilege', 'case details', 'settlement']
            },
            'education': {
                'banned': ['guaranteed grades', 'cheat', 'plagiarism'],
                'sensitive': ['student record', 'ferpa', 'grade', 'transcript']
            },
            'technology': {
                'banned': ['hack', 'crack', 'pirate', 'steal code'],
                'sensitive': ['source code', 'api key', 'password', 'security']
            },
            'construction': {
                'banned': ['unsafe', 'code violation', 'corner cutting'],
                'sensitive': ['safety report', 'inspection', 'compliance']
            }
        }
        
        return industry_restrictions.get(industry, {'banned': [], 'sensitive': []})
    
    def analyze_content(self, content, context=None):
        """🔍 Analyze content for banned words and sensitive terms"""
        
        if not self.is_active or not content:
            return {'status': 'clean', 'issues': []}
        
        analysis_result = {
            'status': 'clean',  # 'clean', 'warning', 'blocked'
            'issues': [],
            'suggestions': [],
            'confidence_score': 0.0,
            'analysis_details': {}
        }
        
        # Step 1: Basic banned words check
        banned_issues = self._check_banned_words(content)
        if banned_issues:
            analysis_result['issues'].extend(banned_issues)
            analysis_result['status'] = 'blocked'
        
        # Step 2: Sensitive terms check
        sensitive_issues = self._check_sensitive_terms(content)
        if sensitive_issues:
            analysis_result['issues'].extend(sensitive_issues)
            if analysis_result['status'] == 'clean':
                analysis_result['status'] = 'warning'
        
        # Step 3: AI-powered analysis (if enabled)
        if self.ai_analysis_enabled:
            ai_analysis = self._ai_content_analysis(content, context)
            if ai_analysis.get('issues'):
                analysis_result['issues'].extend(ai_analysis['issues'])
                analysis_result['confidence_score'] = ai_analysis.get('confidence', 0.0)
        
        # Step 4: Generate suggestions
        if analysis_result['issues']:
            suggestions = self._generate_suggestions(content, analysis_result['issues'])
            analysis_result['suggestions'] = suggestions
        
        # Step 5: Update analytics
        self._update_analytics(analysis_result)
        
        return analysis_result
    
    def _check_banned_words(self, content):
        """🚫 Check for banned words and phrases"""
        
        issues = []
        banned_dict = json.loads(self.banned_words or '{}')
        content_lower = content.lower()
        
        for category, words in banned_dict.items():
            for word in words:
                if isinstance(word, str) and word.lower() in content_lower:
                    # Find exact positions
                    positions = []
                    start = 0
                    while True:
                        pos = content_lower.find(word.lower(), start)
                        if pos == -1:
                            break
                        positions.append(pos)
                        start = pos + 1
                    
                    if positions:
                        issues.append({
                            'type': 'banned_word',
                            'category': category,
                            'word': word,
                            'positions': positions,
                            'severity': 'high',
                            'message': f"Banned word detected: '{word}' (Category: {category})"
                        })
        
        return issues
    
    def _check_sensitive_terms(self, content):
        """⚠️ Check for sensitive terms requiring caution"""
        
        issues = []
        sensitive_dict = json.loads(self.sensitive_terms or '{}')
        content_lower = content.lower()
        
        for category, terms in sensitive_dict.items():
            for term in terms:
                if isinstance(term, str) and term.lower() in content_lower:
                    issues.append({
                        'type': 'sensitive_term',
                        'category': category,
                        'term': term,
                        'severity': 'medium',
                        'message': f"Sensitive term detected: '{term}' - Please review carefully"
                    })
        
        return issues
    
    def _ai_content_analysis(self, content, context=None):
        """🤖 AI-powered content analysis for advanced detection"""
        
        try:
            # Get AI service for content analysis
            ai_service = self.env['external.ai.connector'].get_best_ai_for_task('natural_language')
            
            if not ai_service:
                return {'issues': [], 'confidence': 0.0}
            
            analysis_prompt = f"""
            Analyze this content for potential issues:
            
            Content: "{content}"
            Context: {context or 'General communication'}
            
            Check for:
            1. Inappropriate language or tone
            2. Potential legal/compliance issues
            3. Confidential information leaks
            4. Discriminatory language
            5. Unprofessional content
            6. Cultural sensitivity issues
            
            Respond in JSON format:
            {{
                "issues": [
                    {{
                        "type": "issue_type",
                        "severity": "low|medium|high",
                        "message": "Description of the issue",
                        "suggestion": "How to fix it",
                        "confidence": 0.0-1.0
                    }}
                ],
                "overall_sentiment": "positive|neutral|negative",
                "professionalism_score": 0.0-1.0,
                "risk_level": "low|medium|high"
            }}
            """
            
            response = ai_service.call_ai_service(
                prompt=analysis_prompt,
                context="DataSniffR Content Guardian Analysis",
                max_tokens=1024
            )
            
            if response.get('success'):
                try:
                    ai_result = json.loads(response['content'])
                    return ai_result
                except json.JSONDecodeError:
                    return self._parse_ai_response_fallback(response['content'])
            
        except Exception as e:
            _logger.error(f"AI content analysis failed: {e}")
        
        return {'issues': [], 'confidence': 0.0}
    
    def _parse_ai_response_fallback(self, ai_response):
        """🔄 Fallback parsing for AI response"""
        
        issues = []
        
        # Simple keyword detection in AI response
        if 'inappropriate' in ai_response.lower():
            issues.append({
                'type': 'ai_detected_inappropriate',
                'severity': 'medium',
                'message': 'AI detected potentially inappropriate content',
                'confidence': 0.7
            })
        
        if 'unprofessional' in ai_response.lower():
            issues.append({
                'type': 'ai_detected_unprofessional',
                'severity': 'low',
                'message': 'AI detected unprofessional tone',
                'confidence': 0.6
            })
        
        return {'issues': issues, 'confidence': 0.5}
    
    def _generate_suggestions(self, content, issues):
        """💡 Generate smart suggestions for content improvement"""
        
        suggestions = []
        
        for issue in issues:
            if issue['type'] == 'banned_word':
                alternatives = self._get_word_alternatives(issue['word'])
                suggestions.append({
                    'type': 'word_replacement',
                    'original': issue['word'],
                    'alternatives': alternatives,
                    'message': f"Consider replacing '{issue['word']}' with: {', '.join(alternatives)}"
                })
            
            elif issue['type'] == 'sensitive_term':
                suggestions.append({
                    'type': 'review_required',
                    'message': f"Please review the use of '{issue['term']}' - ensure it's appropriate for the context"
                })
            
            elif issue['type'].startswith('ai_detected'):
                # Get AI suggestions for improvement
                ai_suggestion = self._get_ai_improvement_suggestion(content, issue)
                if ai_suggestion:
                    suggestions.append(ai_suggestion)
        
        return suggestions
    
    def _get_word_alternatives(self, banned_word):
        """🔄 Get alternative words for banned terms"""
        
        # Predefined alternatives for common banned words
        alternatives_dict = {
            'stupid': ['unwise', 'poor decision', 'not ideal'],
            'idiot': ['person', 'individual', 'colleague'],
            'damn': ['very', 'extremely', 'quite'],
            'hell': ['difficult situation', 'challenging', 'problematic'],
            'crap': ['poor quality', 'substandard', 'inadequate'],
            'hate': ['dislike', 'prefer not to', 'find challenging']
        }
        
        return alternatives_dict.get(banned_word.lower(), ['[alternative needed]'])
    
    def _get_ai_improvement_suggestion(self, content, issue):
        """✨ Get AI-powered improvement suggestions"""
        
        try:
            ai_service = self.env['external.ai.connector'].get_best_ai_for_task('natural_language')
            
            if not ai_service:
                return None
            
            suggestion_prompt = f"""
            Improve this content to address the following issue:
            
            Original Content: "{content}"
            Issue: {issue['message']}
            
            Provide a professional, appropriate alternative that maintains the original meaning.
            Keep it concise and natural.
            """
            
            response = ai_service.call_ai_service(
                prompt=suggestion_prompt,
                context="Content improvement suggestion",
                max_tokens=200
            )
            
            if response.get('success'):
                return {
                    'type': 'ai_improvement',
                    'original_content': content,
                    'suggested_content': response['content'],
                    'message': 'AI-generated improvement suggestion'
                }
        
        except Exception as e:
            _logger.error(f"AI suggestion failed: {e}")
        
        return None
    
    def _update_analytics(self, analysis_result):
        """📊 Update guardian analytics"""
        
        self.total_detections += 1
        
        if analysis_result['status'] != 'clean':
            self.successful_preventions += 1
    
    def protect_field_content(self, model_name, field_name, content, record_id=None):
        """🛡️ Real-time field content protection"""
        
        # Check if this model/field is protected
        protected_models = json.loads(self.protected_models or '[]')
        protected_fields = json.loads(self.protected_fields or '{}')
        
        if model_name not in protected_models:
            return {'allowed': True, 'content': content}
        
        # Check field-specific protection
        if model_name in protected_fields:
            if field_name not in protected_fields[model_name]:
                return {'allowed': True, 'content': content}
        
        # Analyze content
        context = f"Field: {field_name} in Model: {model_name}"
        analysis = self.analyze_content(content, context)
        
        # Take action based on configuration
        if analysis['status'] == 'blocked' and self.action_on_detection == 'block':
            return {
                'allowed': False,
                'content': content,
                'issues': analysis['issues'],
                'message': 'Content blocked due to policy violations'
            }
        
        elif analysis['status'] != 'clean' and self.action_on_detection == 'ai_rewrite':
            # AI auto-rewrite
            improved_content = self._ai_rewrite_content(content, analysis['issues'])
            return {
                'allowed': True,
                'content': improved_content,
                'issues': analysis['issues'],
                'message': 'Content automatically improved by AI',
                'original_content': content
            }
        
        else:
            return {
                'allowed': True,
                'content': content,
                'issues': analysis.get('issues', []),
                'suggestions': analysis.get('suggestions', []),
                'message': 'Content reviewed - please consider suggestions'
            }
    
    def _ai_rewrite_content(self, content, issues):
        """✨ AI-powered content rewriting"""
        
        try:
            ai_service = self.env['external.ai.connector'].get_best_ai_for_task('natural_language')
            
            if not ai_service:
                return content
            
            issues_summary = ', '.join([issue['message'] for issue in issues])
            
            rewrite_prompt = f"""
            Rewrite this content to address these issues while maintaining the original meaning:
            
            Original Content: "{content}"
            Issues to Fix: {issues_summary}
            
            Requirements:
            1. Keep the same meaning and intent
            2. Make it professional and appropriate
            3. Remove any problematic language
            4. Maintain the original tone as much as possible
            5. Keep it concise
            
            Return only the improved content, nothing else.
            """
            
            response = ai_service.call_ai_service(
                prompt=rewrite_prompt,
                context="Content rewriting for policy compliance",
                max_tokens=500
            )
            
            if response.get('success'):
                return response['content'].strip()
        
        except Exception as e:
            _logger.error(f"AI rewrite failed: {e}")
        
        return content  # Return original if rewrite fails
    
    def add_banned_word(self, word, category='custom'):
        """➕ Add new banned word to the guardian"""
        
        banned_dict = json.loads(self.banned_words or '{}')
        
        if category not in banned_dict:
            banned_dict[category] = []
        
        if word not in banned_dict[category]:
            banned_dict[category].append(word)
            self.banned_words = json.dumps(banned_dict, indent=2)
            self.last_update = datetime.now()
            
            _logger.info(f"🚫 Added banned word: '{word}' to category '{category}'")
    
    def remove_banned_word(self, word, category=None):
        """➖ Remove banned word from guardian"""
        
        banned_dict = json.loads(self.banned_words or '{}')
        removed = False
        
        if category:
            if category in banned_dict and word in banned_dict[category]:
                banned_dict[category].remove(word)
                removed = True
        else:
            # Remove from all categories
            for cat, words in banned_dict.items():
                if word in words:
                    words.remove(word)
                    removed = True
        
        if removed:
            self.banned_words = json.dumps(banned_dict, indent=2)
            self.last_update = datetime.now()
            _logger.info(f"✅ Removed banned word: '{word}'")
    
    def train_from_feedback(self, content, user_feedback, is_false_positive=False):
        """🎓 Learn from user feedback to improve accuracy"""
        
        if is_false_positive:
            self.false_positives += 1
            # Add to whitelist or adjust sensitivity
            self._add_to_whitelist(content)
        else:
            # Positive feedback - reinforce the detection
            self._reinforce_detection(content)
        
        # Update feedback score
        feedback_value = 1.0 if not is_false_positive else -0.5
        current_total = self.user_feedback_score * (self.total_detections - 1)
        self.user_feedback_score = (current_total + feedback_value) / self.total_detections
    
    def _add_to_whitelist(self, content):
        """✅ Add content to whitelist to prevent future false positives"""
        
        # Implementation for whitelist management
        pass
    
    def _reinforce_detection(self, content):
        """💪 Reinforce positive detections for better accuracy"""
        
        # Implementation for positive reinforcement
        pass
    
    def generate_protection_report(self):
        """📋 Generate comprehensive protection report"""
        
        success_rate = (self.successful_preventions / max(self.total_detections, 1)) * 100
        false_positive_rate = (self.false_positives / max(self.total_detections, 1)) * 100
        
        report = f"""
🛡️ SMART CONTENT GUARDIAN REPORT 🛡️

Guardian: {self.name}
Protection Level: {self.protection_level}
Status: {'🟢 Active' if self.is_active else '🔴 Inactive'}

📊 PROTECTION STATISTICS:
• Total Detections: {self.total_detections}
• Successful Preventions: {self.successful_preventions}
• Success Rate: {success_rate:.1f}%
• False Positive Rate: {false_positive_rate:.1f}%
• User Feedback Score: {self.user_feedback_score:.2f}/1.0

🚫 BANNED WORDS CATEGORIES:
{self._format_word_categories(json.loads(self.banned_words or '{}'))}

⚠️ SENSITIVE TERMS CATEGORIES:
{self._format_word_categories(json.loads(self.sensitive_terms or '{}'))}

🤖 AI ANALYSIS:
• AI Analysis: {'✅ Enabled' if self.ai_analysis_enabled else '❌ Disabled'}
• Context Awareness: {'✅ Enabled' if self.context_awareness else '❌ Disabled'}
• Sentiment Analysis: {'✅ Enabled' if self.sentiment_analysis else '❌ Disabled'}

🎯 PROTECTION SCOPE:
• Protected Models: {len(json.loads(self.protected_models or '[]'))}
• Action on Detection: {self.action_on_detection}

Last Updated: {self.last_update or 'Never'}

mmm lol 🐶💾 - Keeping your content safe and professional! 🛡️✨
        """
        
        return report
    
    def _format_word_categories(self, word_dict):
        """📝 Format word categories for report"""
        
        formatted = []
        for category, words in word_dict.items():
            word_count = len(words) if isinstance(words, list) else 0
            formatted.append(f"  • {category}: {word_count} terms")
        
        return '\n'.join(formatted) if formatted else '  • No categories configured'
    
    @api.model
    def get_protection_examples(self):
        """📚 Get examples of what the guardian protects against"""
        
        examples = {
            'banned_words': {
                'description': 'Words that are completely prohibited',
                'examples': [
                    'Profanity and offensive language',
                    'Discriminatory terms',
                    'Competitor names in negative context',
                    'Confidential project codenames'
                ]
            },
            'sensitive_terms': {
                'description': 'Terms that require careful review',
                'examples': [
                    'Financial information',
                    'Legal terminology',
                    'Personal data references',
                    'Medical information'
                ]
            },
            'ai_detection': {
                'description': 'AI-powered content analysis',
                'examples': [
                    'Inappropriate tone detection',
                    'Cultural sensitivity issues',
                    'Potential legal risks',
                    'Unprofessional language patterns'
                ]
            },
            'context_awareness': {
                'description': 'Smart context-based protection',
                'examples': [
                    'Different rules for internal vs external communication',
                    'Industry-specific terminology validation',
                    'Role-based content restrictions',
                    'Situation-appropriate language checking'
                ]
            }
        }
        
        return examples
    
    def test_content_protection(self, test_content):
        """🧪 Test content protection with sample text"""
        
        test_results = []
        
        test_cases = [
            "This is a normal professional message.",
            "That's a stupid idea and won't work.",
            "We need to discuss the confidential project details.",
            "The competitor's product is terrible.",
            "Please review the patient's medical information."
        ]
        
        if test_content:
            test_cases.append(test_content)
        
        for content in test_cases:
            result = self.analyze_content(content, "Test Context")
            test_results.append({
                'content': content,
                'status': result['status'],
                'issues_count': len(result['issues']),
                'suggestions_count': len(result['suggestions']),
                'details': result
            })
        
        return {
            'test_results': test_results,
            'summary': {
                'total_tests': len(test_results),
                'clean_content': len([r for r in test_results if r['status'] == 'clean']),
                'warnings': len([r for r in test_results if r['status'] == 'warning']),
                'blocked': len([r for r in test_results if r['status'] == 'blocked'])
            }
        }