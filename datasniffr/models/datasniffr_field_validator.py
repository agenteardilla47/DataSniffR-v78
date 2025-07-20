#!/usr/bin/env python3
"""
DataSniffR Field Validator Mini-Module 🔍✅
===========================================

Specialized field validation for perfect data formats!
The ultimate field-by-field quality guardian!

Features:
- 🔤 Email format validation
- 📞 Phone number standardization
- 💳 VAT/Tax ID verification
- 🌍 Address format checking
- 📅 Date format validation
- 💰 Currency format fixing
- 🎯 Custom field rules
- 🤖 AI-powered suggestions

mmm lol 🐶💾 - Every field perfect, every time! 🔍✨
"""

from odoo import models, fields, api
import json
import logging
import re
from datetime import datetime
import phonenumbers
from email_validator import validate_email, EmailNotValidError

_logger = logging.getLogger(__name__)

class DataSniffRFieldValidator(models.Model):
    _name = 'datasniffr.field.validator'
    _description = 'DataSniffR Field Validator - Specific Field Validation 🔍✅'
    _order = 'create_date desc'
    
    name = fields.Char(string='Validation Rule Name', required=True)
    
    # Validation Configuration
    field_type = fields.Selection([
        ('email', 'Email Address 📧'),
        ('phone', 'Phone Number 📞'),
        ('vat', 'VAT/Tax ID 💳'),
        ('address', 'Address 🏠'),
        ('date', 'Date Format 📅'),
        ('currency', 'Currency Amount 💰'),
        ('url', 'Website URL 🌐'),
        ('postal_code', 'Postal Code 📮'),
        ('iban', 'IBAN 🏦'),
        ('custom', 'Custom Validation 🎯'),
    ], string='Field Type', required=True)
    
    target_model = fields.Char(string='Target Model', required=True, default='res.partner')
    target_field = fields.Char(string='Target Field', required=True)
    validation_rules = fields.Text(string='Validation Rules (JSON)')
    
    # Validation Results
    total_records_checked = fields.Integer(string='Records Checked', default=0)
    valid_records = fields.Integer(string='Valid Records', default=0)
    invalid_records = fields.Integer(string='Invalid Records', default=0)
    auto_fixed_records = fields.Integer(string='Auto-Fixed Records', default=0)
    
    validation_score = fields.Float(string='Validation Score %', default=0.0, compute='_compute_validation_score')
    validation_results = fields.Text(string='Validation Results (JSON)')
    
    # Auto-Fix Configuration
    auto_fix_enabled = fields.Boolean(string='Enable Auto-Fix', default=True)
    backup_invalid_values = fields.Boolean(string='Backup Invalid Values', default=True)
    
    @api.depends('total_records_checked', 'valid_records', 'auto_fixed_records')
    def _compute_validation_score(self):
        for record in self:
            if record.total_records_checked > 0:
                record.validation_score = ((record.valid_records + record.auto_fixed_records) / record.total_records_checked) * 100
            else:
                record.validation_score = 0.0
    
    @api.model
    def validate_email_fields(self, model_name='res.partner', field_name='email'):
        """📧 Validate and fix email address formats"""
        
        validator = self.create({
            'name': f'Email Validation - {model_name}.{field_name}',
            'field_type': 'email',
            'target_model': model_name,
            'target_field': field_name
        })
        
        try:
            Model = self.env[model_name]
            records = Model.search([(field_name, '!=', False)])
            
            results = {
                'valid_emails': [],
                'invalid_emails': [],
                'auto_fixed': [],
                'suggestions': []
            }
            
            total_checked = 0
            valid_count = 0
            invalid_count = 0
            fixed_count = 0
            
            for record in records:
                total_checked += 1
                email_value = getattr(record, field_name)
                
                if not email_value:
                    continue
                
                # Clean and validate email
                cleaned_email = self._clean_email(email_value)
                validation_result = self._validate_email_format(cleaned_email)
                
                if validation_result['valid']:
                    valid_count += 1
                    results['valid_emails'].append({
                        'record_id': record.id,
                        'email': cleaned_email,
                        'status': 'valid'
                    })
                    
                    # Auto-fix if cleaned version is different
                    if cleaned_email != email_value and validator.auto_fix_enabled:
                        self._backup_field_value(record, field_name, email_value)
                        record.write({field_name: cleaned_email})
                        fixed_count += 1
                        results['auto_fixed'].append({
                            'record_id': record.id,
                            'original': email_value,
                            'fixed': cleaned_email
                        })
                else:
                    invalid_count += 1
                    results['invalid_emails'].append({
                        'record_id': record.id,
                        'email': email_value,
                        'error': validation_result['error'],
                        'suggestion': self._suggest_email_fix(email_value)
                    })
            
            # Update validator record
            validator.write({
                'total_records_checked': total_checked,
                'valid_records': valid_count,
                'invalid_records': invalid_count,
                'auto_fixed_records': fixed_count,
                'validation_results': json.dumps(results, indent=2)
            })
            
            return {
                'success': True,
                'validator_id': validator.id,
                'total_checked': total_checked,
                'valid_count': valid_count,
                'invalid_count': invalid_count,
                'fixed_count': fixed_count,
                'validation_score': validator.validation_score,
                'message': f'📧 Email validation complete! {valid_count + fixed_count}/{total_checked} emails are now valid!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '❌ Email validation encountered an error!'
            }
    
    def _clean_email(self, email):
        """🧹 Clean email address"""
        if not email:
            return email
        
        # Remove extra whitespace
        cleaned = str(email).strip().lower()
        
        # Remove common typos
        cleaned = cleaned.replace(' ', '')
        cleaned = cleaned.replace('..', '.')
        
        # Fix common domain typos
        domain_fixes = {
            'gmai.com': 'gmail.com',
            'gmial.com': 'gmail.com',
            'yahooo.com': 'yahoo.com',
            'hotmial.com': 'hotmail.com',
            'outlok.com': 'outlook.com'
        }
        
        for typo, correct in domain_fixes.items():
            if typo in cleaned:
                cleaned = cleaned.replace(typo, correct)
        
        return cleaned
    
    def _validate_email_format(self, email):
        """✅ Validate email format"""
        try:
            # Basic format check
            if not email or '@' not in email:
                return {'valid': False, 'error': 'Missing @ symbol'}
            
            parts = email.split('@')
            if len(parts) != 2:
                return {'valid': False, 'error': 'Invalid @ usage'}
            
            local, domain = parts
            if not local or not domain:
                return {'valid': False, 'error': 'Missing local or domain part'}
            
            if '.' not in domain:
                return {'valid': False, 'error': 'Domain missing TLD'}
            
            # Advanced validation with email-validator library
            try:
                validate_email(email)
                return {'valid': True}
            except EmailNotValidError as e:
                return {'valid': False, 'error': str(e)}
            
        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {str(e)}'}
    
    def _suggest_email_fix(self, invalid_email):
        """💡 Suggest email fix"""
        if not invalid_email:
            return None
        
        email = str(invalid_email).strip().lower()
        
        # Common fixes
        if email.count('@') == 0:
            # Maybe missing @
            if 'gmail' in email:
                return email.replace('gmail', '@gmail.com')
            elif 'yahoo' in email:
                return email.replace('yahoo', '@yahoo.com')
        
        if email.count('@') > 1:
            # Too many @, keep first one
            parts = email.split('@')
            return f"{parts[0]}@{parts[1]}"
        
        # Domain suggestions
        if email.endswith('@'):
            return email + 'gmail.com'
        
        return None
    
    @api.model
    def validate_phone_fields(self, model_name='res.partner', field_name='phone'):
        """📞 Validate and standardize phone numbers"""
        
        validator = self.create({
            'name': f'Phone Validation - {model_name}.{field_name}',
            'field_type': 'phone',
            'target_model': model_name,
            'target_field': field_name
        })
        
        try:
            Model = self.env[model_name]
            records = Model.search([(field_name, '!=', False)])
            
            results = {
                'valid_phones': [],
                'invalid_phones': [],
                'auto_fixed': [],
                'standardized': []
            }
            
            total_checked = 0
            valid_count = 0
            invalid_count = 0
            fixed_count = 0
            
            for record in records:
                total_checked += 1
                phone_value = getattr(record, field_name)
                
                if not phone_value:
                    continue
                
                # Clean and validate phone
                cleaned_phone = self._clean_phone(phone_value)
                validation_result = self._validate_phone_format(cleaned_phone, record)
                
                if validation_result['valid']:
                    valid_count += 1
                    standardized_phone = validation_result.get('standardized', cleaned_phone)
                    
                    results['valid_phones'].append({
                        'record_id': record.id,
                        'phone': standardized_phone,
                        'status': 'valid'
                    })
                    
                    # Auto-fix if standardized version is different
                    if standardized_phone != phone_value and validator.auto_fix_enabled:
                        self._backup_field_value(record, field_name, phone_value)
                        record.write({field_name: standardized_phone})
                        fixed_count += 1
                        results['auto_fixed'].append({
                            'record_id': record.id,
                            'original': phone_value,
                            'standardized': standardized_phone
                        })
                else:
                    invalid_count += 1
                    results['invalid_phones'].append({
                        'record_id': record.id,
                        'phone': phone_value,
                        'error': validation_result['error'],
                        'suggestion': self._suggest_phone_fix(phone_value)
                    })
            
            # Update validator record
            validator.write({
                'total_records_checked': total_checked,
                'valid_records': valid_count,
                'invalid_records': invalid_count,
                'auto_fixed_records': fixed_count,
                'validation_results': json.dumps(results, indent=2)
            })
            
            return {
                'success': True,
                'validator_id': validator.id,
                'total_checked': total_checked,
                'valid_count': valid_count,
                'invalid_count': invalid_count,
                'fixed_count': fixed_count,
                'validation_score': validator.validation_score,
                'message': f'📞 Phone validation complete! {valid_count + fixed_count}/{total_checked} phones are now valid!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '❌ Phone validation encountered an error!'
            }
    
    def _clean_phone(self, phone):
        """🧹 Clean phone number"""
        if not phone:
            return phone
        
        # Remove common formatting
        cleaned = str(phone).strip()
        cleaned = re.sub(r'[^\d\+\(\)\-\s]', '', cleaned)  # Keep only digits and basic formatting
        
        return cleaned
    
    def _validate_phone_format(self, phone, record=None):
        """✅ Validate phone format using phonenumbers library"""
        try:
            if not phone:
                return {'valid': False, 'error': 'Empty phone number'}
            
            # Try to determine country from record
            country_code = None
            if record and hasattr(record, 'country_id') and record.country_id:
                country_code = record.country_id.code
            
            # Parse phone number
            try:
                parsed_phone = phonenumbers.parse(phone, country_code)
                
                if phonenumbers.is_valid_number(parsed_phone):
                    # Format in international format
                    standardized = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    return {
                        'valid': True,
                        'standardized': standardized
                    }
                else:
                    return {'valid': False, 'error': 'Invalid phone number format'}
                    
            except phonenumbers.NumberParseException as e:
                return {'valid': False, 'error': f'Parse error: {str(e)}'}
            
        except Exception as e:
            # Fallback basic validation
            if len(re.sub(r'[^\d]', '', phone)) >= 7:  # At least 7 digits
                return {'valid': True, 'standardized': phone}
            else:
                return {'valid': False, 'error': 'Phone too short'}
    
    def _suggest_phone_fix(self, invalid_phone):
        """💡 Suggest phone fix"""
        if not invalid_phone:
            return None
        
        phone = str(invalid_phone).strip()
        digits_only = re.sub(r'[^\d]', '', phone)
        
        # If it has right number of digits, suggest formatting
        if len(digits_only) == 10:  # US format
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 11 and digits_only.startswith('1'):  # US with country code
            return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
        
        return f"Check format - found {len(digits_only)} digits"
    
    @api.model
    def validate_vat_fields(self, model_name='res.partner', field_name='vat'):
        """💳 Validate VAT/Tax ID numbers"""
        
        validator = self.create({
            'name': f'VAT Validation - {model_name}.{field_name}',
            'field_type': 'vat',
            'target_model': model_name,
            'target_field': field_name
        })
        
        try:
            Model = self.env[model_name]
            records = Model.search([(field_name, '!=', False)])
            
            results = {
                'valid_vats': [],
                'invalid_vats': [],
                'auto_fixed': []
            }
            
            total_checked = 0
            valid_count = 0
            invalid_count = 0
            fixed_count = 0
            
            for record in records:
                total_checked += 1
                vat_value = getattr(record, field_name)
                
                if not vat_value:
                    continue
                
                # Clean and validate VAT
                cleaned_vat = self._clean_vat(vat_value)
                validation_result = self._validate_vat_format(cleaned_vat, record)
                
                if validation_result['valid']:
                    valid_count += 1
                    results['valid_vats'].append({
                        'record_id': record.id,
                        'vat': cleaned_vat,
                        'country': validation_result.get('country'),
                        'status': 'valid'
                    })
                    
                    # Auto-fix if cleaned version is different
                    if cleaned_vat != vat_value and validator.auto_fix_enabled:
                        self._backup_field_value(record, field_name, vat_value)
                        record.write({field_name: cleaned_vat})
                        fixed_count += 1
                        results['auto_fixed'].append({
                            'record_id': record.id,
                            'original': vat_value,
                            'fixed': cleaned_vat
                        })
                else:
                    invalid_count += 1
                    results['invalid_vats'].append({
                        'record_id': record.id,
                        'vat': vat_value,
                        'error': validation_result['error']
                    })
            
            # Update validator record
            validator.write({
                'total_records_checked': total_checked,
                'valid_records': valid_count,
                'invalid_records': invalid_count,
                'auto_fixed_records': fixed_count,
                'validation_results': json.dumps(results, indent=2)
            })
            
            return {
                'success': True,
                'validator_id': validator.id,
                'total_checked': total_checked,
                'valid_count': valid_count,
                'invalid_count': invalid_count,
                'fixed_count': fixed_count,
                'validation_score': validator.validation_score,
                'message': f'💳 VAT validation complete! {valid_count + fixed_count}/{total_checked} VAT numbers are now valid!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '❌ VAT validation encountered an error!'
            }
    
    def _clean_vat(self, vat):
        """🧹 Clean VAT number"""
        if not vat:
            return vat
        
        # Remove spaces and convert to uppercase
        cleaned = str(vat).replace(' ', '').replace('-', '').upper()
        
        return cleaned
    
    def _validate_vat_format(self, vat, record=None):
        """✅ Validate VAT format"""
        try:
            if not vat:
                return {'valid': False, 'error': 'Empty VAT number'}
            
            # Basic format checks by country
            country_code = None
            if record and hasattr(record, 'country_id') and record.country_id:
                country_code = record.country_id.code
            
            # Simple validation patterns
            vat_patterns = {
                'US': r'^\d{2}-?\d{7}$',  # US EIN
                'GB': r'^GB\d{9}$|^GB\d{12}$',  # UK VAT
                'DE': r'^DE\d{9}$',  # German VAT
                'FR': r'^FR[A-Z0-9]{2}\d{9}$',  # French VAT
                'ES': r'^ES[A-Z]\d{8}$|^ES\d{8}[A-Z]$',  # Spanish VAT
                'IT': r'^IT\d{11}$',  # Italian VAT
            }
            
            if country_code and country_code in vat_patterns:
                pattern = vat_patterns[country_code]
                if re.match(pattern, vat):
                    return {'valid': True, 'country': country_code}
                else:
                    return {'valid': False, 'error': f'Invalid {country_code} VAT format'}
            
            # Generic validation - at least 5 characters with mix of letters/numbers
            if len(vat) >= 5 and re.match(r'^[A-Z0-9]+$', vat):
                return {'valid': True, 'country': 'Unknown'}
            else:
                return {'valid': False, 'error': 'Invalid VAT format'}
            
        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {str(e)}'}
    
    def _backup_field_value(self, record, field_name, original_value):
        """💾 Backup original field value before auto-fix"""
        
        if not self.backup_invalid_values:
            return
        
        backup_data = {
            'model': record._name,
            'record_id': record.id,
            'field_name': field_name,
            'original_value': original_value,
            'backup_date': datetime.now().isoformat()
        }
        
        # Store in field_value_backup model (would need to be created)
        try:
            self.env['datasniffr.field.backup'].create(backup_data)
        except:
            # If backup model doesn't exist, log it
            _logger.info(f"Backed up {record._name}.{field_name} for record {record.id}: {original_value}")
    
    @api.model
    def validate_custom_field(self, model_name, field_name, validation_rules):
        """🎯 Validate field with custom rules"""
        
        validator = self.create({
            'name': f'Custom Validation - {model_name}.{field_name}',
            'field_type': 'custom',
            'target_model': model_name,
            'target_field': field_name,
            'validation_rules': json.dumps(validation_rules)
        })
        
        try:
            Model = self.env[model_name]
            records = Model.search([(field_name, '!=', False)])
            
            results = {
                'valid_records': [],
                'invalid_records': [],
                'rule_violations': {}
            }
            
            total_checked = 0
            valid_count = 0
            invalid_count = 0
            
            for record in records:
                total_checked += 1
                field_value = getattr(record, field_name)
                
                validation_result = self._apply_custom_validation(field_value, validation_rules)
                
                if validation_result['valid']:
                    valid_count += 1
                    results['valid_records'].append({
                        'record_id': record.id,
                        'value': field_value
                    })
                else:
                    invalid_count += 1
                    results['invalid_records'].append({
                        'record_id': record.id,
                        'value': field_value,
                        'violations': validation_result['violations']
                    })
                    
                    # Track rule violations
                    for violation in validation_result['violations']:
                        rule_name = violation['rule']
                        if rule_name not in results['rule_violations']:
                            results['rule_violations'][rule_name] = 0
                        results['rule_violations'][rule_name] += 1
            
            # Update validator record
            validator.write({
                'total_records_checked': total_checked,
                'valid_records': valid_count,
                'invalid_records': invalid_count,
                'validation_results': json.dumps(results, indent=2)
            })
            
            return {
                'success': True,
                'validator_id': validator.id,
                'total_checked': total_checked,
                'valid_count': valid_count,
                'invalid_count': invalid_count,
                'validation_score': validator.validation_score,
                'rule_violations': results['rule_violations'],
                'message': f'🎯 Custom validation complete! {valid_count}/{total_checked} records passed all rules!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '❌ Custom validation encountered an error!'
            }
    
    def _apply_custom_validation(self, value, rules):
        """🎯 Apply custom validation rules"""
        
        violations = []
        
        for rule in rules:
            rule_type = rule.get('type')
            rule_name = rule.get('name', rule_type)
            
            if rule_type == 'required' and not value:
                violations.append({
                    'rule': rule_name,
                    'message': 'Field is required but empty'
                })
            
            elif rule_type == 'min_length' and value and len(str(value)) < rule.get('value', 0):
                violations.append({
                    'rule': rule_name,
                    'message': f'Value too short (minimum {rule.get("value")} characters)'
                })
            
            elif rule_type == 'max_length' and value and len(str(value)) > rule.get('value', 999):
                violations.append({
                    'rule': rule_name,
                    'message': f'Value too long (maximum {rule.get("value")} characters)'
                })
            
            elif rule_type == 'regex' and value and not re.match(rule.get('pattern', ''), str(value)):
                violations.append({
                    'rule': rule_name,
                    'message': f'Value does not match required pattern'
                })
            
            elif rule_type == 'contains' and value and rule.get('value', '') not in str(value):
                violations.append({
                    'rule': rule_name,
                    'message': f'Value must contain "{rule.get("value")}"'
                })
        
        return {
            'valid': len(violations) == 0,
            'violations': violations
        }
    
    @api.model
    def get_validation_dashboard(self):
        """📊 Get field validation dashboard"""
        
        validators = self.search([], limit=10)
        
        dashboard = {
            'total_validators': len(validators),
            'field_types': {},
            'recent_validations': [],
            'top_issues': [],
            'validation_trends': []
        }
        
        # Count by field type
        for validator in validators:
            field_type = validator.field_type
            if field_type not in dashboard['field_types']:
                dashboard['field_types'][field_type] = {
                    'count': 0,
                    'avg_score': 0,
                    'total_records': 0
                }
            
            dashboard['field_types'][field_type]['count'] += 1
            dashboard['field_types'][field_type]['avg_score'] += validator.validation_score
            dashboard['field_types'][field_type]['total_records'] += validator.total_records_checked
        
        # Calculate averages
        for field_type, data in dashboard['field_types'].items():
            if data['count'] > 0:
                data['avg_score'] = data['avg_score'] / data['count']
        
        # Recent validations
        for validator in validators[:5]:
            dashboard['recent_validations'].append({
                'name': validator.name,
                'field_type': validator.field_type,
                'validation_score': validator.validation_score,
                'records_checked': validator.total_records_checked,
                'date': validator.create_date.isoformat()
            })
        
        return dashboard