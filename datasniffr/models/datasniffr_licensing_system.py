#!/usr/bin/env python3
"""
DataSniffR Enterprise Licensing System 💎🏢
==========================================

The ultimate licensing and enterprise management system for DataSniffR!
Supports both company-wide enterprise licenses and individual user licenses
with advanced key management, usage tracking, and billing integration.

Features:
- 🏢 Enterprise Company-Wide Licensing
- 👤 Individual User Licensing
- 🔐 Secure License Key Management
- 📊 Usage Tracking & Analytics
- 💰 Flexible Pricing Models
- 🎯 Feature Access Control
- 📈 Scalable Billing Integration
- 🛡️ Anti-Piracy Protection

mmm lol 🐶💾 - Making DataSniffR profitable and scalable! 💰✨
"""

from odoo import models, fields, api
import json
import logging
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import requests

_logger = logging.getLogger(__name__)

class DataSniffRLicensingSystem(models.Model):
    _name = 'datasniffr.licensing.system'
    _description = 'DataSniffR Enterprise Licensing System 💎🏢'
    _order = 'create_date desc'
    
    name = fields.Char(string='License Name', required=True)
    
    # License Type
    license_type = fields.Selection([
        ('individual', 'Individual User License 👤'),
        ('team', 'Team License (5-25 users) 👥'),
        ('enterprise', 'Enterprise License (Unlimited) 🏢'),
        ('startup', 'Startup License (Special Pricing) 🚀'),
        ('educational', 'Educational License (Schools) 🎓'),
        ('trial', 'Trial License (30 days) 🎯'),
    ], string='License Type', required=True, default='individual')
    
    # License Details
    license_key = fields.Char(string='License Key', required=True, readonly=True)
    activation_code = fields.Char(string='Activation Code', readonly=True)
    company_id = fields.Many2one('res.company', string='Licensed Company')
    
    # Pricing & Billing
    pricing_model = fields.Selection([
        ('monthly', 'Monthly Subscription 📅'),
        ('annual', 'Annual Subscription 🗓️'),
        ('perpetual', 'Perpetual License 🔒'),
        ('usage_based', 'Usage-Based Pricing 📊'),
        ('enterprise_custom', 'Enterprise Custom Deal 🏢'),
    ], string='Pricing Model', required=True, default='monthly')
    
    price_per_user = fields.Float(string='Price Per User/Month', default=0.0)
    enterprise_price = fields.Float(string='Enterprise Price', default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    # License Limits
    max_users = fields.Integer(string='Maximum Users', default=1)
    max_data_records = fields.Integer(string='Max Data Records/Month', default=10000)
    max_ai_calls = fields.Integer(string='Max AI Service Calls/Month', default=1000)
    max_boss_battles = fields.Integer(string='Max Boss Battles/Month', default=5)
    
    # Feature Access
    features_included = fields.Text(string='Included Features (JSON)')
    ai_services_enabled = fields.Boolean(string='AI Services Access', default=True)
    boss_battles_enabled = fields.Boolean(string='Boss Battles Feature', default=True)
    dashboard_enabled = fields.Boolean(string='Advanced Dashboard', default=True)
    content_guardian_enabled = fields.Boolean(string='Content Guardian', default=False)
    
    # License Status
    is_active = fields.Boolean(string='License Active', default=True)
    activation_date = fields.Datetime(string='Activation Date')
    expiration_date = fields.Datetime(string='Expiration Date')
    trial_end_date = fields.Datetime(string='Trial End Date')
    
    # Usage Tracking
    current_users = fields.Integer(string='Current Active Users', default=0)
    data_records_used = fields.Integer(string='Data Records Used This Month', default=0)
    ai_calls_used = fields.Integer(string='AI Calls Used This Month', default=0)
    boss_battles_used = fields.Integer(string='Boss Battles Used This Month', default=0)
    
    # Enterprise Management
    enterprise_admin_id = fields.Many2one('res.users', string='Enterprise Administrator')
    user_licenses = fields.One2many('datasniffr.user.license', 'parent_license_id', string='User Licenses')
    
    # Billing Integration
    stripe_subscription_id = fields.Char(string='Stripe Subscription ID')
    billing_contact_id = fields.Many2one('res.partner', string='Billing Contact')
    last_payment_date = fields.Datetime(string='Last Payment Date')
    next_billing_date = fields.Datetime(string='Next Billing Date')
    
    @api.model
    def create_enterprise_license(self, company_data, admin_user_id):
        """🏢 Create enterprise license for company-wide access"""
        
        # Generate secure license key
        license_key = self._generate_license_key('enterprise')
        activation_code = self._generate_activation_code()
        
        # Calculate pricing based on company size
        estimated_users = company_data.get('estimated_users', 50)
        enterprise_pricing = self._calculate_enterprise_pricing(estimated_users)
        
        # Set feature access for enterprise
        enterprise_features = {
            'universal_scanner': True,
            'ai_orchestration': True,
            'boss_battles': True,
            'content_guardian': True,
            'responsive_dashboard': True,
            'advanced_analytics': True,
            'priority_support': True,
            'custom_integrations': True,
            'white_label_options': True,
            'api_access': True,
            'bulk_operations': True,
            'advanced_reporting': True
        }
        
        license = self.create({
            'name': f"Enterprise License - {company_data.get('company_name')}",
            'license_type': 'enterprise',
            'license_key': license_key,
            'activation_code': activation_code,
            'company_id': company_data.get('company_id'),
            'pricing_model': 'annual',
            'enterprise_price': enterprise_pricing['annual_price'],
            'max_users': 999999,  # Unlimited for enterprise
            'max_data_records': 999999999,  # Unlimited
            'max_ai_calls': 999999999,  # Unlimited
            'max_boss_battles': 999999,  # Unlimited
            'features_included': json.dumps(enterprise_features, indent=2),
            'ai_services_enabled': True,
            'boss_battles_enabled': True,
            'dashboard_enabled': True,
            'content_guardian_enabled': True,
            'enterprise_admin_id': admin_user_id,
            'activation_date': datetime.now(),
            'expiration_date': datetime.now() + timedelta(days=365)
        })
        
        # Create admin access
        self._create_user_license(license.id, admin_user_id, 'admin')
        
        _logger.info(f"🏢 Enterprise license created for {company_data.get('company_name')}")
        
        return license
    
    @api.model
    def create_individual_license(self, user_data, license_plan='individual'):
        """👤 Create individual user license"""
        
        license_key = self._generate_license_key('individual')
        activation_code = self._generate_activation_code()
        
        # Individual license features
        individual_features = {
            'universal_scanner': True,
            'ai_orchestration': license_plan in ['pro', 'premium'],
            'boss_battles': license_plan in ['pro', 'premium'],
            'content_guardian': license_plan == 'premium',
            'responsive_dashboard': True,
            'basic_analytics': True,
            'email_support': True,
            'api_access': license_plan in ['pro', 'premium']
        }
        
        # Pricing based on plan
        pricing_tiers = {
            'basic': {'monthly': 9.99, 'annual': 99.99},
            'pro': {'monthly': 19.99, 'annual': 199.99},
            'premium': {'monthly': 39.99, 'annual': 399.99}
        }
        
        plan_pricing = pricing_tiers.get(license_plan, pricing_tiers['basic'])
        
        license = self.create({
            'name': f"Individual License - {user_data.get('user_name')} ({license_plan.title()})",
            'license_type': 'individual',
            'license_key': license_key,
            'activation_code': activation_code,
            'pricing_model': 'monthly',
            'price_per_user': plan_pricing['monthly'],
            'max_users': 1,
            'max_data_records': 50000 if license_plan == 'premium' else 25000 if license_plan == 'pro' else 10000,
            'max_ai_calls': 5000 if license_plan == 'premium' else 2000 if license_plan == 'pro' else 500,
            'max_boss_battles': 50 if license_plan == 'premium' else 20 if license_plan == 'pro' else 5,
            'features_included': json.dumps(individual_features, indent=2),
            'ai_services_enabled': True,
            'boss_battles_enabled': license_plan in ['pro', 'premium'],
            'dashboard_enabled': True,
            'content_guardian_enabled': license_plan == 'premium',
            'activation_date': datetime.now(),
            'expiration_date': datetime.now() + timedelta(days=30)  # Monthly billing
        })
        
        _logger.info(f"👤 Individual {license_plan} license created for {user_data.get('user_name')}")
        
        return license
    
    def _generate_license_key(self, license_type):
        """🔐 Generate secure license key"""
        
        # Create unique identifier
        timestamp = str(int(datetime.now().timestamp()))
        random_part = secrets.token_hex(8)
        type_prefix = {
            'enterprise': 'ENT',
            'individual': 'IND', 
            'team': 'TEAM',
            'trial': 'TRIAL'
        }.get(license_type, 'GEN')
        
        # Create license key
        key_data = f"{type_prefix}-{timestamp}-{random_part}"
        
        # Add checksum for validation
        checksum = hashlib.md5(key_data.encode()).hexdigest()[:4].upper()
        license_key = f"{key_data}-{checksum}"
        
        return license_key
    
    def _generate_activation_code(self):
        """🎯 Generate activation code for users"""
        
        # 6-digit activation code
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    def _calculate_enterprise_pricing(self, estimated_users):
        """💰 Calculate enterprise pricing based on company size"""
        
        # Tiered pricing model
        if estimated_users <= 50:
            base_price = 999.99
            tier = 'Small Enterprise'
        elif estimated_users <= 200:
            base_price = 2999.99
            tier = 'Medium Enterprise'
        elif estimated_users <= 1000:
            base_price = 9999.99
            tier = 'Large Enterprise'
        else:
            base_price = 24999.99
            tier = 'Global Enterprise'
        
        # Annual discount
        annual_price = base_price * 12 * 0.8  # 20% annual discount
        
        return {
            'tier': tier,
            'monthly_price': base_price,
            'annual_price': annual_price,
            'estimated_users': estimated_users,
            'price_per_user_month': base_price / estimated_users if estimated_users > 0 else 0
        }
    
    def activate_license(self, activation_code, user_id):
        """🚀 Activate license with activation code"""
        
        if self.activation_code != activation_code:
            return {
                'success': False,
                'message': 'Invalid activation code. Please check and try again.'
            }
        
        if not self.is_active:
            return {
                'success': False,
                'message': 'License is not active. Please contact support.'
            }
        
        if self.expiration_date and self.expiration_date < datetime.now():
            return {
                'success': False,
                'message': 'License has expired. Please renew your subscription.'
            }
        
        # Create or update user license
        user_license = self._create_user_license(self.id, user_id, 'user')
        
        # Update license usage
        self.current_users += 1
        
        return {
            'success': True,
            'message': 'License activated successfully! Welcome to DataSniffR! 🎉',
            'user_license_id': user_license.id,
            'features': json.loads(self.features_included or '{}'),
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None
        }
    
    def _create_user_license(self, parent_license_id, user_id, role='user'):
        """👤 Create individual user license under parent license"""
        
        user_license = self.env['datasniffr.user.license'].create({
            'parent_license_id': parent_license_id,
            'user_id': user_id,
            'role': role,
            'is_active': True,
            'activation_date': datetime.now()
        })
        
        return user_license
    
    def check_feature_access(self, feature_name, user_id=None):
        """🎯 Check if user has access to specific feature"""
        
        if not self.is_active:
            return False
        
        if self.expiration_date and self.expiration_date < datetime.now():
            return False
        
        features = json.loads(self.features_included or '{}')
        return features.get(feature_name, False)
    
    def track_usage(self, usage_type, amount=1, user_id=None):
        """📊 Track feature usage for billing and limits"""
        
        if usage_type == 'data_records':
            self.data_records_used += amount
            if self.data_records_used > self.max_data_records:
                return {
                    'allowed': False,
                    'message': 'Monthly data record limit exceeded. Please upgrade your plan.',
                    'usage': self.data_records_used,
                    'limit': self.max_data_records
                }
        
        elif usage_type == 'ai_calls':
            self.ai_calls_used += amount
            if self.ai_calls_used > self.max_ai_calls:
                return {
                    'allowed': False,
                    'message': 'Monthly AI service call limit exceeded. Please upgrade your plan.',
                    'usage': self.ai_calls_used,
                    'limit': self.max_ai_calls
                }
        
        elif usage_type == 'boss_battles':
            self.boss_battles_used += amount
            if self.boss_battles_used > self.max_boss_battles:
                return {
                    'allowed': False,
                    'message': 'Monthly boss battle limit exceeded. Please upgrade your plan.',
                    'usage': self.boss_battles_used,
                    'limit': self.max_boss_battles
                }
        
        return {
            'allowed': True,
            'usage': getattr(self, f'{usage_type}_used'),
            'limit': getattr(self, f'max_{usage_type}'),
            'percentage_used': (getattr(self, f'{usage_type}_used') / getattr(self, f'max_{usage_type}')) * 100
        }
    
    def generate_billing_invoice(self):
        """💰 Generate billing invoice for license"""
        
        if self.license_type == 'enterprise':
            amount = self.enterprise_price
            description = f"DataSniffR Enterprise License - {self.name}"
        else:
            amount = self.price_per_user * self.current_users
            description = f"DataSniffR License - {self.current_users} user(s)"
        
        invoice_data = {
            'license_id': self.id,
            'license_name': self.name,
            'billing_period': f"{datetime.now().strftime('%Y-%m')}",
            'amount': amount,
            'currency': self.currency_id.name,
            'description': description,
            'usage_summary': {
                'users': self.current_users,
                'data_records': self.data_records_used,
                'ai_calls': self.ai_calls_used,
                'boss_battles': self.boss_battles_used
            },
            'features_included': json.loads(self.features_included or '{}'),
            'billing_contact': self.billing_contact_id.name if self.billing_contact_id else None,
            'due_date': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        return invoice_data
    
    def upgrade_license(self, new_plan):
        """⬆️ Upgrade license to higher tier"""
        
        upgrade_paths = {
            'individual': {
                'basic_to_pro': {'price_increase': 10.00, 'features': ['ai_orchestration', 'boss_battles']},
                'basic_to_premium': {'price_increase': 30.00, 'features': ['ai_orchestration', 'boss_battles', 'content_guardian']},
                'pro_to_premium': {'price_increase': 20.00, 'features': ['content_guardian']}
            },
            'team_to_enterprise': {
                'price_model': 'custom',
                'features': ['unlimited_users', 'priority_support', 'custom_integrations']
            }
        }
        
        # Implementation for license upgrades
        pass
    
    def send_license_notification(self, notification_type):
        """📧 Send license-related notifications"""
        
        notifications = {
            'activation_success': {
                'subject': '🎉 DataSniffR License Activated Successfully!',
                'template': 'license_activation_success'
            },
            'expiration_warning': {
                'subject': '⚠️ DataSniffR License Expiring Soon',
                'template': 'license_expiration_warning'
            },
            'usage_limit_warning': {
                'subject': '📊 DataSniffR Usage Limit Warning',
                'template': 'usage_limit_warning'
            },
            'upgrade_available': {
                'subject': '⬆️ DataSniffR License Upgrade Available',
                'template': 'upgrade_available'
            }
        }
        
        # Send notification via email system
        if notification_type in notifications:
            email_system = self.env['email.preparation.system'].search([], limit=1)
            if email_system:
                email_system.send_license_notification(
                    self.id,
                    notification_type,
                    notifications[notification_type]
                )
    
    def get_license_dashboard_data(self):
        """📊 Get license dashboard data for admin"""
        
        return {
            'license_info': {
                'name': self.name,
                'type': self.license_type,
                'status': 'Active' if self.is_active else 'Inactive',
                'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None
            },
            'usage_stats': {
                'users': {
                    'current': self.current_users,
                    'limit': self.max_users,
                    'percentage': (self.current_users / max(self.max_users, 1)) * 100
                },
                'data_records': {
                    'used': self.data_records_used,
                    'limit': self.max_data_records,
                    'percentage': (self.data_records_used / max(self.max_data_records, 1)) * 100
                },
                'ai_calls': {
                    'used': self.ai_calls_used,
                    'limit': self.max_ai_calls,
                    'percentage': (self.ai_calls_used / max(self.max_ai_calls, 1)) * 100
                },
                'boss_battles': {
                    'used': self.boss_battles_used,
                    'limit': self.max_boss_battles,
                    'percentage': (self.boss_battles_used / max(self.max_boss_battles, 1)) * 100
                }
            },
            'features': json.loads(self.features_included or '{}'),
            'billing_info': {
                'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
                'pricing_model': self.pricing_model,
                'monthly_cost': self.price_per_user * self.current_users if self.license_type != 'enterprise' else self.enterprise_price / 12
            }
        }
    
    @api.model
    def validate_license_key(self, license_key):
        """🔍 Validate license key format and checksum"""
        
        try:
            parts = license_key.split('-')
            if len(parts) != 4:
                return False
            
            # Verify checksum
            key_data = '-'.join(parts[:-1])
            expected_checksum = hashlib.md5(key_data.encode()).hexdigest()[:4].upper()
            
            return parts[-1] == expected_checksum
        
        except Exception:
            return False
    
    def generate_license_report(self):
        """📋 Generate comprehensive license report"""
        
        report = f"""
💎 DATASNIFFR LICENSE REPORT 💎

License: {self.name}
Type: {self.license_type.upper()}
Status: {'🟢 ACTIVE' if self.is_active else '🔴 INACTIVE'}
License Key: {self.license_key}

📊 USAGE STATISTICS:
• Users: {self.current_users}/{self.max_users}
• Data Records: {self.data_records_used:,}/{self.max_data_records:,}
• AI Calls: {self.ai_calls_used:,}/{self.max_ai_calls:,}
• Boss Battles: {self.boss_battles_used}/{self.max_boss_battles}

💰 BILLING INFORMATION:
• Pricing Model: {self.pricing_model}
• Monthly Cost: ${self.price_per_user * self.current_users if self.license_type != 'enterprise' else self.enterprise_price / 12:.2f}
• Next Billing: {self.next_billing_date or 'Not set'}

🎯 FEATURES INCLUDED:
{self._format_features(json.loads(self.features_included or '{}'))}

📅 LICENSE DATES:
• Activated: {self.activation_date}
• Expires: {self.expiration_date or 'Never (Perpetual)'}

mmm lol 🐶💾 - Your DataSniffR license is {'dancing smoothly' if self.is_active else 'needs attention'}! 💎✨
        """
        
        return report
    
    def _format_features(self, features):
        """📝 Format features list for report"""
        
        formatted = []
        for feature, enabled in features.items():
            status = '✅' if enabled else '❌'
            feature_name = feature.replace('_', ' ').title()
            formatted.append(f"  {status} {feature_name}")
        
        return '\n'.join(formatted) if formatted else '  • No features configured'


class DataSniffRUserLicense(models.Model):
    _name = 'datasniffr.user.license'
    _description = 'Individual User License Record 👤💎'
    
    parent_license_id = fields.Many2one('datasniffr.licensing.system', string='Parent License', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    
    role = fields.Selection([
        ('admin', 'Enterprise Administrator 👑'),
        ('manager', 'Team Manager 👥'),
        ('user', 'Standard User 👤'),
    ], string='User Role', default='user')
    
    is_active = fields.Boolean(string='Active', default=True)
    activation_date = fields.Datetime(string='Activation Date', default=datetime.now)
    last_login = fields.Datetime(string='Last DataSniffR Login')
    
    # Usage Tracking
    personal_data_records = fields.Integer(string='Personal Data Records Used', default=0)
    personal_ai_calls = fields.Integer(string='Personal AI Calls Used', default=0)
    personal_boss_battles = fields.Integer(string='Personal Boss Battles Started', default=0)
    
    def track_user_activity(self, activity_type, details=None):
        """📊 Track individual user activity"""
        
        if activity_type == 'login':
            self.last_login = datetime.now()
        elif activity_type == 'data_record_scan':
            self.personal_data_records += details.get('records_count', 1)
        elif activity_type == 'ai_service_call':
            self.personal_ai_calls += 1
        elif activity_type == 'boss_battle_start':
            self.personal_boss_battles += 1
        
        # Update parent license usage
        if self.parent_license_id:
            self.parent_license_id.track_usage(activity_type, details.get('amount', 1), self.user_id.id)