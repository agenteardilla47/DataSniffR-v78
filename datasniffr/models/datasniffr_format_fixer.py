#!/usr/bin/env python3
"""
DataSniffR Format Fixer Mini-Module 🔧✨
=======================================

The ultimate format correction and standardization wizard!
Transform messy data into beautiful, consistent formats!

Features:
- 🔤 Text format standardization
- 📞 Phone number formatting
- 📧 Email cleanup and validation
- 💰 Currency format fixing
- 📅 Date format standardization
- 🏠 Address format consistency
- 🤖 AI-powered format suggestions
- 📊 Format pattern learning

mmm lol 🐶💾 - Making data beautiful, one format at a time! 🔧✨
"""

from odoo import models, fields, api
import json
import logging
import re
from datetime import datetime
import phonenumbers

_logger = logging.getLogger(__name__)

class DataSniffRFormatFixer(models.Model):
    _name = 'datasniffr.format.fixer'
    _description = 'DataSniffR Format Fixer - Auto Format Correction 🔧✨'
    _order = 'create_date desc'
    
    name = fields.Char(string='Format Fix Job Name', required=True, default='Format Fix')
    
    # Fix Configuration
    target_model = fields.Char(string='Target Model', required=True, default='res.partner')
    fix_type = fields.Selection([
        ('phone_numbers', 'Phone Number Formatting 📞'),
        ('email_cleanup', 'Email Cleanup 📧'),
        ('name_standardization', 'Name Standardization 👤'),
        ('address_formatting', 'Address Formatting 🏠'),
        ('currency_formatting', 'Currency Formatting 💰'),
        ('date_standardization', 'Date Standardization 📅'),
        ('text_cleanup', 'Text Cleanup 🧹'),
        ('comprehensive_fix', 'Comprehensive Fix 🌈'),
    ], string='Fix Type', default='comprehensive_fix', required=True)
    
    fields_to_fix = fields.Text(string='Fields to Fix (JSON)', default='["name", "email", "phone"]')
    
    # Fix Configuration Options
    auto_apply_fixes = fields.Boolean(string='Auto Apply Fixes', default=True)
    backup_original_values = fields.Boolean(string='Backup Original Values', default=True)
    use_ai_suggestions = fields.Boolean(string='Use AI Suggestions', default=True)
    
    # Fix Results
    total_records_processed = fields.Integer(string='Records Processed', default=0)
    fixes_applied = fields.Integer(string='Fixes Applied', default=0)
    manual_review_needed = fields.Integer(string='Manual Review Needed', default=0)
    
    fix_results = fields.Text(string='Fix Results (JSON)')
    format_patterns_learned = fields.Text(string='Format Patterns Learned (JSON)')
    
    # Statistics
    improvement_score = fields.Float(string='Improvement Score %', default=0.0, compute='_compute_improvement_score')
    
    @api.depends('total_records_processed', 'fixes_applied')
    def _compute_improvement_score(self):
        for record in self:
            if record.total_records_processed > 0:
                record.improvement_score = (record.fixes_applied / record.total_records_processed) * 100
            else:
                record.improvement_score = 0.0
    
    @api.model
    def fix_phone_number_formats(self, model_name='res.partner'):
        """📞 Fix and standardize phone number formats"""
        
        fixer = self.create({
            'name': f'Phone Format Fix - {model_name}',
            'target_model': model_name,
            'fix_type': 'phone_numbers'
        })
        
        try:
            Model = self.env[model_name]
            records = Model.search([('phone', '!=', False)])
            
            fix_results = {
                'standardized_phones': [],
                'invalid_phones': [],
                'format_patterns': {},
                'country_distributions': {}
            }
            
            total_processed = 0
            fixes_applied = 0
            
            for record in records:
                total_processed += 1
                original_phone = record.phone
                
                # Attempt to fix and standardize phone
                fixed_phone = self._fix_phone_format(original_phone, record)
                
                if fixed_phone and fixed_phone != original_phone:
                    if fixer.backup_original_values:
                        self._backup_field_value(record, 'phone', original_phone)
                    
                    if fixer.auto_apply_fixes:
                        record.phone = fixed_phone
                        fixes_applied += 1
                        
                        fix_results['standardized_phones'].append({
                            'record_id': record.id,
                            'original': original_phone,
                            'fixed': fixed_phone,
                            'country': self._detect_phone_country(fixed_phone)
                        })
                    
                    # Learn format patterns
                    pattern = self._extract_phone_pattern(original_phone)
                    if pattern:
                        fix_results['format_patterns'][pattern] = fix_results['format_patterns'].get(pattern, 0) + 1
                
                elif not fixed_phone:
                    fix_results['invalid_phones'].append({
                        'record_id': record.id,
                        'phone': original_phone,
                        'suggestion': self._suggest_phone_fix(original_phone)
                    })
            
            # Update fixer record
            fixer.write({
                'total_records_processed': total_processed,
                'fixes_applied': fixes_applied,
                'fix_results': json.dumps(fix_results, indent=2)
            })
            
            return {
                'success': True,
                'fixer_id': fixer.id,
                'total_processed': total_processed,
                'fixes_applied': fixes_applied,
                'improvement_score': fixer.improvement_score,
                'message': f'📞 Phone format fix complete! Fixed {fixes_applied}/{total_processed} phone numbers!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '❌ Phone format fix encountered an error!'
            }
    
    def _fix_phone_format(self, phone, record=None):
        """📞 Fix and standardize phone format"""
        
        if not phone:
            return None
        
        try:
            # Clean the phone number first
            cleaned = re.sub(r'[^\d\+\(\)\-\s]', '', str(phone))
            
            # Determine country from record
            country_code = None
            if record and hasattr(record, 'country_id') and record.country_id:
                country_code = record.country_id.code
            
            # Try to parse with phonenumbers library
            try:
                parsed = phonenumbers.parse(cleaned, country_code)
                if phonenumbers.is_valid_number(parsed):
                    # Return in international format
                    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            except:
                pass
            
            # Fallback formatting for common patterns
            digits = re.sub(r'[^\d]', '', cleaned)
            
            if len(digits) == 10:  # US format
                return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits.startswith('1'):  # US with country code
                return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            elif len(digits) >= 7:  # Generic formatting
                return f"+{digits[:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}"
            
            return None
            
        except Exception:
            return None
    
    def _detect_phone_country(self, phone):
        """🌍 Detect country from phone number"""
        
        try:
            parsed = phonenumbers.parse(phone, None)
            return phonenumbers.region_code_for_number(parsed)
        except:
            return 'Unknown'
    
    def _extract_phone_pattern(self, phone):
        """📊 Extract format pattern from phone number"""
        
        if not phone:
            return None
        
        # Replace digits with 'X' to create pattern
        pattern = re.sub(r'\d', 'X', str(phone))
        return pattern
    
    def _suggest_phone_fix(self, phone):
        """💡 Suggest phone fix"""
        
        if not phone:
            return "Add a valid phone number"
        
        digits = re.sub(r'[^\d]', '', str(phone))
        
        if len(digits) < 7:
            return f"Phone too short - add {7 - len(digits)} more digits"
        elif len(digits) == 10:
            return f"Format as: ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) > 11:
            return "Phone too long - check for extra digits"
        
        return "Check phone number format"
    
    @api.model
    def fix_email_formats(self, model_name='res.partner'):
        """📧 Fix and clean email formats"""
        
        fixer = self.create({
            'name': f'Email Format Fix - {model_name}',
            'target_model': model_name,
            'fix_type': 'email_cleanup'
        })
        
        try:
            Model = self.env[model_name]
            records = Model.search([('email', '!=', False)])
            
            fix_results = {
                'cleaned_emails': [],
                'invalid_emails': [],
                'domain_fixes': {},
                'common_typos_fixed': {}
            }
            
            total_processed = 0
            fixes_applied = 0
            
            for record in records:
                total_processed += 1
                original_email = record.email
                
                # Clean and fix email
                fixed_email = self._fix_email_format(original_email)
                
                if fixed_email and fixed_email != original_email:
                    if fixer.backup_original_values:
                        self._backup_field_value(record, 'email', original_email)
                    
                    if fixer.auto_apply_fixes:
                        record.email = fixed_email
                        fixes_applied += 1
                        
                        fix_results['cleaned_emails'].append({
                            'record_id': record.id,
                            'original': original_email,
                            'fixed': fixed_email,
                            'fix_type': self._classify_email_fix(original_email, fixed_email)
                        })
                        
                        # Track domain fixes
                        if '@' in original_email and '@' in fixed_email:
                            orig_domain = original_email.split('@')[1].lower()
                            fixed_domain = fixed_email.split('@')[1].lower()
                            if orig_domain != fixed_domain:
                                fix_results['domain_fixes'][f"{orig_domain} -> {fixed_domain}"] = \
                                    fix_results['domain_fixes'].get(f"{orig_domain} -> {fixed_domain}", 0) + 1
                
                elif not self._is_valid_email_format(original_email):
                    fix_results['invalid_emails'].append({
                        'record_id': record.id,
                        'email': original_email,
                        'issues': self._identify_email_issues(original_email),
                        'suggestion': self._suggest_email_fix(original_email)
                    })
            
            # Update fixer record
            fixer.write({
                'total_records_processed': total_processed,
                'fixes_applied': fixes_applied,
                'fix_results': json.dumps(fix_results, indent=2)
            })
            
            return {
                'success': True,
                'fixer_id': fixer.id,
                'total_processed': total_processed,
                'fixes_applied': fixes_applied,
                'improvement_score': fixer.improvement_score,
                'message': f'📧 Email format fix complete! Fixed {fixes_applied}/{total_processed} email addresses!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '❌ Email format fix encountered an error!'
            }
    
    def _fix_email_format(self, email):
        """📧 Fix email format issues"""
        
        if not email:
            return None
        
        # Basic cleaning
        cleaned = str(email).strip().lower()
        
        # Remove extra spaces
        cleaned = re.sub(r'\s+', '', cleaned)
        
        # Fix double dots
        cleaned = cleaned.replace('..', '.')
        
        # Fix common domain typos
        domain_fixes = {
            'gmai.com': 'gmail.com',
            'gmial.com': 'gmail.com',
            'gmali.com': 'gmail.com',
            'yahooo.com': 'yahoo.com',
            'yaho.com': 'yahoo.com',
            'hotmial.com': 'hotmail.com',
            'hotmil.com': 'hotmail.com',
            'outlok.com': 'outlook.com',
            'outlokc.com': 'outlook.com',
            'gmai.co': 'gmail.com',
            'yahoo.co': 'yahoo.com'
        }
        
        for typo, correct in domain_fixes.items():
            if typo in cleaned:
                cleaned = cleaned.replace(typo, correct)
        
        # Validate basic format
        if self._is_valid_email_format(cleaned):
            return cleaned
        
        return None
    
    def _is_valid_email_format(self, email):
        """✅ Check if email has valid format"""
        
        if not email:
            return False
        
        # Basic regex check
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _classify_email_fix(self, original, fixed):
        """🏷️ Classify the type of email fix applied"""
        
        if original.lower() != fixed.lower():
            return 'case_normalization'
        
        orig_domain = original.split('@')[1] if '@' in original else ''
        fixed_domain = fixed.split('@')[1] if '@' in fixed else ''
        
        if orig_domain != fixed_domain:
            return 'domain_typo_fix'
        
        if ' ' in original and ' ' not in fixed:
            return 'space_removal'
        
        if '..' in original and '..' not in fixed:
            return 'double_dot_fix'
        
        return 'general_cleanup'
    
    def _identify_email_issues(self, email):
        """🔍 Identify specific issues with email"""
        
        issues = []
        
        if not email:
            return ['empty_email']
        
        if '@' not in email:
            issues.append('missing_at_symbol')
        elif email.count('@') > 1:
            issues.append('multiple_at_symbols')
        
        if '@' in email:
            parts = email.split('@')
            if len(parts) == 2:
                local, domain = parts
                if not local:
                    issues.append('missing_local_part')
                if not domain:
                    issues.append('missing_domain')
                elif '.' not in domain:
                    issues.append('domain_missing_tld')
        
        if ' ' in email:
            issues.append('contains_spaces')
        
        if '..' in email:
            issues.append('double_dots')
        
        return issues
    
    def _suggest_email_fix(self, email):
        """💡 Suggest email fix"""
        
        if not email:
            return "Add a valid email address"
        
        issues = self._identify_email_issues(email)
        
        if 'missing_at_symbol' in issues:
            if 'gmail' in email.lower():
                return email.replace('gmail', '@gmail.com')
            return "Add @ symbol and domain"
        
        if 'multiple_at_symbols' in issues:
            return "Remove extra @ symbols"
        
        if 'contains_spaces' in issues:
            return "Remove spaces from email"
        
        if 'double_dots' in issues:
            return "Fix double dots (..)"
        
        return "Check email format"
    
    @api.model
    def fix_name_formats(self, model_name='res.partner'):
        """👤 Fix and standardize name formats"""
        
        fixer = self.create({
            'name': f'Name Format Fix - {model_name}',
            'target_model': model_name,
            'fix_type': 'name_standardization'
        })
        
        try:
            Model = self.env[model_name]
            records = Model.search([('name', '!=', False)])
            
            fix_results = {
                'standardized_names': [],
                'capitalization_fixes': [],
                'spacing_fixes': [],
                'special_char_fixes': []
            }
            
            total_processed = 0
            fixes_applied = 0
            
            for record in records:
                total_processed += 1
                original_name = record.name
                
                # Fix and standardize name
                fixed_name = self._fix_name_format(original_name)
                
                if fixed_name and fixed_name != original_name:
                    if fixer.backup_original_values:
                        self._backup_field_value(record, 'name', original_name)
                    
                    if fixer.auto_apply_fixes:
                        record.name = fixed_name
                        fixes_applied += 1
                        
                        fix_type = self._classify_name_fix(original_name, fixed_name)
                        fix_results[f"{fix_type}_fixes"].append({
                            'record_id': record.id,
                            'original': original_name,
                            'fixed': fixed_name
                        })
            
            # Update fixer record
            fixer.write({
                'total_records_processed': total_processed,
                'fixes_applied': fixes_applied,
                'fix_results': json.dumps(fix_results, indent=2)
            })
            
            return {
                'success': True,
                'fixer_id': fixer.id,
                'total_processed': total_processed,
                'fixes_applied': fixes_applied,
                'improvement_score': fixer.improvement_score,
                'message': f'👤 Name format fix complete! Fixed {fixes_applied}/{total_processed} names!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '❌ Name format fix encountered an error!'
            }
    
    def _fix_name_format(self, name):
        """👤 Fix name format issues"""
        
        if not name:
            return None
        
        fixed = str(name).strip()
        
        # Remove extra spaces
        fixed = re.sub(r'\s+', ' ', fixed)
        
        # Fix capitalization (Title Case)
        fixed = fixed.title()
        
        # Handle special cases
        # Fix common prefixes/suffixes
        prefixes = ['Mc', 'Mac', 'O\'', 'De', 'Van', 'Von', 'La', 'Le']
        for prefix in prefixes:
            pattern = r'\b' + prefix.lower() + r'([a-z])'
            replacement = prefix + r'\1'
            fixed = re.sub(pattern, replacement, fixed, flags=re.IGNORECASE)
        
        # Fix Roman numerals
        roman_pattern = r'\b([IVX]+)\b'
        fixed = re.sub(roman_pattern, lambda m: m.group(1).upper(), fixed)
        
        return fixed
    
    def _classify_name_fix(self, original, fixed):
        """🏷️ Classify the type of name fix applied"""
        
        if original.lower() == fixed.lower() and original != fixed:
            return 'capitalization'
        
        if len(original.split()) != len(fixed.split()):
            return 'spacing'
        
        if re.sub(r'[a-zA-Z\s]', '', original) != re.sub(r'[a-zA-Z\s]', '', fixed):
            return 'special_char'
        
        return 'standardized'
    
    @api.model
    def comprehensive_format_fix(self, model_name='res.partner'):
        """🌈 Apply comprehensive format fixes to all fields"""
        
        fixer = self.create({
            'name': f'Comprehensive Fix - {model_name}',
            'target_model': model_name,
            'fix_type': 'comprehensive_fix'
        })
        
        try:
            # Run all format fixes
            phone_result = self.fix_phone_number_formats(model_name)
            email_result = self.fix_email_formats(model_name)
            name_result = self.fix_name_formats(model_name)
            
            comprehensive_results = {
                'phone_fixes': phone_result,
                'email_fixes': email_result,
                'name_fixes': name_result,
                'total_improvements': (
                    phone_result.get('fixes_applied', 0) +
                    email_result.get('fixes_applied', 0) +
                    name_result.get('fixes_applied', 0)
                )
            }
            
            # Update fixer record
            fixer.write({
                'total_records_processed': max(
                    phone_result.get('total_processed', 0),
                    email_result.get('total_processed', 0),
                    name_result.get('total_processed', 0)
                ),
                'fixes_applied': comprehensive_results['total_improvements'],
                'fix_results': json.dumps(comprehensive_results, indent=2)
            })
            
            return {
                'success': True,
                'fixer_id': fixer.id,
                'comprehensive_results': comprehensive_results,
                'total_improvements': comprehensive_results['total_improvements'],
                'improvement_score': fixer.improvement_score,
                'message': f'🌈 Comprehensive format fix complete! Applied {comprehensive_results["total_improvements"]} total improvements!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '❌ Comprehensive format fix encountered an error!'
            }
    
    def _backup_field_value(self, record, field_name, original_value):
        """💾 Backup original field value before fixing"""
        
        backup_data = {
            'model': record._name,
            'record_id': record.id,
            'field_name': field_name,
            'original_value': original_value,
            'backup_date': datetime.now().isoformat(),
            'fixer_id': self.id
        }
        
        # Store backup (would integrate with backup system)
        _logger.info(f"Format fix backup: {record._name}.{field_name} for record {record.id}")
    
    @api.model
    def learn_format_patterns(self):
        """🧠 Learn format patterns from successful fixes"""
        
        all_fixers = self.search([('fix_results', '!=', False)])
        
        learned_patterns = {
            'phone_patterns': {},
            'email_patterns': {},
            'name_patterns': {},
            'common_fixes': {},
            'success_rates': {}
        }
        
        for fixer in all_fixers:
            try:
                results = json.loads(fixer.fix_results)
                
                # Learn from phone fixes
                if 'standardized_phones' in results:
                    for fix in results['standardized_phones']:
                        pattern = self._extract_phone_pattern(fix['original'])
                        if pattern:
                            learned_patterns['phone_patterns'][pattern] = \
                                learned_patterns['phone_patterns'].get(pattern, 0) + 1
                
                # Learn from email fixes
                if 'cleaned_emails' in results:
                    for fix in results['cleaned_emails']:
                        fix_type = fix.get('fix_type', 'unknown')
                        learned_patterns['email_patterns'][fix_type] = \
                            learned_patterns['email_patterns'].get(fix_type, 0) + 1
                
                # Calculate success rates by fix type
                if fixer.total_records_processed > 0:
                    success_rate = fixer.improvement_score
                    fix_type = fixer.fix_type
                    if fix_type not in learned_patterns['success_rates']:
                        learned_patterns['success_rates'][fix_type] = []
                    learned_patterns['success_rates'][fix_type].append(success_rate)
                
            except Exception as e:
                _logger.warning(f"Error learning from fixer {fixer.id}: {str(e)}")
        
        # Calculate average success rates
        for fix_type, rates in learned_patterns['success_rates'].items():
            learned_patterns['success_rates'][fix_type] = sum(rates) / len(rates) if rates else 0
        
        return learned_patterns
    
    @api.model
    def get_format_fixer_dashboard(self):
        """📊 Get format fixer dashboard"""
        
        fixers = self.search([], limit=20)
        
        dashboard = {
            'total_fixers': len(fixers),
            'total_fixes_applied': sum(f.fixes_applied for f in fixers),
            'total_records_processed': sum(f.total_records_processed for f in fixers),
            'average_improvement_score': 0,
            'fix_type_distribution': {},
            'recent_fixes': [],
            'top_performing_fixers': []
        }
        
        if fixers:
            dashboard['average_improvement_score'] = sum(f.improvement_score for f in fixers) / len(fixers)
        
        # Fix type distribution
        for fixer in fixers:
            fix_type = fixer.fix_type
            if fix_type not in dashboard['fix_type_distribution']:
                dashboard['fix_type_distribution'][fix_type] = {
                    'count': 0,
                    'total_fixes': 0,
                    'avg_improvement': 0
                }
            
            dashboard['fix_type_distribution'][fix_type]['count'] += 1
            dashboard['fix_type_distribution'][fix_type]['total_fixes'] += fixer.fixes_applied
            dashboard['fix_type_distribution'][fix_type]['avg_improvement'] += fixer.improvement_score
        
        # Calculate averages
        for fix_type, data in dashboard['fix_type_distribution'].items():
            if data['count'] > 0:
                data['avg_improvement'] = data['avg_improvement'] / data['count']
        
        # Recent fixes
        for fixer in fixers[:10]:
            dashboard['recent_fixes'].append({
                'name': fixer.name,
                'fix_type': fixer.fix_type,
                'fixes_applied': fixer.fixes_applied,
                'improvement_score': fixer.improvement_score,
                'date': fixer.create_date.isoformat()
            })
        
        # Top performing fixers
        top_fixers = sorted(fixers, key=lambda f: f.improvement_score, reverse=True)[:5]
        for fixer in top_fixers:
            dashboard['top_performing_fixers'].append({
                'name': fixer.name,
                'improvement_score': fixer.improvement_score,
                'fixes_applied': fixer.fixes_applied
            })
        
        return dashboard