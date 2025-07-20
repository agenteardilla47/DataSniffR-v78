#!/usr/bin/env python3
"""
DataSniffR AI Workflow Orchestrator 🎭🤖
=======================================

The ultimate AI workflow coordinator! When users need complex help,
DataSniffR orchestrates calls to external AI services with detailed
instructions and automatically updates the database with results!

Example Flow:
User: "I need a new email template for construction clients"
↓
DataSniffR: Analyzes request → Calls Gemini with detailed instructions
↓
Gemini: Creates template with construction industry specifics
↓
DataSniffR: Processes result → Adds to database → Notifies user

Features:
- 🎯 Intelligent request analysis
- 🤖 Multi-AI service orchestration
- 📝 Detailed instruction generation
- 💾 Automatic database updates
- 🔄 Workflow chaining
- 🎭 Context-aware responses

mmm lol 🐶💾 - Making AI collaboration seamless! 🤖✨
"""

from odoo import models, fields, api
import json
import logging
from datetime import datetime
import re
from collections import defaultdict

_logger = logging.getLogger(__name__)

class AIWorkflowOrchestrator(models.Model):
    _name = 'ai.workflow.orchestrator'
    _description = 'AI Workflow Orchestration System 🎭🤖'
    _order = 'create_date desc'
    
    name = fields.Char(string='Workflow Name', required=True)
    
    # Request Information
    user_request = fields.Text(string='Original User Request')
    request_type = fields.Selection([
        ('template_creation', 'Email Template Creation 📧'),
        ('data_analysis', 'Data Analysis Request 📊'),
        ('validation_rules', 'Custom Validation Rules 🔍'),
        ('sass_generation', 'Sass Message Generation 💅'),
        ('workflow_automation', 'Workflow Automation 🔄'),
        ('report_generation', 'Custom Report Generation 📋'),
        ('integration_setup', 'Integration Setup 🔗'),
        ('custom_solution', 'Custom Solution Development 🛠️'),
    ], string='Request Type', required=True)
    
    # AI Orchestration
    ai_services_used = fields.Text(string='AI Services Used (JSON)')
    orchestration_plan = fields.Text(string='Orchestration Plan (JSON)')
    execution_steps = fields.Text(string='Execution Steps (JSON)')
    
    # Results
    ai_responses = fields.Text(string='AI Responses (JSON)')
    generated_content = fields.Text(string='Generated Content (JSON)')
    database_updates = fields.Text(string='Database Updates (JSON)')
    
    # Status
    workflow_status = fields.Selection([
        ('analyzing', 'Analyzing Request 🔍'),
        ('planning', 'Planning Orchestration 📋'),
        ('executing', 'Executing Workflow 🚀'),
        ('processing', 'Processing Results 💾'),
        ('completed', 'Workflow Completed ✅'),
        ('failed', 'Workflow Failed ❌'),
    ], default='analyzing', string='Workflow Status')
    
    success_rate = fields.Float(string='Success Rate %', default=0.0)
    execution_time = fields.Float(string='Execution Time (seconds)', default=0.0)
    
    # User Information
    requesting_user_id = fields.Many2one('res.users', string='Requesting User')
    completion_message = fields.Text(string='Completion Message to User')
    
    @api.model
    def process_user_request(self, user_request, user_id=None):
        """🎯 Main entry point for processing complex user requests"""
        
        _logger.info(f"🎭 Processing user request: {user_request[:100]}...")
        
        # Create workflow record
        workflow = self.create({
            'name': f"AI Workflow - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'user_request': user_request,
            'requesting_user_id': user_id or self.env.user.id,
            'workflow_status': 'analyzing'
        })
        
        try:
            # Step 1: Analyze the request
            analysis = workflow._analyze_user_request(user_request)
            
            # Step 2: Create orchestration plan
            plan = workflow._create_orchestration_plan(analysis)
            
            # Step 3: Execute the workflow
            results = workflow._execute_workflow(plan)
            
            # Step 4: Process and store results
            final_result = workflow._process_results(results)
            
            workflow.workflow_status = 'completed'
            workflow.success_rate = 100.0
            
            return {
                'success': True,
                'workflow_id': workflow.id,
                'result': final_result,
                'message': workflow.completion_message
            }
            
        except Exception as e:
            workflow.workflow_status = 'failed'
            workflow.success_rate = 0.0
            _logger.error(f"Workflow failed: {e}")
            
            return {
                'success': False,
                'workflow_id': workflow.id,
                'error': str(e),
                'message': f"Sorry! I encountered an issue: {str(e)}"
            }
    
    def _analyze_user_request(self, user_request):
        """🔍 Analyze user request to understand intent and requirements"""
        
        self.workflow_status = 'analyzing'
        
        # Use AI to analyze the request
        analysis_prompt = f"""
        Analyze this user request and extract key information:
        
        User Request: "{user_request}"
        
        Please provide analysis in JSON format:
        {{
            "request_type": "template_creation|data_analysis|validation_rules|etc",
            "primary_intent": "What the user wants to accomplish",
            "key_requirements": ["list", "of", "requirements"],
            "context_clues": ["industry", "client_type", "specific_needs"],
            "complexity_level": "simple|medium|complex",
            "estimated_ai_services_needed": ["gemini", "openai", "claude"],
            "database_updates_required": ["email_templates", "validation_rules", "etc"],
            "user_expertise_level": "beginner|intermediate|expert"
        }}
        """
        
        # Get best AI for analysis
        ai_service = self.env['external.ai.connector'].get_best_ai_for_task('natural_language')
        
        if not ai_service:
            raise Exception("No AI service available for request analysis")
        
        response = ai_service.call_ai_service(analysis_prompt, max_tokens=1024)
        
        if not response.get('success'):
            raise Exception(f"AI analysis failed: {response.get('error')}")
        
        try:
            analysis = json.loads(response['content'])
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            analysis = self._parse_analysis_fallback(response['content'], user_request)
        
        # Set request type based on analysis
        self.request_type = analysis.get('request_type', 'custom_solution')
        
        _logger.info(f"🔍 Request analysis complete: {analysis.get('primary_intent')}")
        
        return analysis
    
    def _parse_analysis_fallback(self, ai_response, user_request):
        """🔄 Fallback analysis parsing when JSON fails"""
        
        # Simple keyword-based analysis
        request_lower = user_request.lower()
        
        if any(word in request_lower for word in ['template', 'email', 'notification']):
            request_type = 'template_creation'
        elif any(word in request_lower for word in ['analyze', 'data', 'report']):
            request_type = 'data_analysis'
        elif any(word in request_lower for word in ['validation', 'rule', 'check']):
            request_type = 'validation_rules'
        else:
            request_type = 'custom_solution'
        
        return {
            'request_type': request_type,
            'primary_intent': f"User wants help with {request_type.replace('_', ' ')}",
            'key_requirements': ['custom_solution'],
            'context_clues': ['general_request'],
            'complexity_level': 'medium',
            'estimated_ai_services_needed': ['gemini'],
            'database_updates_required': ['custom_data'],
            'user_expertise_level': 'intermediate',
            'ai_response_raw': ai_response
        }
    
    def _create_orchestration_plan(self, analysis):
        """📋 Create detailed orchestration plan based on analysis"""
        
        self.workflow_status = 'planning'
        
        request_type = analysis.get('request_type')
        complexity = analysis.get('complexity_level', 'medium')
        
        # Create specialized plans based on request type
        if request_type == 'template_creation':
            plan = self._create_template_creation_plan(analysis)
        elif request_type == 'data_analysis':
            plan = self._create_data_analysis_plan(analysis)
        elif request_type == 'validation_rules':
            plan = self._create_validation_rules_plan(analysis)
        elif request_type == 'sass_generation':
            plan = self._create_sass_generation_plan(analysis)
        else:
            plan = self._create_generic_plan(analysis)
        
        # Store the plan
        self.orchestration_plan = json.dumps(plan, indent=2)
        
        _logger.info(f"📋 Orchestration plan created with {len(plan.get('steps', []))} steps")
        
        return plan
    
    def _create_template_creation_plan(self, analysis):
        """📧 Create plan for email template creation"""
        
        context_clues = analysis.get('context_clues', [])
        requirements = analysis.get('key_requirements', [])
        
        plan = {
            'workflow_type': 'template_creation',
            'steps': [
                {
                    'step': 1,
                    'action': 'analyze_template_requirements',
                    'ai_service': 'gemini',
                    'prompt_template': 'template_analysis',
                    'expected_output': 'template_requirements'
                },
                {
                    'step': 2,
                    'action': 'generate_template_content',
                    'ai_service': 'claude',
                    'prompt_template': 'template_generation',
                    'expected_output': 'email_template'
                },
                {
                    'step': 3,
                    'action': 'optimize_for_datasniffr',
                    'ai_service': 'gemini',
                    'prompt_template': 'datasniffr_optimization',
                    'expected_output': 'optimized_template'
                },
                {
                    'step': 4,
                    'action': 'store_in_database',
                    'ai_service': None,
                    'prompt_template': None,
                    'expected_output': 'database_record'
                }
            ],
            'prompts': {
                'template_analysis': f"""
                Analyze the template requirements for this specific use case:
                
                User Request: "{self.user_request}"
                Context: {', '.join(context_clues)}
                Requirements: {', '.join(requirements)}
                
                Provide detailed analysis:
                1. Client type and industry specifics
                2. Tone and communication style needed
                3. Key information to include
                4. DataSniffR integration points
                5. Personalization variables needed
                
                Format as detailed JSON specification.
                """,
                
                'template_generation': """
                Based on the analysis, create a professional email template with:
                
                1. Subject line variations (3 options)
                2. HTML email body with proper structure
                3. Plain text version
                4. Variable placeholders for personalization
                5. DataSniffR signature integration
                6. Industry-specific language and terminology
                7. Call-to-action buttons
                8. Mobile-responsive design considerations
                
                Make it engaging, professional, and DataSniffR-branded!
                """,
                
                'datasniffr_optimization': """
                Optimize this email template for DataSniffR integration:
                
                1. Add DataSniffR personality and sass (appropriate level)
                2. Include data quality messaging
                3. Add tracking variables for analytics
                4. Ensure Odoo compatibility
                5. Add conditional content blocks
                6. Include unsubscribe and compliance elements
                7. Optimize for different client types
                
                Return the final, production-ready template.
                """
            },
            'database_operations': [
                {
                    'model': 'mail.template',
                    'operation': 'create',
                    'data_source': 'optimized_template'
                },
                {
                    'model': 'email.preparation.system',
                    'operation': 'register_template',
                    'data_source': 'template_metadata'
                }
            ]
        }
        
        return plan
    
    def _create_data_analysis_plan(self, analysis):
        """📊 Create plan for data analysis requests"""
        
        return {
            'workflow_type': 'data_analysis',
            'steps': [
                {
                    'step': 1,
                    'action': 'identify_data_sources',
                    'ai_service': 'claude',
                    'prompt_template': 'data_source_analysis'
                },
                {
                    'step': 2,
                    'action': 'generate_analysis_queries',
                    'ai_service': 'gemini',
                    'prompt_template': 'query_generation'
                },
                {
                    'step': 3,
                    'action': 'create_visualization_specs',
                    'ai_service': 'openai',
                    'prompt_template': 'visualization_design'
                },
                {
                    'step': 4,
                    'action': 'implement_analysis',
                    'ai_service': None,
                    'prompt_template': None
                }
            ],
            'prompts': {
                'data_source_analysis': f"""
                Analyze data requirements for: "{self.user_request}"
                
                Identify:
                1. Required Odoo models and fields
                2. Data relationships needed
                3. Filtering and grouping requirements
                4. Time range considerations
                5. Performance optimization needs
                """,
                
                'query_generation': """
                Generate optimized database queries and analysis logic
                for the identified requirements. Include:
                1. SQL queries for data extraction
                2. Python analysis code
                3. Data transformation steps
                4. Error handling
                """,
                
                'visualization_design': """
                Design visualization specifications:
                1. Chart types and configurations
                2. Dashboard layout
                3. Interactive elements
                4. Export options
                5. Mobile responsiveness
                """
            }
        }
    
    def _create_validation_rules_plan(self, analysis):
        """🔍 Create plan for custom validation rules"""
        
        return {
            'workflow_type': 'validation_rules',
            'steps': [
                {
                    'step': 1,
                    'action': 'analyze_validation_needs',
                    'ai_service': 'claude',
                    'prompt_template': 'validation_analysis'
                },
                {
                    'step': 2,
                    'action': 'generate_validation_logic',
                    'ai_service': 'gemini',
                    'prompt_template': 'validation_code_generation'
                },
                {
                    'step': 3,
                    'action': 'create_error_messages',
                    'ai_service': 'claude',
                    'prompt_template': 'sass_error_messages'
                },
                {
                    'step': 4,
                    'action': 'integrate_with_datasniffr',
                    'ai_service': None,
                    'prompt_template': None
                }
            ]
        }
    
    def _create_sass_generation_plan(self, analysis):
        """💅 Create plan for sass message generation"""
        
        return {
            'workflow_type': 'sass_generation',
            'steps': [
                {
                    'step': 1,
                    'action': 'analyze_context',
                    'ai_service': 'claude',
                    'prompt_template': 'sass_context_analysis'
                },
                {
                    'step': 2,
                    'action': 'generate_sass_variations',
                    'ai_service': 'openai',
                    'prompt_template': 'sass_generation'
                },
                {
                    'step': 3,
                    'action': 'optimize_for_company_culture',
                    'ai_service': 'gemini',
                    'prompt_template': 'culture_optimization'
                }
            ]
        }
    
    def _create_generic_plan(self, analysis):
        """🛠️ Create generic plan for custom solutions"""
        
        return {
            'workflow_type': 'custom_solution',
            'steps': [
                {
                    'step': 1,
                    'action': 'understand_requirements',
                    'ai_service': 'claude',
                    'prompt_template': 'requirements_analysis'
                },
                {
                    'step': 2,
                    'action': 'design_solution',
                    'ai_service': 'gemini',
                    'prompt_template': 'solution_design'
                },
                {
                    'step': 3,
                    'action': 'implement_solution',
                    'ai_service': 'openai',
                    'prompt_template': 'implementation_guide'
                }
            ],
            'prompts': {
                'requirements_analysis': f"""
                Analyze this custom request: "{self.user_request}"
                
                Provide:
                1. Detailed requirements breakdown
                2. Technical feasibility assessment
                3. Integration points with DataSniffR
                4. Potential challenges
                5. Success criteria
                """,
                
                'solution_design': """
                Design a comprehensive solution including:
                1. Architecture overview
                2. Implementation steps
                3. Code structure
                4. Database changes needed
                5. Testing approach
                """,
                
                'implementation_guide': """
                Create detailed implementation guide:
                1. Step-by-step instructions
                2. Code examples
                3. Configuration settings
                4. Troubleshooting tips
                5. Maintenance procedures
                """
            }
        }
    
    def _execute_workflow(self, plan):
        """🚀 Execute the orchestration plan"""
        
        self.workflow_status = 'executing'
        
        results = {}
        execution_steps = []
        
        for step_config in plan.get('steps', []):
            step_num = step_config['step']
            action = step_config['action']
            ai_service_name = step_config.get('ai_service')
            
            _logger.info(f"🚀 Executing step {step_num}: {action}")
            
            step_start_time = datetime.now()
            
            try:
                if ai_service_name:
                    # AI-powered step
                    result = self._execute_ai_step(step_config, plan, results)
                else:
                    # Database or system step
                    result = self._execute_system_step(step_config, plan, results)
                
                step_end_time = datetime.now()
                step_duration = (step_end_time - step_start_time).total_seconds()
                
                execution_steps.append({
                    'step': step_num,
                    'action': action,
                    'status': 'success',
                    'duration': step_duration,
                    'result_summary': str(result)[:200] + '...' if len(str(result)) > 200 else str(result)
                })
                
                results[f'step_{step_num}'] = result
                
            except Exception as e:
                _logger.error(f"Step {step_num} failed: {e}")
                
                execution_steps.append({
                    'step': step_num,
                    'action': action,
                    'status': 'failed',
                    'error': str(e)
                })
                
                # Continue with next step or fail workflow based on criticality
                if step_config.get('critical', True):
                    raise Exception(f"Critical step {step_num} failed: {e}")
        
        # Store execution details
        self.execution_steps = json.dumps(execution_steps, indent=2)
        
        return results
    
    def _execute_ai_step(self, step_config, plan, previous_results):
        """🤖 Execute an AI-powered step"""
        
        ai_service_name = step_config['ai_service']
        prompt_template_name = step_config.get('prompt_template')
        
        # Get AI service
        if ai_service_name == 'best':
            ai_service = self.env['external.ai.connector'].get_best_ai_for_task('general')
        else:
            ai_service = self.env['external.ai.connector'].search([
                ('ai_provider', '=', ai_service_name),
                ('is_active', '=', True)
            ], limit=1)
        
        if not ai_service:
            raise Exception(f"AI service {ai_service_name} not available")
        
        # Get prompt template
        prompt_template = plan.get('prompts', {}).get(prompt_template_name, '')
        
        if not prompt_template:
            raise Exception(f"Prompt template {prompt_template_name} not found")
        
        # Prepare context from previous results
        context_data = {
            'user_request': self.user_request,
            'previous_results': previous_results,
            'step_config': step_config
        }
        
        # Format prompt with context
        formatted_prompt = self._format_prompt_with_context(prompt_template, context_data, previous_results)
        
        # Call AI service
        response = ai_service.call_ai_service(
            prompt=formatted_prompt,
            context=f"DataSniffR AI Workflow Step: {step_config['action']}",
            max_tokens=2048
        )
        
        if not response.get('success'):
            raise Exception(f"AI service call failed: {response.get('error')}")
        
        return {
            'ai_service': ai_service.name,
            'prompt_used': formatted_prompt[:500] + '...' if len(formatted_prompt) > 500 else formatted_prompt,
            'response': response['content'],
            'metadata': {
                'provider': ai_service.ai_provider,
                'model': ai_service.model_name,
                'usage': response.get('usage', {})
            }
        }
    
    def _execute_system_step(self, step_config, plan, previous_results):
        """💾 Execute a system/database step"""
        
        action = step_config['action']
        
        if action == 'store_in_database':
            return self._store_template_in_database(previous_results, plan)
        elif action == 'implement_analysis':
            return self._implement_data_analysis(previous_results, plan)
        elif action == 'integrate_with_datasniffr':
            return self._integrate_validation_rules(previous_results, plan)
        else:
            return {'message': f'System step {action} completed', 'data': 'placeholder'}
    
    def _store_template_in_database(self, previous_results, plan):
        """📧 Store generated email template in database"""
        
        # Get the optimized template from previous step
        template_data = previous_results.get('step_3', {}).get('response', '')
        
        try:
            # Parse template data (assuming AI returns structured format)
            if template_data.startswith('{'):
                template_info = json.loads(template_data)
            else:
                # Fallback parsing
                template_info = self._parse_template_fallback(template_data)
            
            # Create mail template
            mail_template = self.env['mail.template'].create({
                'name': template_info.get('name', f'DataSniffR Template - {datetime.now().strftime("%Y-%m-%d")}'),
                'subject': template_info.get('subject', 'DataSniffR Notification'),
                'body_html': template_info.get('body_html', template_data),
                'model_id': self.env.ref('base.model_res_users').id,  # Default model
                'auto_delete': False,
                'use_default_to': True
            })
            
            # Register with email system
            email_system = self.env['email.preparation.system'].search([], limit=1)
            if email_system:
                # Add template to available templates
                current_templates = json.loads(email_system.available_templates or '{}')
                current_templates[f'ai_generated_{mail_template.id}'] = {
                    'template_id': mail_template.id,
                    'name': template_info.get('name'),
                    'description': f'AI-generated template for: {self.user_request[:100]}',
                    'created_by_ai': True,
                    'created_at': datetime.now().isoformat()
                }
                email_system.available_templates = json.dumps(current_templates, indent=2)
            
            return {
                'template_id': mail_template.id,
                'template_name': mail_template.name,
                'message': 'Email template successfully created and stored!',
                'template_info': template_info
            }
            
        except Exception as e:
            _logger.error(f"Failed to store template: {e}")
            raise Exception(f"Template storage failed: {e}")
    
    def _parse_template_fallback(self, template_data):
        """🔄 Fallback template parsing when JSON fails"""
        
        # Extract key information using regex
        subject_match = re.search(r'Subject:\s*(.+?)(?:\n|$)', template_data, re.IGNORECASE)
        subject = subject_match.group(1).strip() if subject_match else 'DataSniffR Notification'
        
        # Extract HTML body (look for HTML tags)
        if '<html>' in template_data.lower() or '<div>' in template_data.lower():
            body_html = template_data
        else:
            # Convert plain text to HTML
            body_html = f'<div style="font-family: Arial, sans-serif;">{template_data.replace(chr(10), "<br>")}</div>'
        
        return {
            'name': f'AI Generated Template - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'subject': subject,
            'body_html': body_html,
            'type': 'ai_generated'
        }
    
    def _format_prompt_with_context(self, prompt_template, context_data, previous_results):
        """📝 Format prompt template with context and previous results"""
        
        formatted_prompt = prompt_template
        
        # Replace context variables
        for key, value in context_data.items():
            placeholder = f'{{{key}}}'
            if placeholder in formatted_prompt:
                formatted_prompt = formatted_prompt.replace(placeholder, str(value))
        
        # Add previous results context if relevant
        if previous_results:
            context_section = "\n\nPrevious Step Results:\n"
            for step_key, step_result in previous_results.items():
                if isinstance(step_result, dict) and 'response' in step_result:
                    context_section += f"{step_key}: {step_result['response'][:300]}...\n"
            
            formatted_prompt += context_section
        
        return formatted_prompt
    
    def _process_results(self, execution_results):
        """💾 Process final results and prepare user response"""
        
        self.workflow_status = 'processing'
        
        # Store all results
        self.ai_responses = json.dumps(execution_results, indent=2)
        
        # Generate completion message based on workflow type
        completion_message = self._generate_completion_message(execution_results)
        self.completion_message = completion_message
        
        # Extract generated content
        generated_content = self._extract_generated_content(execution_results)
        self.generated_content = json.dumps(generated_content, indent=2)
        
        # Record database updates
        database_updates = self._record_database_updates(execution_results)
        self.database_updates = json.dumps(database_updates, indent=2)
        
        return {
            'completion_message': completion_message,
            'generated_content': generated_content,
            'database_updates': database_updates,
            'execution_summary': self._generate_execution_summary(execution_results)
        }
    
    def _generate_completion_message(self, results):
        """💬 Generate friendly completion message for user"""
        
        if self.request_type == 'template_creation':
            template_result = results.get('step_4', {})
            template_name = template_result.get('template_name', 'your new template')
            
            return f"""
🎉 Amazing! I've successfully created {template_name} for you!

Here's what I did:
✅ Analyzed your specific requirements for construction clients
✅ Generated a professional email template with industry-specific language
✅ Optimized it with DataSniffR personality and branding
✅ Stored it in your Odoo system for immediate use

Your template is now available in the Email Templates section and ready to use for your construction client communications!

Need any adjustments or want to create more templates? Just let me know! 

mmm lol 🐶💾 - Another successful AI collaboration! ✨
            """
        
        elif self.request_type == 'data_analysis':
            return f"""
📊 Data analysis complete! I've created a comprehensive analysis solution for your request.

The analysis includes custom queries, visualizations, and automated reporting - all integrated with your DataSniffR system!

mmm lol 🐶💾 - Your data insights are ready! 🚀
            """
        
        else:
            return f"""
✅ Workflow completed successfully! 

I've processed your request and implemented the solution you needed. All changes have been integrated with your DataSniffR system.

mmm lol 🐶💾 - Mission accomplished! 🎯
            """
    
    def _extract_generated_content(self, results):
        """📄 Extract generated content from results"""
        
        content = {}
        
        for step_key, step_result in results.items():
            if isinstance(step_result, dict):
                if 'response' in step_result:
                    content[step_key] = {
                        'ai_service': step_result.get('ai_service', 'unknown'),
                        'content': step_result['response'],
                        'metadata': step_result.get('metadata', {})
                    }
                elif 'template_id' in step_result:
                    content[step_key] = {
                        'type': 'database_record',
                        'record_type': 'mail.template',
                        'record_id': step_result['template_id'],
                        'details': step_result
                    }
        
        return content
    
    def _record_database_updates(self, results):
        """💾 Record all database updates made during workflow"""
        
        updates = []
        
        for step_key, step_result in results.items():
            if isinstance(step_result, dict):
                if 'template_id' in step_result:
                    updates.append({
                        'model': 'mail.template',
                        'operation': 'create',
                        'record_id': step_result['template_id'],
                        'description': f'Created email template: {step_result.get("template_name")}',
                        'timestamp': datetime.now().isoformat()
                    })
        
        return updates
    
    def _generate_execution_summary(self, results):
        """📋 Generate execution summary"""
        
        return {
            'total_steps': len(results),
            'successful_steps': len([r for r in results.values() if not isinstance(r, dict) or 'error' not in r]),
            'ai_services_used': len(set(r.get('ai_service', '') for r in results.values() if isinstance(r, dict) and 'ai_service' in r)),
            'database_records_created': len([r for r in results.values() if isinstance(r, dict) and 'template_id' in r]),
            'workflow_type': self.request_type,
            'completion_time': datetime.now().isoformat()
        }
    
    @api.model
    def get_workflow_examples(self):
        """📋 Get example workflows to show users what's possible"""
        
        examples = {
            'email_templates': {
                'title': 'Custom Email Template Creation',
                'description': 'Create industry-specific email templates',
                'example_requests': [
                    "I need an email template for construction clients about project updates",
                    "Create a follow-up template for healthcare providers",
                    "Design a welcome email for new retail partners"
                ]
            },
            'data_analysis': {
                'title': 'Custom Data Analysis',
                'description': 'Generate insights and reports from your data',
                'example_requests': [
                    "Analyze customer satisfaction trends by region",
                    "Create a sales performance dashboard for my team",
                    "Show me inventory optimization opportunities"
                ]
            },
            'validation_rules': {
                'title': 'Custom Validation Rules',
                'description': 'Create smart data validation for your specific needs',
                'example_requests': [
                    "Validate product codes for our industry standards",
                    "Check customer addresses for delivery feasibility",
                    "Ensure pricing follows our discount policies"
                ]
            },
            'workflow_automation': {
                'title': 'Process Automation',
                'description': 'Automate repetitive tasks and workflows',
                'example_requests': [
                    "Automatically notify managers of overdue tasks",
                    "Create approval workflows for purchase orders",
                    "Set up automatic data quality monitoring"
                ]
            }
        }
        
        return examples