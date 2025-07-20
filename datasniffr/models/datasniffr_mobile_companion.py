# -*- coding: utf-8 -*-

import json
import base64
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import uuid
import hashlib
from odoo.http import request

_logger = logging.getLogger(__name__)

class DatasniffrMobileCompanion(models.Model):
    _name = 'datasniffr.mobile.companion'
    _description = 'DataSniffR Mobile Companion - Mobile App Support'
    _order = 'create_date desc'

    name = fields.Char('Device Name', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    device_id = fields.Char('Device ID', required=True, unique=True)
    device_type = fields.Selection([
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('tablet', 'Tablet'),
        ('web', 'Web App')
    ], string='Device Type', required=True)
    
    # Device Information
    app_version = fields.Char('App Version')
    os_version = fields.Char('OS Version')
    device_model = fields.Char('Device Model')
    screen_resolution = fields.Char('Screen Resolution')
    
    # Authentication & Security
    access_token = fields.Char('Access Token', readonly=True)
    refresh_token = fields.Char('Refresh Token', readonly=True)
    token_expires_at = fields.Datetime('Token Expires At', readonly=True)
    last_activity = fields.Datetime('Last Activity', readonly=True)
    
    # Push Notifications
    push_token = fields.Char('Push Notification Token')
    push_enabled = fields.Boolean('Push Notifications Enabled', default=True)
    notification_settings = fields.Text('Notification Settings', default='{}')
    
    # Sync Configuration
    offline_sync_enabled = fields.Boolean('Offline Sync Enabled', default=True)
    sync_frequency = fields.Selection([
        ('realtime', 'Real-time'),
        ('5min', 'Every 5 minutes'),
        ('15min', 'Every 15 minutes'),
        ('30min', 'Every 30 minutes'),
        ('1hour', 'Every hour'),
        ('manual', 'Manual only')
    ], string='Sync Frequency', default='15min')
    
    last_sync = fields.Datetime('Last Sync', readonly=True)
    sync_status = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('failed', 'Failed'),
        ('pending', 'Pending')
    ], string='Sync Status', readonly=True)
    
    # Mobile Features
    quick_scan_enabled = fields.Boolean('Quick Scan Enabled', default=True)
    voice_commands_enabled = fields.Boolean('Voice Commands Enabled', default=True)
    camera_scan_enabled = fields.Boolean('Camera Scan Enabled', default=True)
    location_services_enabled = fields.Boolean('Location Services Enabled', default=False)
    
    # Data Quality Settings
    mobile_scan_types = fields.Text('Mobile Scan Types', default='{}')
    auto_fix_enabled = fields.Boolean('Auto-fix Enabled', default=True)
    ai_suggestions_enabled = fields.Boolean('AI Suggestions Enabled', default=True)
    
    # Statistics
    scans_performed = fields.Integer('Scans Performed', readonly=True)
    issues_found = fields.Integer('Issues Found', readonly=True)
    fixes_applied = fields.Integer('Fixes Applied', readonly=True)
    notifications_sent = fields.Integer('Notifications Sent', readonly=True)
    
    # Status
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked')
    ], string='Status', default='active')
    
    # Boss Battle Integration
    mobile_xp = fields.Integer('Mobile XP', default=0, readonly=True)
    mobile_level = fields.Integer('Mobile Level', default=1, readonly=True)
    boss_battles_triggered = fields.Integer('Boss Battles Triggered', readonly=True)
    
    # Offline Data
    offline_data = fields.One2many('datasniffr.mobile.offline.data', 'companion_id', string='Offline Data')
    mobile_sessions = fields.One2many('datasniffr.mobile.session', 'companion_id', string='Mobile Sessions')

    @api.model
    def create(self, vals):
        """Override create to generate tokens and setup device"""
        if not vals.get('device_id'):
            vals['device_id'] = str(uuid.uuid4())
        
        # Generate access tokens
        vals['access_token'] = self._generate_token()
        vals['refresh_token'] = self._generate_token()
        vals['token_expires_at'] = datetime.now() + timedelta(hours=24)
        
        # Setup default notification settings
        if not vals.get('notification_settings'):
            vals['notification_settings'] = json.dumps({
                'data_issues': True,
                'scan_complete': True,
                'boss_battles': True,
                'achievements': True,
                'system_alerts': True
            })
        
        # Setup default mobile scan types
        if not vals.get('mobile_scan_types'):
            vals['mobile_scan_types'] = json.dumps({
                'quick_health_check': True,
                'duplicate_detection': True,
                'format_validation': True,
                'field_validation': True,
                'ai_quality_check': True
            })
        
        return super(DatasniffrMobileCompanion, self).create(vals)

    def _generate_token(self):
        """Generate secure token"""
        return hashlib.sha256(f"{uuid.uuid4()}{datetime.now()}".encode()).hexdigest()

    @api.model
    def authenticate_device(self, device_id, user_credentials):
        """Authenticate mobile device"""
        try:
            # Find existing companion or create new one
            companion = self.search([('device_id', '=', device_id)], limit=1)
            
            if not companion:
                # Create new companion for device
                companion = self.create({
                    'name': f"Mobile Device {device_id[:8]}",
                    'device_id': device_id,
                    'device_type': 'android',  # Default, should be passed from client
                })
            
            # Update last activity
            companion.last_activity = datetime.now()
            
            # Start new mobile session
            session = self.env['datasniffr.mobile.session'].create({
                'companion_id': companion.id,
                'session_start': datetime.now(),
                'device_info': json.dumps(user_credentials.get('device_info', {}))
            })
            
            return {
                'success': True,
                'access_token': companion.access_token,
                'refresh_token': companion.refresh_token,
                'expires_at': companion.token_expires_at.isoformat(),
                'companion_id': companion.id,
                'session_id': session.id
            }
            
        except Exception as e:
            _logger.error(f"Device authentication failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    def action_sync_mobile_data(self):
        """Sync data for mobile device"""
        self.ensure_one()
        
        try:
            # Get data that needs to be synced to mobile
            sync_data = self._prepare_mobile_sync_data()
            
            # Process offline changes from mobile
            offline_changes = self._process_offline_changes()
            
            # Update sync status
            self.last_sync = datetime.now()
            self.sync_status = 'success'
            
            # Check for boss battle triggers
            self._check_mobile_boss_battles(sync_data, offline_changes)
            
            return {
                'success': True,
                'sync_data': sync_data,
                'offline_changes_processed': offline_changes,
                'last_sync': self.last_sync.isoformat()
            }
            
        except Exception as e:
            self.sync_status = 'failed'
            _logger.error(f"Mobile sync failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _prepare_mobile_sync_data(self):
        """Prepare data for mobile sync"""
        sync_data = {
            'user_profile': {
                'name': self.user_id.name,
                'email': self.user_id.email,
                'mobile_level': self.mobile_level,
                'mobile_xp': self.mobile_xp
            },
            'recent_scans': [],
            'pending_issues': [],
            'boss_battles': [],
            'achievements': [],
            'settings': json.loads(self.notification_settings)
        }
        
        # Get recent scans
        recent_scans = self.env['datasniffr.scan.result'].search([
            ('user_id', '=', self.user_id.id),
            ('create_date', '>=', datetime.now() - timedelta(days=7))
        ], limit=20)
        
        for scan in recent_scans:
            sync_data['recent_scans'].append({
                'id': scan.id,
                'name': scan.name,
                'scan_type': scan.scan_type,
                'score': scan.quality_score,
                'issues_found': scan.total_issues,
                'date': scan.create_date.isoformat(),
                'status': scan.state
            })
        
        # Get pending data quality issues
        pending_issues = self.env['datasniffr.data.issue'].search([
            ('state', '=', 'open'),
            ('assigned_user_id', '=', self.user_id.id)
        ], limit=50)
        
        for issue in pending_issues:
            sync_data['pending_issues'].append({
                'id': issue.id,
                'title': issue.name,
                'severity': issue.severity,
                'model': issue.model_name,
                'record_id': issue.record_id,
                'suggested_fix': issue.suggested_fix,
                'can_auto_fix': issue.can_auto_fix
            })
        
        # Get active boss battles
        active_battles = self.env['datasniffr.boss.battle'].search([
            ('user_id', '=', self.user_id.id),
            ('state', 'in', ['active', 'pending'])
        ])
        
        for battle in active_battles:
            sync_data['boss_battles'].append({
                'id': battle.id,
                'name': battle.name,
                'boss_type': battle.boss_type,
                'difficulty': battle.difficulty,
                'xp_reward': battle.xp_reward,
                'progress': battle.progress,
                'state': battle.state
            })
        
        return sync_data

    def _process_offline_changes(self):
        """Process changes made while offline"""
        offline_data = self.offline_data.filtered(lambda x: x.sync_status == 'pending')
        processed_count = 0
        
        for offline_record in offline_data:
            try:
                data = json.loads(offline_record.data)
                
                if offline_record.action == 'scan':
                    # Process offline scan
                    self._process_offline_scan(data)
                elif offline_record.action == 'fix':
                    # Process offline fix
                    self._process_offline_fix(data)
                elif offline_record.action == 'create':
                    # Process offline record creation
                    self._process_offline_create(data)
                
                offline_record.sync_status = 'synced'
                offline_record.synced_at = datetime.now()
                processed_count += 1
                
            except Exception as e:
                offline_record.sync_status = 'failed'
                offline_record.error_message = str(e)
                _logger.error(f"Failed to process offline data: {str(e)}")
        
        return processed_count

    def _process_offline_scan(self, scan_data):
        """Process scan performed offline"""
        # Create scan result from offline data
        scan_result = self.env['datasniffr.scan.result'].create({
            'name': scan_data.get('name', 'Mobile Scan'),
            'scan_type': scan_data.get('scan_type', 'mobile'),
            'model_name': scan_data.get('model_name'),
            'user_id': self.user_id.id,
            'quality_score': scan_data.get('quality_score', 0),
            'total_issues': scan_data.get('total_issues', 0),
            'state': 'completed'
        })
        
        # Update mobile statistics
        self.scans_performed += 1
        self.issues_found += scan_data.get('total_issues', 0)
        
        # Award mobile XP
        self._award_mobile_xp(50)

    def _process_offline_fix(self, fix_data):
        """Process fix applied offline"""
        # Find the data issue and mark as fixed
        issue = self.env['datasniffr.data.issue'].browse(fix_data.get('issue_id'))
        if issue.exists():
            issue.write({
                'state': 'fixed',
                'resolution_notes': f"Fixed via mobile app on {datetime.now()}",
                'fixed_by': self.user_id.id,
                'fixed_date': datetime.now()
            })
        
        # Update mobile statistics
        self.fixes_applied += 1
        
        # Award mobile XP
        self._award_mobile_xp(25)

    def _process_offline_create(self, create_data):
        """Process record created offline"""
        model_name = create_data.get('model_name')
        if model_name:
            model = self.env[model_name]
            model.create(create_data.get('values', {}))

    def _award_mobile_xp(self, xp_amount):
        """Award XP and handle level ups"""
        self.mobile_xp += xp_amount
        
        # Calculate new level (every 1000 XP = 1 level)
        new_level = (self.mobile_xp // 1000) + 1
        
        if new_level > self.mobile_level:
            self.mobile_level = new_level
            
            # Send level up notification
            self._send_push_notification(
                title="🎉 Level Up!",
                body=f"Congratulations! You've reached Mobile Level {new_level}!",
                data={'type': 'level_up', 'new_level': new_level}
            )

    def _check_mobile_boss_battles(self, sync_data, offline_changes):
        """Check if mobile activity should trigger boss battles"""
        try:
            # Trigger boss battle for mobile power users
            if self.scans_performed > 100 and self.mobile_level >= 5:
                self.boss_battles_triggered += 1
                
                boss_battle = self.env['datasniffr.boss.battle'].create({
                    'name': f'📱 Mobile Master Boss - {self.name}',
                    'boss_type': 'mobile_master',
                    'difficulty': 'legendary',
                    'description': f'Conquered data quality from mobile device!',
                    'trigger_model': self._name,
                    'trigger_record_id': self.id,
                    'user_id': self.user_id.id,
                    'xp_reward': 1500,
                    'battle_data': json.dumps({
                        'mobile_scans': self.scans_performed,
                        'mobile_level': self.mobile_level,
                        'device_type': self.device_type
                    })
                })
                
                boss_battle.action_start_battle()
                
                # Send boss battle notification
                self._send_push_notification(
                    title="⚔️ Boss Battle!",
                    body="Mobile Master Boss has appeared! Ready for battle?",
                    data={'type': 'boss_battle', 'battle_id': boss_battle.id}
                )
            
            # Trigger for offline warriors
            elif offline_changes > 20:
                boss_battle = self.env['datasniffr.boss.battle'].create({
                    'name': f'🏝️ Offline Warrior Boss - {self.name}',
                    'boss_type': 'offline_warrior',
                    'difficulty': 'epic',
                    'description': f'Mastered offline data management!',
                    'trigger_model': self._name,
                    'trigger_record_id': self.id,
                    'user_id': self.user_id.id,
                    'xp_reward': 1000,
                    'battle_data': json.dumps({
                        'offline_changes': offline_changes,
                        'sync_frequency': self.sync_frequency
                    })
                })
                
                boss_battle.action_start_battle()
                
        except Exception as e:
            _logger.error(f"Error checking mobile boss battles: {str(e)}")

    def _send_push_notification(self, title, body, data=None):
        """Send push notification to mobile device"""
        try:
            if not self.push_enabled or not self.push_token:
                return False
            
            notification_data = {
                'title': title,
                'body': body,
                'data': data or {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Here you would integrate with actual push notification service
            # For now, we'll log the notification and create a record
            
            self.env['datasniffr.mobile.notification'].create({
                'companion_id': self.id,
                'title': title,
                'body': body,
                'data': json.dumps(data or {}),
                'sent_at': datetime.now(),
                'status': 'sent'
            })
            
            self.notifications_sent += 1
            
            _logger.info(f"Push notification sent to {self.name}: {title}")
            return True
            
        except Exception as e:
            _logger.error(f"Failed to send push notification: {str(e)}")
            return False

    def action_send_test_notification(self):
        """Send test notification to mobile device"""
        self.ensure_one()
        
        success = self._send_push_notification(
            title="🧪 Test Notification",
            body="DataSniffR Mobile is working perfectly!",
            data={'type': 'test'}
        )
        
        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'🎯 Test notification sent to {self.name}!',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'❌ Failed to send notification to {self.name}',
                    'type': 'warning',
                    'sticky': False,
                }
            }

    def action_revoke_access(self):
        """Revoke mobile device access"""
        self.ensure_one()
        
        self.write({
            'state': 'revoked',
            'access_token': False,
            'refresh_token': False,
            'token_expires_at': False
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'🔒 Access revoked for {self.name}',
                'type': 'info',
                'sticky': False,
            }
        }

    @api.model
    def cleanup_expired_tokens(self):
        """Cron job to cleanup expired tokens"""
        expired_companions = self.search([
            ('token_expires_at', '<', datetime.now()),
            ('state', '=', 'active')
        ])
        
        for companion in expired_companions:
            companion.state = 'inactive'
            companion.access_token = False
            companion.refresh_token = False


class DatasniffrMobileOfflineData(models.Model):
    _name = 'datasniffr.mobile.offline.data'
    _description = 'Mobile Offline Data'
    _order = 'create_date desc'

    companion_id = fields.Many2one('datasniffr.mobile.companion', string='Mobile Companion', required=True, ondelete='cascade')
    action = fields.Selection([
        ('scan', 'Scan'),
        ('fix', 'Fix Issue'),
        ('create', 'Create Record'),
        ('update', 'Update Record'),
        ('delete', 'Delete Record')
    ], string='Action', required=True)
    
    data = fields.Text('Data', required=True, help='JSON data for the action')
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('failed', 'Failed')
    ], string='Sync Status', default='pending')
    
    created_offline_at = fields.Datetime('Created Offline At', required=True)
    synced_at = fields.Datetime('Synced At')
    error_message = fields.Text('Error Message')


class DatasniffrMobileSession(models.Model):
    _name = 'datasniffr.mobile.session'
    _description = 'Mobile App Sessions'
    _order = 'session_start desc'

    companion_id = fields.Many2one('datasniffr.mobile.companion', string='Mobile Companion', required=True, ondelete='cascade')
    session_start = fields.Datetime('Session Start', required=True)
    session_end = fields.Datetime('Session End')
    duration_minutes = fields.Float('Duration (minutes)', compute='_compute_duration', store=True)
    
    device_info = fields.Text('Device Info')
    actions_performed = fields.Integer('Actions Performed', default=0)
    scans_in_session = fields.Integer('Scans in Session', default=0)
    fixes_in_session = fields.Integer('Fixes in Session', default=0)
    
    @api.depends('session_start', 'session_end')
    def _compute_duration(self):
        for session in self:
            if session.session_start and session.session_end:
                duration = session.session_end - session.session_start
                session.duration_minutes = duration.total_seconds() / 60
            else:
                session.duration_minutes = 0


class DatasniffrMobileNotification(models.Model):
    _name = 'datasniffr.mobile.notification'
    _description = 'Mobile Push Notifications'
    _order = 'sent_at desc'

    companion_id = fields.Many2one('datasniffr.mobile.companion', string='Mobile Companion', required=True, ondelete='cascade')
    title = fields.Char('Title', required=True)
    body = fields.Text('Body', required=True)
    data = fields.Text('Data', help='JSON data payload')
    
    sent_at = fields.Datetime('Sent At', required=True)
    delivered_at = fields.Datetime('Delivered At')
    opened_at = fields.Datetime('Opened At')
    
    status = fields.Selection([
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('failed', 'Failed')
    ], string='Status', default='sent')
    
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.title} - {record.sent_at.strftime('%Y-%m-%d %H:%M')}"
            result.append((record.id, name))
        return result