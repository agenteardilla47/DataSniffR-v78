# -*- coding: utf-8 -*-

import json
import requests
import base64
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import hashlib
import hmac
from urllib.parse import urlencode, urlparse
import xml.etree.ElementTree as ET

_logger = logging.getLogger(__name__)

class DatasniffrApiConnector(models.Model):
    _name = 'datasniffr.api.connector'
    _description = 'DataSniffR API Connector - External API Integration'
    _order = 'create_date desc'

    name = fields.Char('Connection Name', required=True)
    description = fields.Text('Description')
    api_type = fields.Selection([
        ('rest', 'REST API'),
        ('soap', 'SOAP API'),
        ('graphql', 'GraphQL'),
        ('webhook', 'Webhook'),
        ('ftp', 'FTP/SFTP'),
        ('database', 'Direct Database'),
        ('custom', 'Custom Protocol')
    ], string='API Type', required=True, default='rest')
    
    # Connection Configuration
    base_url = fields.Char('Base URL', required=True)
    auth_type = fields.Selection([
        ('none', 'No Authentication'),
        ('basic', 'Basic Auth'),
        ('bearer', 'Bearer Token'),
        ('oauth2', 'OAuth 2.0'),
        ('api_key', 'API Key'),
        ('custom', 'Custom Headers')
    ], string='Authentication Type', default='none')
    
    username = fields.Char('Username')
    password = fields.Char('Password')
    api_key = fields.Char('API Key')
    bearer_token = fields.Text('Bearer Token')
    custom_headers = fields.Text('Custom Headers', help='JSON format: {"key": "value"}')
    
    # OAuth 2.0 Configuration
    oauth_client_id = fields.Char('OAuth Client ID')
    oauth_client_secret = fields.Char('OAuth Client Secret')
    oauth_token_url = fields.Char('OAuth Token URL')
    oauth_scope = fields.Char('OAuth Scope')
    oauth_access_token = fields.Text('Access Token', readonly=True)
    oauth_refresh_token = fields.Text('Refresh Token', readonly=True)
    oauth_expires_at = fields.Datetime('Token Expires At', readonly=True)
    
    # Data Mapping
    sync_direction = fields.Selection([
        ('import', 'Import Only'),
        ('export', 'Export Only'),
        ('bidirectional', 'Bidirectional Sync')
    ], string='Sync Direction', default='import')
    
    source_model = fields.Char('Source Model', help='Odoo model to sync from/to')
    target_endpoint = fields.Char('Target Endpoint', help='API endpoint path')
    data_format = fields.Selection([
        ('json', 'JSON'),
        ('xml', 'XML'),
        ('csv', 'CSV'),
        ('custom', 'Custom Format')
    ], string='Data Format', default='json')
    
    field_mapping = fields.Text('Field Mapping', default='{}', help='JSON mapping between Odoo fields and API fields')
    transformation_rules = fields.Text('Transformation Rules', default='{}', help='JSON rules for data transformation')
    
    # Sync Configuration
    sync_frequency = fields.Selection([
        ('manual', 'Manual'),
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly')
    ], string='Sync Frequency', default='manual')
    
    batch_size = fields.Integer('Batch Size', default=100, help='Number of records to process per batch')
    timeout = fields.Integer('Timeout (seconds)', default=30)
    retry_attempts = fields.Integer('Retry Attempts', default=3)
    
    # Webhook Configuration
    webhook_secret = fields.Char('Webhook Secret')
    webhook_events = fields.Text('Webhook Events', help='Comma-separated list of events to listen for')
    
    # Status and Monitoring
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('testing', 'Testing'),
        ('error', 'Error'),
        ('disabled', 'Disabled')
    ], string='Status', default='draft')
    
    last_sync = fields.Datetime('Last Sync', readonly=True)
    next_sync = fields.Datetime('Next Sync', readonly=True)
    sync_status = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
        ('running', 'Running')
    ], string='Last Sync Status', readonly=True)
    
    # Statistics
    total_syncs = fields.Integer('Total Syncs', readonly=True)
    successful_syncs = fields.Integer('Successful Syncs', readonly=True)
    failed_syncs = fields.Integer('Failed Syncs', readonly=True)
    records_imported = fields.Integer('Records Imported', readonly=True)
    records_exported = fields.Integer('Records Exported', readonly=True)
    
    # AI Integration
    ai_data_validation = fields.Boolean('AI Data Validation', default=True)
    ai_error_analysis = fields.Boolean('AI Error Analysis', default=True)
    ai_provider = fields.Selection([
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI GPT'),
        ('claude', 'Anthropic Claude')
    ], string='AI Provider', default='gemini')
    
    # Boss Battle Integration
    boss_battle_triggered = fields.Boolean('Boss Battle Triggered', readonly=True)
    boss_battle_type = fields.Char('Boss Battle Type', readonly=True)
    
    # Logs
    sync_logs = fields.One2many('datasniffr.api.sync.log', 'connector_id', string='Sync Logs')

    @api.model
    def create(self, vals):
        """Override create to set up initial configuration"""
        if 'field_mapping' not in vals or not vals['field_mapping']:
            vals['field_mapping'] = json.dumps({
                'id': 'id',
                'name': 'name',
                'create_date': 'created_at',
                'write_date': 'updated_at'
            })
        return super(DatasniffrApiConnector, self).create(vals)

    def action_test_connection(self):
        """Test the API connection"""
        self.ensure_one()
        
        try:
            self.state = 'testing'
            
            # Prepare request
            headers = self._get_headers()
            url = self._build_url('/test')  # Use a test endpoint if available
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                self.state = 'active'
                message = f"🎯 Connection to {self.name} successful! Status: {response.status_code}"
                msg_type = 'success'
            else:
                self.state = 'error'
                message = f"❌ Connection failed! Status: {response.status_code} - {response.text[:100]}"
                msg_type = 'warning'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': msg_type,
                    'sticky': False,
                }
            }
            
        except Exception as e:
            self.state = 'error'
            _logger.error(f"Connection test failed for {self.name}: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f"❌ Connection test failed: {str(e)}",
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def action_sync_now(self):
        """Trigger immediate synchronization"""
        self.ensure_one()
        
        try:
            if self.sync_direction == 'import':
                result = self._import_data()
            elif self.sync_direction == 'export':
                result = self._export_data()
            else:  # bidirectional
                import_result = self._import_data()
                export_result = self._export_data()
                result = {
                    'imported': import_result.get('count', 0),
                    'exported': export_result.get('count', 0),
                    'errors': import_result.get('errors', []) + export_result.get('errors', [])
                }
            
            # Update statistics
            self.total_syncs += 1
            if not result.get('errors'):
                self.successful_syncs += 1
                self.sync_status = 'success'
            else:
                self.failed_syncs += 1
                self.sync_status = 'failed' if len(result.get('errors', [])) > 0 else 'partial'
            
            self.last_sync = datetime.now()
            self._schedule_next_sync()
            
            # Check for boss battle triggers
            self._check_boss_battle_triggers(result)
            
            # Create sync log
            self._create_sync_log(result)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'🚀 Sync completed! Processed: {result.get("imported", 0) + result.get("exported", 0)} records',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Sync failed for {self.name}: {str(e)}")
            self.sync_status = 'failed'
            self.failed_syncs += 1
            raise UserError(f"Sync failed: {str(e)}")

    def _import_data(self):
        """Import data from external API"""
        try:
            headers = self._get_headers()
            url = self._build_url(self.target_endpoint)
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse response data
            if self.data_format == 'json':
                data = response.json()
            elif self.data_format == 'xml':
                data = self._parse_xml(response.text)
            else:
                data = response.text
            
            # Transform and import data
            records_created = 0
            errors = []
            
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and 'data' in data:
                items = data['data']
            else:
                items = [data]
            
            for item in items:
                try:
                    # Transform data according to field mapping
                    transformed_data = self._transform_data(item, 'import')
                    
                    # Validate with AI if enabled
                    if self.ai_data_validation:
                        validation_result = self._ai_validate_data(transformed_data)
                        if not validation_result['valid']:
                            errors.append(f"AI validation failed: {validation_result['reason']}")
                            continue
                    
                    # Create or update record
                    model = self.env[self.source_model]
                    
                    # Check if record exists
                    existing_record = None
                    if 'id' in transformed_data:
                        existing_record = model.search([('id', '=', transformed_data['id'])], limit=1)
                    
                    if existing_record:
                        existing_record.write(transformed_data)
                    else:
                        model.create(transformed_data)
                    
                    records_created += 1
                    
                except Exception as e:
                    errors.append(f"Error processing record: {str(e)}")
            
            self.records_imported += records_created
            
            return {
                'count': records_created,
                'errors': errors,
                'type': 'import'
            }
            
        except Exception as e:
            _logger.error(f"Import failed: {str(e)}")
            raise

    def _export_data(self):
        """Export data to external API"""
        try:
            model = self.env[self.source_model]
            records = model.search([])  # Get all records or apply domain filter
            
            exported_count = 0
            errors = []
            
            # Process in batches
            for i in range(0, len(records), self.batch_size):
                batch = records[i:i + self.batch_size]
                
                batch_data = []
                for record in batch:
                    try:
                        # Transform data according to field mapping
                        transformed_data = self._transform_data(record, 'export')
                        batch_data.append(transformed_data)
                    except Exception as e:
                        errors.append(f"Error transforming record {record.id}: {str(e)}")
                
                if batch_data:
                    # Send batch to API
                    try:
                        headers = self._get_headers()
                        url = self._build_url(self.target_endpoint)
                        
                        if self.data_format == 'json':
                            response = requests.post(url, json=batch_data, headers=headers, timeout=self.timeout)
                        else:
                            response = requests.post(url, data=batch_data, headers=headers, timeout=self.timeout)
                        
                        response.raise_for_status()
                        exported_count += len(batch_data)
                        
                    except Exception as e:
                        errors.append(f"Error sending batch: {str(e)}")
            
            self.records_exported += exported_count
            
            return {
                'count': exported_count,
                'errors': errors,
                'type': 'export'
            }
            
        except Exception as e:
            _logger.error(f"Export failed: {str(e)}")
            raise

    def _get_headers(self):
        """Get HTTP headers for API requests"""
        headers = {'Content-Type': 'application/json'}
        
        if self.auth_type == 'basic':
            auth_string = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            headers['Authorization'] = f'Basic {auth_string}'
        elif self.auth_type == 'bearer':
            headers['Authorization'] = f'Bearer {self.bearer_token}'
        elif self.auth_type == 'api_key':
            headers['X-API-Key'] = self.api_key
        elif self.auth_type == 'oauth2':
            if self._is_token_expired():
                self._refresh_oauth_token()
            headers['Authorization'] = f'Bearer {self.oauth_access_token}'
        
        # Add custom headers
        if self.custom_headers:
            try:
                custom = json.loads(self.custom_headers)
                headers.update(custom)
            except:
                pass
        
        return headers

    def _build_url(self, endpoint):
        """Build complete URL for API request"""
        base = self.base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base}/{endpoint}"

    def _transform_data(self, data, direction):
        """Transform data according to field mapping and rules"""
        try:
            field_mapping = json.loads(self.field_mapping) if self.field_mapping else {}
            transformation_rules = json.loads(self.transformation_rules) if self.transformation_rules else {}
            
            transformed = {}
            
            if direction == 'import':
                # API -> Odoo
                for api_field, odoo_field in field_mapping.items():
                    if api_field in data:
                        value = data[api_field]
                        
                        # Apply transformation rules
                        if odoo_field in transformation_rules:
                            rule = transformation_rules[odoo_field]
                            if rule.get('type') == 'date':
                                value = self._transform_date(value, rule.get('format', '%Y-%m-%d'))
                            elif rule.get('type') == 'boolean':
                                value = str(value).lower() in ['true', '1', 'yes']
                            elif rule.get('type') == 'float':
                                value = float(value) if value else 0.0
                        
                        transformed[odoo_field] = value
            else:
                # Odoo -> API
                reverse_mapping = {v: k for k, v in field_mapping.items()}
                for odoo_field, api_field in reverse_mapping.items():
                    if hasattr(data, odoo_field):
                        value = getattr(data, odoo_field)
                        
                        # Handle Many2one fields
                        if hasattr(value, 'name'):
                            value = value.name
                        elif hasattr(value, 'id'):
                            value = value.id
                        
                        transformed[api_field] = value
            
            return transformed
            
        except Exception as e:
            _logger.error(f"Data transformation failed: {str(e)}")
            raise

    def _transform_date(self, value, format_string):
        """Transform date string to datetime object"""
        try:
            if isinstance(value, str):
                return datetime.strptime(value, format_string)
            return value
        except:
            return False

    def _ai_validate_data(self, data):
        """Use AI to validate data quality"""
        try:
            # Mock AI validation (in real implementation, call actual AI service)
            validation_result = {
                'valid': True,
                'reason': '',
                'confidence': 0.95,
                'suggestions': []
            }
            
            # Basic validation rules
            if not data:
                validation_result['valid'] = False
                validation_result['reason'] = 'Empty data'
            elif 'name' in data and not data['name']:
                validation_result['valid'] = False
                validation_result['reason'] = 'Missing required field: name'
            
            return validation_result
            
        except Exception as e:
            _logger.error(f"AI validation failed: {str(e)}")
            return {'valid': True, 'reason': 'Validation unavailable'}

    def _check_boss_battle_triggers(self, sync_result):
        """Check if sync should trigger boss battles"""
        try:
            total_processed = sync_result.get('imported', 0) + sync_result.get('exported', 0)
            
            # Trigger boss battle for large syncs
            if total_processed > 5000:
                self.boss_battle_triggered = True
                self.boss_battle_type = 'data_tsunami'
                
                boss_battle = self.env['datasniffr.boss.battle'].create({
                    'name': f'🌊 Data Tsunami Boss - {self.name}',
                    'boss_type': 'data_tsunami',
                    'difficulty': 'legendary',
                    'description': f'Survived massive data sync with {total_processed} records!',
                    'trigger_model': self._name,
                    'trigger_record_id': self.id,
                    'xp_reward': min(total_processed // 10, 2000),
                    'battle_data': json.dumps({
                        'records_processed': total_processed,
                        'sync_type': self.sync_direction,
                        'api_type': self.api_type
                    })
                })
                
                boss_battle.action_start_battle()
            
            # Trigger for error-free complex syncs
            elif total_processed > 1000 and not sync_result.get('errors'):
                self.boss_battle_triggered = True
                self.boss_battle_type = 'sync_master'
                
                boss_battle = self.env['datasniffr.boss.battle'].create({
                    'name': f'⚡ Sync Master Boss - {self.name}',
                    'boss_type': 'sync_master',
                    'difficulty': 'epic',
                    'description': 'Achieved perfect synchronization without errors!',
                    'trigger_model': self._name,
                    'trigger_record_id': self.id,
                    'xp_reward': 1000,
                    'battle_data': json.dumps({
                        'perfect_sync': True,
                        'records_processed': total_processed
                    })
                })
                
                boss_battle.action_start_battle()
                
        except Exception as e:
            _logger.error(f"Error checking boss battle triggers: {str(e)}")

    def _create_sync_log(self, result):
        """Create sync log entry"""
        self.env['datasniffr.api.sync.log'].create({
            'connector_id': self.id,
            'sync_type': self.sync_direction,
            'status': 'success' if not result.get('errors') else 'failed',
            'records_processed': result.get('imported', 0) + result.get('exported', 0),
            'error_count': len(result.get('errors', [])),
            'details': json.dumps(result),
            'sync_date': datetime.now()
        })

    def _schedule_next_sync(self):
        """Schedule next automatic sync"""
        if self.sync_frequency == 'hourly':
            self.next_sync = datetime.now() + timedelta(hours=1)
        elif self.sync_frequency == 'daily':
            self.next_sync = datetime.now() + timedelta(days=1)
        elif self.sync_frequency == 'weekly':
            self.next_sync = datetime.now() + timedelta(weeks=1)

    def _is_token_expired(self):
        """Check if OAuth token is expired"""
        if not self.oauth_expires_at:
            return True
        return datetime.now() >= self.oauth_expires_at

    def _refresh_oauth_token(self):
        """Refresh OAuth 2.0 token"""
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.oauth_refresh_token,
                'client_id': self.oauth_client_id,
                'client_secret': self.oauth_client_secret
            }
            
            response = requests.post(self.oauth_token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.oauth_access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                self.oauth_refresh_token = token_data['refresh_token']
            
            expires_in = token_data.get('expires_in', 3600)
            self.oauth_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
        except Exception as e:
            _logger.error(f"Token refresh failed: {str(e)}")
            raise

    def _parse_xml(self, xml_string):
        """Parse XML response to dictionary"""
        try:
            root = ET.fromstring(xml_string)
            return self._xml_to_dict(root)
        except Exception as e:
            _logger.error(f"XML parsing failed: {str(e)}")
            return {}

    def _xml_to_dict(self, element):
        """Convert XML element to dictionary"""
        result = {}
        for child in element:
            if len(child) == 0:
                result[child.tag] = child.text
            else:
                result[child.tag] = self._xml_to_dict(child)
        return result

    @api.model
    def process_webhook(self, connector_id, data, signature=None):
        """Process incoming webhook data"""
        connector = self.browse(connector_id)
        
        try:
            # Verify webhook signature if secret is configured
            if connector.webhook_secret and signature:
                expected_signature = hmac.new(
                    connector.webhook_secret.encode(),
                    json.dumps(data).encode(),
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature, expected_signature):
                    raise ValidationError("Invalid webhook signature")
            
            # Process webhook data
            transformed_data = connector._transform_data(data, 'import')
            
            # Create or update record
            model = connector.env[connector.source_model]
            record = model.create(transformed_data)
            
            _logger.info(f"Webhook processed successfully for {connector.name}")
            
            return {'status': 'success', 'record_id': record.id}
            
        except Exception as e:
            _logger.error(f"Webhook processing failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @api.model
    def run_scheduled_syncs(self):
        """Cron job to run scheduled syncs"""
        scheduled_connectors = self.search([
            ('sync_frequency', '!=', 'manual'),
            ('next_sync', '<=', datetime.now()),
            ('state', '=', 'active')
        ])
        
        for connector in scheduled_connectors:
            try:
                connector.action_sync_now()
            except Exception as e:
                _logger.error(f"Scheduled sync failed for {connector.name}: {str(e)}")


class DatasniffrApiSyncLog(models.Model):
    _name = 'datasniffr.api.sync.log'
    _description = 'API Sync Logs'
    _order = 'sync_date desc'

    connector_id = fields.Many2one('datasniffr.api.connector', string='Connector', required=True, ondelete='cascade')
    sync_type = fields.Selection([
        ('import', 'Import'),
        ('export', 'Export'),
        ('bidirectional', 'Bidirectional')
    ], string='Sync Type', required=True)
    
    status = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed')
    ], string='Status', required=True)
    
    sync_date = fields.Datetime('Sync Date', required=True)
    records_processed = fields.Integer('Records Processed')
    error_count = fields.Integer('Error Count')
    details = fields.Text('Details')
    
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.connector_id.name} - {record.sync_date.strftime('%Y-%m-%d %H:%M')} ({record.status})"
            result.append((record.id, name))
        return result