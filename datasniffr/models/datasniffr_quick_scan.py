#!/usr/bin/env python3
"""
DataSniffR Quick Scan Mini-Module ⚡🔍
====================================

Lightning-fast basic scans for when you need results NOW!
The speediest data quality checks in the universe!

Features:
- ⚡ 10-second basic health checks
- 🎯 Essential problem detection
- 📊 Instant overview dashboard
- 🚨 Critical issue alerts
- 🎮 Quick boss battle challenges
- 📱 Mobile-friendly results

mmm lol 🐶💾 - Speed of light data scanning! ⚡✨
"""

from odoo import models, fields, api
import json
import logging
from datetime import datetime
import time

_logger = logging.getLogger(__name__)

class DataSniffRQuickScan(models.Model):
    _name = 'datasniffr.quick.scan'
    _description = 'DataSniffR Quick Scan - Lightning Fast Basic Scans ⚡🔍'
    _order = 'create_date desc'
    
    name = fields.Char(string='Quick Scan Name', required=True, default='Lightning Scan')
    
    # Scan Configuration
    scan_type = fields.Selection([
        ('health_check', 'Health Check ❤️'),
        ('critical_scan', 'Critical Issues Only 🚨'),
        ('duplicate_hunt', 'Quick Duplicate Hunt 👥'),
        ('format_check', 'Format Validation 🔤'),
        ('relationship_scan', 'Relationship Check 🔗'),
        ('security_sweep', 'Security Sweep 🛡️'),
        ('performance_check', 'Performance Check 🚀'),
        ('full_lightning', 'Full Lightning Scan ⚡'),
    ], string='Scan Type', default='health_check', required=True)
    
    target_models = fields.Text(string='Target Models (JSON)', default='["res.partner", "sale.order", "product.template"]')
    max_records_per_model = fields.Integer(string='Max Records Per Model', default=1000)
    time_limit_seconds = fields.Integer(string='Time Limit (seconds)', default=10)
    
    # Scan Results
    scan_status = fields.Selection([
        ('pending', 'Pending ⏳'),
        ('running', 'Running 🏃‍♂️'),
        ('completed', 'Completed ✅'),
        ('timeout', 'Timeout ⏰'),
        ('error', 'Error ❌'),
    ], string='Scan Status', default='pending')
    
    scan_duration = fields.Float(string='Scan Duration (seconds)', default=0.0)
    total_records_scanned = fields.Integer(string='Total Records Scanned', default=0)
    issues_found = fields.Integer(string='Issues Found', default=0)
    critical_issues = fields.Integer(string='Critical Issues', default=0)
    
    # Quick Results Summary
    health_score = fields.Float(string='Health Score %', default=0.0)
    scan_results = fields.Text(string='Quick Results (JSON)')
    recommendations = fields.Text(string='Quick Recommendations (JSON)')
    
    # Boss Battle Integration
    boss_battle_triggered = fields.Boolean(string='Boss Battle Triggered', default=False)
    battle_challenge = fields.Text(string='Battle Challenge (JSON)')
    
    @api.model
    def run_lightning_health_check(self):
        """❤️ Lightning-fast health check in under 10 seconds"""
        
        start_time = time.time()
        scan_record = self.create({
            'name': f'Health Check - {datetime.now().strftime("%H:%M:%S")}',
            'scan_type': 'health_check',
            'scan_status': 'running'
        })
        
        try:
            results = {
                'models_checked': [],
                'critical_issues': [],
                'warnings': [],
                'health_metrics': {},
                'quick_stats': {}
            }
            
            # Quick model health checks
            target_models = ['res.partner', 'sale.order', 'product.template', 'account.move']
            total_issues = 0
            critical_count = 0
            
            for model_name in target_models:
                if time.time() - start_time > 8:  # Leave 2 seconds buffer
                    break
                    
                model_results = self._quick_model_check(model_name)
                results['models_checked'].append(model_results)
                
                total_issues += model_results.get('issues_count', 0)
                critical_count += model_results.get('critical_count', 0)
                
                results['quick_stats'][model_name] = {
                    'total_records': model_results.get('total_records', 0),
                    'issues_found': model_results.get('issues_count', 0),
                    'health_score': model_results.get('health_score', 100)
                }
            
            # Calculate overall health score
            overall_health = max(0, 100 - (total_issues * 2) - (critical_count * 10))
            
            # Generate quick recommendations
            recommendations = self._generate_quick_recommendations(results)
            
            # Check if boss battle should be triggered
            boss_battle = self._check_boss_battle_trigger(total_issues, critical_count)
            
            scan_duration = time.time() - start_time
            
            # Update scan record
            scan_record.write({
                'scan_status': 'completed',
                'scan_duration': scan_duration,
                'issues_found': total_issues,
                'critical_issues': critical_count,
                'health_score': overall_health,
                'scan_results': json.dumps(results, indent=2),
                'recommendations': json.dumps(recommendations, indent=2),
                'boss_battle_triggered': boss_battle.get('triggered', False),
                'battle_challenge': json.dumps(boss_battle, indent=2) if boss_battle.get('triggered') else None
            })
            
            return {
                'success': True,
                'scan_id': scan_record.id,
                'duration': scan_duration,
                'health_score': overall_health,
                'issues_found': total_issues,
                'critical_issues': critical_count,
                'message': f'⚡ Lightning scan completed in {scan_duration:.2f} seconds!',
                'boss_battle_triggered': boss_battle.get('triggered', False)
            }
            
        except Exception as e:
            scan_record.write({
                'scan_status': 'error',
                'scan_duration': time.time() - start_time
            })
            
            return {
                'success': False,
                'error': str(e),
                'message': '❌ Quick scan encountered an error!'
            }
    
    def _quick_model_check(self, model_name):
        """🔍 Quick health check for a specific model"""
        
        try:
            Model = self.env[model_name]
            
            # Quick record count
            total_records = Model.search_count([])
            if total_records == 0:
                return {
                    'model': model_name,
                    'total_records': 0,
                    'issues_count': 0,
                    'critical_count': 0,
                    'health_score': 100,
                    'status': 'empty'
                }
            
            # Sample records for quick check (max 100)
            sample_size = min(100, total_records)
            sample_records = Model.search([], limit=sample_size)
            
            issues = []
            critical_issues = []
            
            # Quick checks
            for record in sample_records:
                # Check for missing required fields
                if hasattr(record, 'name') and not record.name:
                    issues.append('Missing name field')
                    
                if hasattr(record, 'email') and record.email and '@' not in str(record.email):
                    critical_issues.append('Invalid email format')
                    
                if hasattr(record, 'phone') and record.phone and len(str(record.phone).replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) < 7:
                    issues.append('Invalid phone format')
            
            issues_count = len(issues)
            critical_count = len(critical_issues)
            
            # Calculate health score for this model
            health_score = max(0, 100 - (issues_count * 5) - (critical_count * 15))
            
            return {
                'model': model_name,
                'total_records': total_records,
                'sample_size': sample_size,
                'issues_count': issues_count,
                'critical_count': critical_count,
                'health_score': health_score,
                'issues': issues[:5],  # Top 5 issues
                'critical_issues': critical_issues[:3]  # Top 3 critical
            }
            
        except Exception as e:
            return {
                'model': model_name,
                'total_records': 0,
                'issues_count': 1,
                'critical_count': 1,
                'health_score': 0,
                'error': str(e)
            }
    
    def _generate_quick_recommendations(self, results):
        """💡 Generate lightning-fast recommendations"""
        
        recommendations = {
            'immediate_actions': [],
            'quick_fixes': [],
            'boss_battles': [],
            'celebration_worthy': []
        }
        
        total_issues = sum(model.get('issues_count', 0) for model in results['models_checked'])
        critical_issues = sum(model.get('critical_count', 0) for model in results['models_checked'])
        
        if critical_issues > 0:
            recommendations['immediate_actions'].append({
                'action': 'Fix Critical Issues',
                'description': f'🚨 {critical_issues} critical issues need immediate attention!',
                'priority': 'URGENT',
                'estimated_time': '15 minutes'
            })
        
        if total_issues > 10:
            recommendations['boss_battles'].append({
                'battle': 'Data Quality Dragon',
                'description': f'⚔️ Challenge your team to fix {total_issues} issues!',
                'reward': '100 DataSniffR points per issue fixed'
            })
        
        if total_issues < 5:
            recommendations['celebration_worthy'].append({
                'achievement': 'Data Quality Champion',
                'description': '🏆 Your data quality is excellent! Time to celebrate!',
                'suggestion': 'Share your success with the team!'
            })
        
        # Model-specific recommendations
        for model_data in results['models_checked']:
            if model_data.get('health_score', 100) < 80:
                recommendations['quick_fixes'].append({
                    'model': model_data['model'],
                    'action': f"Quick cleanup for {model_data['model']}",
                    'description': f"Health score: {model_data.get('health_score', 0):.1f}%",
                    'time_estimate': '5 minutes'
                })
        
        return recommendations
    
    def _check_boss_battle_trigger(self, total_issues, critical_issues):
        """⚔️ Check if conditions warrant a boss battle"""
        
        battle = {'triggered': False}
        
        if critical_issues >= 5:
            battle = {
                'triggered': True,
                'battle_type': 'Critical Crisis Dragon',
                'description': f'🐉 {critical_issues} critical issues detected! All hands on deck!',
                'team_challenge': 'Fix all critical issues in 30 minutes',
                'reward_points': critical_issues * 50,
                'celebration': 'Victory dance when completed!'
            }
        elif total_issues >= 20:
            battle = {
                'triggered': True,
                'battle_type': 'Data Quality Hydra',
                'description': f'🐍 {total_issues} issues detected! Time for team collaboration!',
                'team_challenge': 'Each team member fixes 5 issues',
                'reward_points': total_issues * 10,
                'celebration': 'Team high-fives all around!'
            }
        
        return battle
    
    @api.model
    def run_critical_issues_scan(self):
        """🚨 Ultra-fast critical issues detection"""
        
        start_time = time.time()
        
        critical_checks = [
            self._check_duplicate_customers(),
            self._check_invalid_emails(),
            self._check_missing_required_fields(),
            self._check_broken_relationships(),
            self._check_security_issues()
        ]
        
        critical_issues = []
        for check in critical_checks:
            if check['issues_found'] > 0:
                critical_issues.extend(check['issues'])
        
        scan_duration = time.time() - start_time
        
        return {
            'success': True,
            'scan_type': 'critical_scan',
            'duration': scan_duration,
            'critical_issues': len(critical_issues),
            'issues': critical_issues[:10],  # Top 10 most critical
            'message': f'🚨 Found {len(critical_issues)} critical issues in {scan_duration:.2f} seconds!'
        }
    
    def _check_duplicate_customers(self):
        """👥 Quick duplicate customer check"""
        
        # Simple duplicate detection based on email
        partners = self.env['res.partner'].search([('email', '!=', False)], limit=500)
        
        email_counts = {}
        duplicates = []
        
        for partner in partners:
            email = partner.email.lower().strip()
            if email in email_counts:
                duplicates.append({
                    'type': 'duplicate_customer',
                    'description': f'Duplicate email: {email}',
                    'records': [email_counts[email], partner.id],
                    'severity': 'high'
                })
            else:
                email_counts[email] = partner.id
        
        return {
            'check': 'duplicate_customers',
            'issues_found': len(duplicates),
            'issues': duplicates
        }
    
    def _check_invalid_emails(self):
        """📧 Quick invalid email detection"""
        
        partners = self.env['res.partner'].search([('email', '!=', False)], limit=500)
        
        invalid_emails = []
        for partner in partners:
            email = partner.email
            if email and ('@' not in email or '.' not in email.split('@')[-1]):
                invalid_emails.append({
                    'type': 'invalid_email',
                    'description': f'Invalid email format: {email}',
                    'record_id': partner.id,
                    'severity': 'critical'
                })
        
        return {
            'check': 'invalid_emails',
            'issues_found': len(invalid_emails),
            'issues': invalid_emails
        }
    
    def _check_missing_required_fields(self):
        """❗ Quick missing required fields check"""
        
        # Check partners without names
        partners_no_name = self.env['res.partner'].search([('name', 'in', [False, ''])], limit=100)
        
        missing_fields = []
        for partner in partners_no_name:
            missing_fields.append({
                'type': 'missing_required_field',
                'description': 'Customer without name',
                'record_id': partner.id,
                'field': 'name',
                'severity': 'high'
            })
        
        return {
            'check': 'missing_required_fields',
            'issues_found': len(missing_fields),
            'issues': missing_fields
        }
    
    def _check_broken_relationships(self):
        """🔗 Quick relationship integrity check"""
        
        # Check sale orders without customers
        orders_no_customer = self.env['sale.order'].search([('partner_id', '=', False)], limit=50)
        
        broken_relationships = []
        for order in orders_no_customer:
            broken_relationships.append({
                'type': 'broken_relationship',
                'description': 'Sale order without customer',
                'record_id': order.id,
                'severity': 'critical'
            })
        
        return {
            'check': 'broken_relationships',
            'issues_found': len(broken_relationships),
            'issues': broken_relationships
        }
    
    def _check_security_issues(self):
        """🛡️ Quick security check"""
        
        # Check for users with excessive permissions (simplified)
        admin_users = self.env['res.users'].search([('groups_id', 'in', [self.env.ref('base.group_system').id])], limit=20)
        
        security_issues = []
        if len(admin_users) > 5:
            security_issues.append({
                'type': 'security_risk',
                'description': f'{len(admin_users)} users have admin privileges',
                'severity': 'medium',
                'recommendation': 'Review admin user permissions'
            })
        
        return {
            'check': 'security_issues',
            'issues_found': len(security_issues),
            'issues': security_issues
        }
    
    @api.model
    def get_quick_scan_dashboard(self):
        """📊 Get instant dashboard data for mobile/quick view"""
        
        recent_scans = self.search([], limit=5)
        
        dashboard = {
            'last_scan': None,
            'health_trend': [],
            'quick_stats': {
                'total_scans_today': 0,
                'average_health_score': 0,
                'issues_fixed_today': 0,
                'boss_battles_triggered': 0
            },
            'urgent_actions': [],
            'celebration_moments': []
        }
        
        if recent_scans:
            latest_scan = recent_scans[0]
            dashboard['last_scan'] = {
                'id': latest_scan.id,
                'name': latest_scan.name,
                'health_score': latest_scan.health_score,
                'issues_found': latest_scan.issues_found,
                'duration': latest_scan.scan_duration,
                'status': latest_scan.scan_status
            }
            
            # Health trend from recent scans
            for scan in recent_scans:
                dashboard['health_trend'].append({
                    'timestamp': scan.create_date.isoformat(),
                    'health_score': scan.health_score,
                    'issues_count': scan.issues_found
                })
        
        # Quick stats (would be calculated from actual data)
        today_scans = self.search([('create_date', '>=', datetime.now().strftime('%Y-%m-%d 00:00:00'))])
        dashboard['quick_stats']['total_scans_today'] = len(today_scans)
        
        if today_scans:
            dashboard['quick_stats']['average_health_score'] = sum(scan.health_score for scan in today_scans) / len(today_scans)
            dashboard['quick_stats']['boss_battles_triggered'] = sum(1 for scan in today_scans if scan.boss_battle_triggered)
        
        return dashboard
    
    def trigger_quick_boss_battle(self):
        """⚔️ Trigger an instant boss battle based on scan results"""
        
        if not self.boss_battle_triggered:
            return {'error': 'No boss battle conditions met'}
        
        battle_data = json.loads(self.battle_challenge or '{}')
        
        # Create boss battle record (integrate with boss_battle_task_distributor)
        boss_battle = self.env['boss.battle.task.distributor'].create_lightning_battle({
            'battle_type': battle_data.get('battle_type', 'Quick Data Challenge'),
            'description': battle_data.get('description', 'Lightning-fast data quality challenge!'),
            'target_issues': self.issues_found,
            'time_limit': 30,  # 30 minute lightning battle
            'reward_points': battle_data.get('reward_points', 100),
            'source_scan_id': self.id
        })
        
        return {
            'success': True,
            'battle_id': boss_battle.id,
            'message': f"⚔️ {battle_data.get('battle_type', 'Lightning Battle')} has begun!",
            'challenge': battle_data.get('team_challenge', 'Fix data quality issues!'),
            'reward': f"{battle_data.get('reward_points', 100)} points available!"
        }
    
    @api.model
    def run_mobile_friendly_scan(self):
        """📱 Ultra-light scan optimized for mobile devices"""
        
        start_time = time.time()
        
        # Super basic checks for mobile
        mobile_results = {
            'health_status': 'good',  # good, warning, critical
            'issues_count': 0,
            'top_priority': None,
            'quick_action': None,
            'celebration': None
        }
        
        # Quick customer check
        partners_no_email = self.env['res.partner'].search_count([('email', '=', False), ('is_company', '=', False)])
        
        if partners_no_email > 10:
            mobile_results['health_status'] = 'warning'
            mobile_results['issues_count'] = partners_no_email
            mobile_results['top_priority'] = f'{partners_no_email} customers missing email addresses'
            mobile_results['quick_action'] = 'Update customer emails'
        elif partners_no_email > 50:
            mobile_results['health_status'] = 'critical'
        
        if mobile_results['health_status'] == 'good':
            mobile_results['celebration'] = '🎉 Your data looks great! Keep up the excellent work!'
        
        scan_duration = time.time() - start_time
        
        return {
            'success': True,
            'scan_type': 'mobile_friendly',
            'duration': scan_duration,
            'results': mobile_results,
            'message': f'📱 Mobile scan completed in {scan_duration:.2f} seconds!'
        }
    
    def get_scan_celebration_message(self):
        """🎉 Get celebration message based on scan results"""
        
        if self.health_score >= 95:
            return {
                'celebration': True,
                'message': '🏆 OUTSTANDING! Your data quality is phenomenal!',
                'emoji': '🎉🏆✨',
                'action': 'Share this achievement with your team!',
                'dance_move': 'Victory breakdance! 💃🕺'
            }
        elif self.health_score >= 85:
            return {
                'celebration': True,
                'message': '🌟 EXCELLENT! Your data quality is impressive!',
                'emoji': '🌟💫⭐',
                'action': 'Keep up the great work!',
                'dance_move': 'Happy shimmy! 💃'
            }
        elif self.health_score >= 70:
            return {
                'celebration': False,
                'message': '👍 GOOD! Your data quality is solid with room for improvement.',
                'emoji': '👍💪📈',
                'action': 'Let\'s fix a few more issues!',
                'dance_move': 'Encouraging nod! 👍'
            }
        else:
            return {
                'celebration': False,
                'message': '💪 OPPORTUNITY! Time to make your data shine!',
                'emoji': '💪🔧⚡',
                'action': 'Boss battle time! Rally the team!',
                'dance_move': 'Battle ready stance! ⚔️'
            }
    
    @api.model
    def get_lightning_scan_stats(self):
        """📊 Get overall lightning scan statistics"""
        
        all_scans = self.search([])
        
        stats = {
            'total_scans': len(all_scans),
            'average_duration': sum(scan.scan_duration for scan in all_scans) / len(all_scans) if all_scans else 0,
            'average_health_score': sum(scan.health_score for scan in all_scans) / len(all_scans) if all_scans else 0,
            'total_issues_found': sum(scan.issues_found for scan in all_scans),
            'boss_battles_triggered': sum(1 for scan in all_scans if scan.boss_battle_triggered),
            'fastest_scan': min(scan.scan_duration for scan in all_scans) if all_scans else 0,
            'best_health_score': max(scan.health_score for scan in all_scans) if all_scans else 0
        }
        
        return stats