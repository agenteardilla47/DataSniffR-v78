#!/usr/bin/env python3
"""
DataSniffR External AI Connector 🤖🌐
====================================

Connect DataSniffR to external AI services like Gemini, OpenAI, Claude, etc.
for enhanced intelligence, natural language processing, and advanced analytics!

Features:
- 🧠 Multi-AI Provider Support (Gemini, OpenAI, Claude, Hugging Face)
- 🔄 Intelligent API Routing & Fallback
- 💬 Natural Language Data Analysis
- 🎯 Smart Error Classification & Solutions
- 📊 AI-Powered Insights & Recommendations
- 🎭 Dynamic Sass Generation
- 🔒 Secure API Key Management

mmm lol 🐶💾 - Bringing the power of external AI to DataSniffR! 🤖✨
"""

from odoo import models, fields, api
import requests
import json
import logging
from datetime import datetime
import base64
import hashlib
import time
from urllib.parse import urljoin

_logger = logging.getLogger(__name__)

class ExternalAIConnector(models.Model):
    _name = 'external.ai.connector'
    _description = 'External AI Service Connector 🤖🌐'
    _order = 'create_date desc'
    
    name = fields.Char(string='AI Service Name', required=True)
    
    # AI Service Configuration
    ai_provider = fields.Selection([
        ('gemini', 'Google Gemini 🧠'),
        ('openai', 'OpenAI GPT 🤖'),
        ('claude', 'Anthropic Claude 🎭'),
        ('huggingface', 'Hugging Face 🤗'),
        ('azure_openai', 'Azure OpenAI 🌐'),
        ('custom', 'Custom API 🔧'),
    ], string='AI Provider', required=True)
    
    # API Configuration
    api_endpoint = fields.Char(string='API Endpoint URL')
    api_key = fields.Char(string='API Key (Encrypted)', help='API key will be encrypted for security')
    api_version = fields.Char(string='API Version', default='v1')
    model_name = fields.Char(string='Model Name', help='e.g., gemini-pro, gpt-4, claude-3-sonnet')
    
    # Service Status
    is_active = fields.Boolean(string='Active', default=True)
    last_used = fields.Datetime(string='Last Used')
    total_requests = fields.Integer(string='Total Requests', default=0)
    successful_requests = fields.Integer(string='Successful Requests', default=0)
    failed_requests = fields.Integer(string='Failed Requests', default=0)
    
    # Performance Metrics
    avg_response_time = fields.Float(string='Average Response Time (seconds)', default=0.0)
    rate_limit_remaining = fields.Integer(string='Rate Limit Remaining', default=1000)
    monthly_usage = fields.Integer(string='Monthly Usage Count', default=0)
    
    # Service Capabilities
    supports_text = fields.Boolean(string='Supports Text Analysis', default=True)
    supports_vision = fields.Boolean(string='Supports Image Analysis', default=False)
    supports_code = fields.Boolean(string='Supports Code Analysis', default=False)
    supports_data = fields.Boolean(string='Supports Data Analysis', default=True)
    
    # Configuration JSON
    additional_config = fields.Text(string='Additional Configuration (JSON)')
    
    @api.model
    def setup_gemini_connector(self, api_key, model='gemini-pro'):
        """🧠 Set up Google Gemini AI connector"""
        
        return self.create({
            'name': f'Google Gemini ({model})',
            'ai_provider': 'gemini',
            'api_endpoint': 'https://generativelanguage.googleapis.com/v1beta',
            'api_key': self._encrypt_api_key(api_key),
            'model_name': model,
            'supports_text': True,
            'supports_vision': model == 'gemini-pro-vision',
            'supports_code': True,
            'supports_data': True,
            'additional_config': json.dumps({
                'temperature': 0.7,
                'max_tokens': 2048,
                'safety_settings': 'default'
            })
        })
    
    @api.model
    def setup_openai_connector(self, api_key, model='gpt-4'):
        """🤖 Set up OpenAI GPT connector"""
        
        return self.create({
            'name': f'OpenAI {model}',
            'ai_provider': 'openai',
            'api_endpoint': 'https://api.openai.com/v1',
            'api_key': self._encrypt_api_key(api_key),
            'model_name': model,
            'supports_text': True,
            'supports_vision': 'vision' in model,
            'supports_code': True,
            'supports_data': True,
            'additional_config': json.dumps({
                'temperature': 0.7,
                'max_tokens': 2048,
                'frequency_penalty': 0,
                'presence_penalty': 0
            })
        })
    
    @api.model
    def setup_claude_connector(self, api_key, model='claude-3-sonnet-20240229'):
        """🎭 Set up Anthropic Claude connector"""
        
        return self.create({
            'name': f'Anthropic Claude ({model})',
            'ai_provider': 'claude',
            'api_endpoint': 'https://api.anthropic.com/v1',
            'api_key': self._encrypt_api_key(api_key),
            'model_name': model,
            'supports_text': True,
            'supports_vision': 'vision' in model or 'claude-3' in model,
            'supports_code': True,
            'supports_data': True,
            'additional_config': json.dumps({
                'max_tokens': 2048,
                'temperature': 0.7
            })
        })
    
    def _encrypt_api_key(self, api_key):
        """🔒 Encrypt API key for secure storage"""
        if not api_key:
            return ''
        
        # Simple encryption (in production, use proper encryption)
        encoded = base64.b64encode(api_key.encode()).decode()
        return f"encrypted_{encoded}"
    
    def _decrypt_api_key(self):
        """🔓 Decrypt API key for usage"""
        if not self.api_key or not self.api_key.startswith('encrypted_'):
            return self.api_key
        
        try:
            encoded = self.api_key.replace('encrypted_', '')
            return base64.b64decode(encoded.encode()).decode()
        except Exception as e:
            _logger.error(f"Failed to decrypt API key: {e}")
            return ''
    
    def test_connection(self):
        """🔍 Test connection to AI service"""
        
        try:
            response = self.call_ai_service(
                prompt="Hello! This is a test connection. Please respond with 'Connection successful!'",
                max_tokens=50
            )
            
            if response.get('success'):
                return {
                    'success': True,
                    'message': f"✅ Connection to {self.name} successful!",
                    'response': response.get('content', '')
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ Connection to {self.name} failed!",
                    'error': response.get('error', 'Unknown error')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Connection test failed: {str(e)}",
                'error': str(e)
            }
    
    def call_ai_service(self, prompt, context=None, max_tokens=2048, temperature=0.7):
        """🤖 Make API call to external AI service"""
        
        if not self.is_active:
            return {'success': False, 'error': 'AI service is not active'}
        
        start_time = time.time()
        
        try:
            # Prepare request based on provider
            if self.ai_provider == 'gemini':
                response = self._call_gemini(prompt, context, max_tokens, temperature)
            elif self.ai_provider == 'openai':
                response = self._call_openai(prompt, context, max_tokens, temperature)
            elif self.ai_provider == 'claude':
                response = self._call_claude(prompt, context, max_tokens, temperature)
            elif self.ai_provider == 'huggingface':
                response = self._call_huggingface(prompt, context, max_tokens, temperature)
            else:
                return {'success': False, 'error': f'Unsupported AI provider: {self.ai_provider}'}
            
            # Update metrics
            response_time = time.time() - start_time
            self._update_metrics(response.get('success', False), response_time)
            
            return response
            
        except Exception as e:
            self._update_metrics(False, time.time() - start_time)
            _logger.error(f"AI service call failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _call_gemini(self, prompt, context=None, max_tokens=2048, temperature=0.7):
        """🧠 Call Google Gemini API"""
        
        api_key = self._decrypt_api_key()
        if not api_key:
            return {'success': False, 'error': 'No API key configured'}
        
        url = f"{self.api_endpoint}/models/{self.model_name}:generateContent"
        
        # Prepare request payload
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{context}\n\n{prompt}" if context else prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "candidateCount": 1
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Add API key to URL for Gemini
        url += f"?key={api_key}"
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'candidates' in data and len(data['candidates']) > 0:
                content = data['candidates'][0]['content']['parts'][0]['text']
                return {
                    'success': True,
                    'content': content,
                    'provider': 'gemini',
                    'model': self.model_name,
                    'usage': data.get('usageMetadata', {})
                }
            else:
                return {'success': False, 'error': 'No response from Gemini'}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Gemini API error: {str(e)}'}
    
    def _call_openai(self, prompt, context=None, max_tokens=2048, temperature=0.7):
        """🤖 Call OpenAI API"""
        
        api_key = self._decrypt_api_key()
        if not api_key:
            return {'success': False, 'error': 'No API key configured'}
        
        url = f"{self.api_endpoint}/chat/completions"
        
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                return {
                    'success': True,
                    'content': content,
                    'provider': 'openai',
                    'model': self.model_name,
                    'usage': data.get('usage', {})
                }
            else:
                return {'success': False, 'error': 'No response from OpenAI'}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'OpenAI API error: {str(e)}'}
    
    def _call_claude(self, prompt, context=None, max_tokens=2048, temperature=0.7):
        """🎭 Call Anthropic Claude API"""
        
        api_key = self._decrypt_api_key()
        if not api_key:
            return {'success': False, 'error': 'No API key configured'}
        
        url = f"{self.api_endpoint}/messages"
        
        messages = []
        if context:
            messages.append({"role": "user", "content": f"Context: {context}\n\nQuery: {prompt}"})
        else:
            messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'content' in data and len(data['content']) > 0:
                content = data['content'][0]['text']
                return {
                    'success': True,
                    'content': content,
                    'provider': 'claude',
                    'model': self.model_name,
                    'usage': data.get('usage', {})
                }
            else:
                return {'success': False, 'error': 'No response from Claude'}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Claude API error: {str(e)}'}
    
    def _call_huggingface(self, prompt, context=None, max_tokens=2048, temperature=0.7):
        """🤗 Call Hugging Face API"""
        
        api_key = self._decrypt_api_key()
        if not api_key:
            return {'success': False, 'error': 'No API key configured'}
        
        # Hugging Face Inference API
        url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        
        payload = {
            "inputs": f"{context}\n\n{prompt}" if context else prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False
            }
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                content = data[0].get('generated_text', '')
                return {
                    'success': True,
                    'content': content,
                    'provider': 'huggingface',
                    'model': self.model_name
                }
            else:
                return {'success': False, 'error': 'No response from Hugging Face'}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Hugging Face API error: {str(e)}'}
    
    def _update_metrics(self, success, response_time):
        """📊 Update service performance metrics"""
        
        self.total_requests += 1
        self.last_used = datetime.now()
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Update average response time
        if self.total_requests > 1:
            self.avg_response_time = ((self.avg_response_time * (self.total_requests - 1)) + response_time) / self.total_requests
        else:
            self.avg_response_time = response_time
    
    @api.model
    def get_best_ai_for_task(self, task_type='general'):
        """🎯 Get the best AI service for a specific task"""
        
        active_services = self.search([('is_active', '=', True)])
        
        if not active_services:
            return None
        
        # Task-specific preferences
        task_preferences = {
            'data_analysis': ['claude', 'gpt-4', 'gemini'],
            'code_generation': ['gpt-4', 'claude', 'gemini'],
            'natural_language': ['claude', 'gpt-4', 'gemini'],
            'sass_generation': ['claude', 'gpt-4', 'gemini'],
            'error_classification': ['gemini', 'gpt-4', 'claude'],
            'general': ['gemini', 'gpt-4', 'claude']
        }
        
        preferred_providers = task_preferences.get(task_type, task_preferences['general'])
        
        # Find best service based on preferences and performance
        for provider in preferred_providers:
            services = active_services.filtered(lambda s: s.ai_provider == provider)
            if services:
                # Return the one with best success rate
                best_service = services.sorted(
                    lambda s: s.successful_requests / max(s.total_requests, 1), 
                    reverse=True
                )[0]
                return best_service
        
        # Fallback to any active service
        return active_services.sorted(
            lambda s: s.successful_requests / max(s.total_requests, 1), 
            reverse=True
        )[0] if active_services else None
    
    def analyze_data_quality(self, data_sample, field_info):
        """📊 Use AI to analyze data quality and suggest improvements"""
        
        context = """
        You are DataSniffR, a sassy AI data quality expert. 
        Analyze the provided data sample and field information.
        Provide insights, identify issues, and suggest improvements with your signature sass.
        """
        
        prompt = f"""
        Field Information: {json.dumps(field_info, indent=2)}
        
        Data Sample: {json.dumps(data_sample, indent=2)}
        
        Please analyze this data and provide:
        1. Quality assessment (score 1-10)
        2. Issues identified
        3. Improvement suggestions
        4. Sassy comments about the data quality
        5. Specific actions to take
        
        Respond in JSON format with your signature DataSniffR style!
        """
        
        response = self.call_ai_service(prompt, context)
        
        if response.get('success'):
            try:
                # Try to parse JSON response
                analysis = json.loads(response['content'])
                return analysis
            except json.JSONDecodeError:
                # If not JSON, return raw response
                return {
                    'analysis': response['content'],
                    'raw_response': True
                }
        else:
            return {'error': response.get('error', 'AI analysis failed')}
    
    def generate_sassy_message(self, error_type, field_name, user_name):
        """💅 Generate personalized sassy messages using AI"""
        
        context = """
        You are DataSniffR, the sassiest AI data quality assistant ever created.
        Generate witty, humorous, but helpful messages about data quality issues.
        Keep it professional but fun, with emojis and personality.
        """
        
        prompt = f"""
        Generate a sassy but helpful message for:
        - User: {user_name}
        - Error Type: {error_type}
        - Field: {field_name}
        
        Make it encouraging, funny, and include a helpful tip.
        Use the DataSniffR personality with "mmm lol 🐶💾" signature.
        """
        
        response = self.call_ai_service(prompt, context, max_tokens=200)
        
        if response.get('success'):
            return response['content']
        else:
            # Fallback to default message
            return f"Hey {user_name}! Your {field_name} field needs some love! 🐶💾"
    
    def get_intelligent_suggestions(self, error_context):
        """💡 Get AI-powered suggestions for fixing data issues"""
        
        context = """
        You are an expert data quality consultant working with DataSniffR.
        Provide practical, actionable suggestions for fixing data quality issues.
        """
        
        prompt = f"""
        Data Quality Issue Context:
        {json.dumps(error_context, indent=2)}
        
        Please provide:
        1. Root cause analysis
        2. Step-by-step fix instructions
        3. Prevention strategies
        4. Best practices
        
        Make it practical and actionable!
        """
        
        response = self.call_ai_service(prompt, context)
        
        if response.get('success'):
            return response['content']
        else:
            return "Unable to generate suggestions at this time. Please check the AI service connection."
    
    @api.model
    def batch_ai_analysis(self, analysis_requests):
        """🚀 Process multiple AI requests efficiently"""
        
        results = []
        best_ai = self.get_best_ai_for_task('data_analysis')
        
        if not best_ai:
            return {'error': 'No AI services available'}
        
        for request in analysis_requests:
            try:
                result = best_ai.call_ai_service(
                    prompt=request.get('prompt', ''),
                    context=request.get('context', ''),
                    max_tokens=request.get('max_tokens', 1024)
                )
                
                results.append({
                    'request_id': request.get('id'),
                    'result': result
                })
                
                # Small delay to respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                results.append({
                    'request_id': request.get('id'),
                    'error': str(e)
                })
        
        return {
            'success': True,
            'results': results,
            'ai_service': best_ai.name
        }
    
    def generate_service_report(self):
        """📋 Generate performance report for AI service"""
        
        success_rate = (self.successful_requests / max(self.total_requests, 1)) * 100
        
        report = f"""
🤖 AI SERVICE PERFORMANCE REPORT 🤖

Service: {self.name}
Provider: {self.ai_provider}
Model: {self.model_name}

📊 USAGE STATISTICS:
• Total Requests: {self.total_requests}
• Successful: {self.successful_requests}
• Failed: {self.failed_requests}
• Success Rate: {success_rate:.1f}%
• Avg Response Time: {self.avg_response_time:.2f}s

📈 PERFORMANCE:
• Rate Limit Remaining: {self.rate_limit_remaining}
• Monthly Usage: {self.monthly_usage}
• Last Used: {self.last_used or 'Never'}

🎯 CAPABILITIES:
• Text Analysis: {'✅' if self.supports_text else '❌'}
• Vision Analysis: {'✅' if self.supports_vision else '❌'}
• Code Analysis: {'✅' if self.supports_code else '❌'}
• Data Analysis: {'✅' if self.supports_data else '❌'}

mmm lol 🐶💾 - AI service running {'smoothly' if success_rate > 90 else 'needs attention'}! 🤖✨
        """
        
        return report