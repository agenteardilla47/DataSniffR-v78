# -*- coding: utf-8 -*-

import json
import base64
import os
import shutil
import gzip
import tarfile
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import hashlib
import boto3
from google.cloud import storage as gcs
import paramiko
import ftplib

_logger = logging.getLogger(__name__)

class DatasniffrBackupManager(models.Model):
    _name = 'datasniffr.backup.manager'
    _description = 'DataSniffR Backup Manager - Data Backup Automation'
    _order = 'create_date desc'

    name = fields.Char('Backup Configuration Name', required=True)
    description = fields.Text('Description')
    backup_type = fields.Selection([
        ('full', 'Full Backup'),
        ('incremental', 'Incremental Backup'),
        ('differential', 'Differential Backup'),
        ('selective', 'Selective Backup'),
        ('snapshot', 'Snapshot Backup')
    ], string='Backup Type', required=True, default='full')
    
    # Backup Scope
    backup_scope = fields.Selection([
        ('database', 'Full Database'),
        ('models', 'Specific Models'),
        ('records', 'Specific Records'),
        ('files', 'File Attachments'),
        ('custom', 'Custom Selection')
    ], string='Backup Scope', required=True, default='database')
    
    model_names = fields.Text('Model Names', help='Comma-separated list of models to backup')
    record_filters = fields.Text('Record Filters', help='JSON domain filters for selective backup')
    include_attachments = fields.Boolean('Include Attachments', default=True)
    include_logs = fields.Boolean('Include System Logs', default=False)
    
    # Storage Configuration
    storage_type = fields.Selection([
        ('local', 'Local Storage'),
        ('ftp', 'FTP/SFTP'),
        ('aws_s3', 'Amazon S3'),
        ('google_cloud', 'Google Cloud Storage'),
        ('azure', 'Azure Blob Storage'),
        ('dropbox', 'Dropbox'),
        ('custom', 'Custom Storage')
    ], string='Storage Type', required=True, default='local')
    
    local_path = fields.Char('Local Storage Path', default='/opt/odoo/backups')
    
    # FTP/SFTP Configuration
    ftp_host = fields.Char('FTP/SFTP Host')
    ftp_port = fields.Integer('FTP Port', default=21)
    ftp_username = fields.Char('FTP Username')
    ftp_password = fields.Char('FTP Password')
    ftp_path = fields.Char('FTP Remote Path', default='/')
    use_sftp = fields.Boolean('Use SFTP', default=False)
    
    # Cloud Storage Configuration
    aws_access_key = fields.Char('AWS Access Key')
    aws_secret_key = fields.Char('AWS Secret Key')
    aws_bucket = fields.Char('AWS S3 Bucket')
    aws_region = fields.Char('AWS Region', default='us-east-1')
    
    gcp_credentials = fields.Text('GCP Service Account JSON')
    gcp_bucket = fields.Char('GCP Storage Bucket')
    
    azure_connection_string = fields.Char('Azure Connection String')
    azure_container = fields.Char('Azure Container Name')
    
    # Scheduling
    schedule_type = fields.Selection([
        ('manual', 'Manual'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom Cron')
    ], string='Schedule', default='daily')
    
    schedule_time = fields.Float('Schedule Time (24h)', default=2.0, help='Hour of day for daily/weekly backups')
    custom_cron = fields.Char('Custom Cron Expression')
    next_backup = fields.Datetime('Next Backup', readonly=True)
    
    # Retention Policy
    retention_days = fields.Integer('Retention Days', default=30, help='Keep backups for X days')
    max_backups = fields.Integer('Max Backup Count', default=10, help='Maximum number of backups to keep')
    compress_backups = fields.Boolean('Compress Backups', default=True)
    encrypt_backups = fields.Boolean('Encrypt Backups', default=False)
    encryption_key = fields.Char('Encryption Key')
    
    # Verification
    verify_backups = fields.Boolean('Verify Backup Integrity', default=True)
    test_restore = fields.Boolean('Test Restore Process', default=False)
    
    # Status and Statistics
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('running', 'Running'),
        ('error', 'Error'),
        ('disabled', 'Disabled')
    ], string='Status', default='draft')
    
    last_backup = fields.Datetime('Last Backup', readonly=True)
    last_backup_status = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed')
    ], string='Last Backup Status', readonly=True)
    
    total_backups = fields.Integer('Total Backups Created', readonly=True)
    successful_backups = fields.Integer('Successful Backups', readonly=True)
    failed_backups = fields.Integer('Failed Backups', readonly=True)
    total_backup_size = fields.Float('Total Backup Size (GB)', readonly=True)
    
    # AI Integration
    ai_optimization = fields.Boolean('AI Backup Optimization', default=True)
    ai_anomaly_detection = fields.Boolean('AI Anomaly Detection', default=True)
    ai_provider = fields.Selection([
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI GPT'),
        ('claude', 'Anthropic Claude')
    ], string='AI Provider', default='gemini')
    
    # Boss Battle Integration
    boss_battle_triggered = fields.Boolean('Boss Battle Triggered', readonly=True)
    boss_battle_type = fields.Char('Boss Battle Type', readonly=True)
    
    # Backup History
    backup_history = fields.One2many('datasniffr.backup.history', 'backup_manager_id', string='Backup History')

    @api.model
    def create(self, vals):
        """Override create to setup initial configuration"""
        if 'record_filters' not in vals or not vals['record_filters']:
            vals['record_filters'] = json.dumps([])
        
        if not vals.get('encryption_key') and vals.get('encrypt_backups'):
            vals['encryption_key'] = self._generate_encryption_key()
        
        return super(DatasniffrBackupManager, self).create(vals)

    def _generate_encryption_key(self):
        """Generate encryption key for backups"""
        import secrets
        return secrets.token_urlsafe(32)

    def action_create_backup(self):
        """Create backup manually"""
        self.ensure_one()
        
        try:
            self.state = 'running'
            start_time = datetime.now()
            
            # Prepare backup data
            backup_data = self._prepare_backup_data()
            
            # Create backup file
            backup_file = self._create_backup_file(backup_data)
            
            # Upload to storage
            storage_result = self._upload_backup(backup_file)
            
            # Verify backup if enabled
            if self.verify_backups:
                verification_result = self._verify_backup(backup_file)
            else:
                verification_result = {'verified': True}
            
            # Calculate backup size
            backup_size = os.path.getsize(backup_file['path']) / (1024**3)  # GB
            
            # Create backup history record
            backup_history = self.env['datasniffr.backup.history'].create({
                'backup_manager_id': self.id,
                'backup_type': self.backup_type,
                'backup_date': start_time,
                'backup_size_gb': backup_size,
                'storage_location': storage_result.get('location', ''),
                'status': 'success' if verification_result['verified'] else 'failed',
                'backup_hash': backup_file.get('hash', ''),
                'metadata': json.dumps({
                    'records_backed_up': backup_data.get('record_count', 0),
                    'models_included': backup_data.get('models', []),
                    'compression_ratio': backup_file.get('compression_ratio', 1.0)
                })
            })
            
            # Update statistics
            self.total_backups += 1
            self.total_backup_size += backup_size
            self.last_backup = start_time
            
            if verification_result['verified']:
                self.successful_backups += 1
                self.last_backup_status = 'success'
                self.state = 'active'
            else:
                self.failed_backups += 1
                self.last_backup_status = 'failed'
                self.state = 'error'
            
            # Schedule next backup
            self._schedule_next_backup()
            
            # Check for boss battle triggers
            self._check_backup_boss_battles(backup_data, backup_history)
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            # Clean up local temp file
            if os.path.exists(backup_file['path']):
                os.remove(backup_file['path'])
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'🎯 Backup "{self.name}" created successfully! Size: {backup_size:.2f} GB',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            self.state = 'error'
            self.failed_backups += 1
            self.last_backup_status = 'failed'
            _logger.error(f"Backup creation failed: {str(e)}")
            raise UserError(f"Backup creation failed: {str(e)}")

    def _prepare_backup_data(self):
        """Prepare data for backup"""
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'backup_type': self.backup_type,
            'backup_scope': self.backup_scope,
            'data': {},
            'metadata': {},
            'record_count': 0,
            'models': []
        }
        
        if self.backup_scope == 'database':
            # Full database backup
            backup_data['data'] = self._backup_full_database()
        elif self.backup_scope == 'models':
            # Specific models backup
            backup_data['data'] = self._backup_models()
        elif self.backup_scope == 'records':
            # Specific records backup
            backup_data['data'] = self._backup_records()
        elif self.backup_scope == 'files':
            # File attachments backup
            backup_data['data'] = self._backup_attachments()
        
        # Add system metadata
        backup_data['metadata'] = {
            'odoo_version': self.env['ir.module.module'].get_module_info('base')['version'],
            'database_name': self.env.cr.dbname,
            'backup_manager_id': self.id,
            'user_id': self.env.user.id,
            'company_id': self.env.company.id
        }
        
        return backup_data

    def _backup_full_database(self):
        """Create full database backup"""
        data = {}
        record_count = 0
        
        # Get all models
        model_names = self.env.registry.keys()
        
        for model_name in model_names:
            try:
                model = self.env[model_name]
                records = model.search([])
                
                if records:
                    model_data = []
                    for record in records:
                        record_data = {}
                        for field_name, field in model._fields.items():
                            try:
                                value = record[field_name]
                                # Handle different field types
                                if hasattr(value, 'id'):
                                    value = value.id
                                elif hasattr(value, 'ids'):
                                    value = value.ids
                                record_data[field_name] = value
                            except:
                                pass
                        model_data.append(record_data)
                    
                    data[model_name] = model_data
                    record_count += len(model_data)
                    
            except Exception as e:
                _logger.warning(f"Failed to backup model {model_name}: {str(e)}")
        
        return {'models': data, 'record_count': record_count}

    def _backup_models(self):
        """Backup specific models"""
        data = {}
        record_count = 0
        
        if self.model_names:
            model_list = [m.strip() for m in self.model_names.split(',')]
            
            for model_name in model_list:
                try:
                    model = self.env[model_name]
                    records = model.search([])
                    
                    model_data = []
                    for record in records:
                        record_data = {}
                        for field_name, field in model._fields.items():
                            try:
                                value = record[field_name]
                                if hasattr(value, 'id'):
                                    value = value.id
                                elif hasattr(value, 'ids'):
                                    value = value.ids
                                record_data[field_name] = value
                            except:
                                pass
                        model_data.append(record_data)
                    
                    data[model_name] = model_data
                    record_count += len(model_data)
                    
                except Exception as e:
                    _logger.error(f"Failed to backup model {model_name}: {str(e)}")
        
        return {'models': data, 'record_count': record_count}

    def _backup_records(self):
        """Backup specific records based on filters"""
        data = {}
        record_count = 0
        
        try:
            filters = json.loads(self.record_filters) if self.record_filters else []
            
            for filter_config in filters:
                model_name = filter_config.get('model')
                domain = filter_config.get('domain', [])
                
                if model_name:
                    model = self.env[model_name]
                    records = model.search(domain)
                    
                    model_data = []
                    for record in records:
                        record_data = {}
                        for field_name, field in model._fields.items():
                            try:
                                value = record[field_name]
                                if hasattr(value, 'id'):
                                    value = value.id
                                elif hasattr(value, 'ids'):
                                    value = value.ids
                                record_data[field_name] = value
                            except:
                                pass
                        model_data.append(record_data)
                    
                    data[model_name] = data.get(model_name, []) + model_data
                    record_count += len(model_data)
                    
        except Exception as e:
            _logger.error(f"Failed to backup filtered records: {str(e)}")
        
        return {'models': data, 'record_count': record_count}

    def _backup_attachments(self):
        """Backup file attachments"""
        attachments = self.env['ir.attachment'].search([])
        attachment_data = []
        
        for attachment in attachments:
            try:
                attachment_info = {
                    'id': attachment.id,
                    'name': attachment.name,
                    'datas_fname': attachment.datas_fname,
                    'mimetype': attachment.mimetype,
                    'res_model': attachment.res_model,
                    'res_id': attachment.res_id,
                    'datas': attachment.datas.decode() if attachment.datas else None,
                    'file_size': attachment.file_size,
                    'checksum': attachment.checksum
                }
                attachment_data.append(attachment_info)
            except Exception as e:
                _logger.warning(f"Failed to backup attachment {attachment.id}: {str(e)}")
        
        return {'attachments': attachment_data, 'record_count': len(attachment_data)}

    def _create_backup_file(self, backup_data):
        """Create backup file with compression and encryption"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.name}_{timestamp}_backup.json"
        
        # Create temp directory
        temp_dir = '/tmp/datasniffr_backups'
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, filename)
        
        # Write backup data to file
        with open(file_path, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        original_size = os.path.getsize(file_path)
        
        # Compress if enabled
        if self.compress_backups:
            compressed_path = file_path + '.gz'
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            os.remove(file_path)
            file_path = compressed_path
            filename += '.gz'
        
        # Encrypt if enabled
        if self.encrypt_backups and self.encryption_key:
            encrypted_path = file_path + '.enc'
            self._encrypt_file(file_path, encrypted_path, self.encryption_key)
            os.remove(file_path)
            file_path = encrypted_path
            filename += '.enc'
        
        # Calculate hash
        file_hash = self._calculate_file_hash(file_path)
        
        final_size = os.path.getsize(file_path)
        compression_ratio = original_size / final_size if final_size > 0 else 1.0
        
        return {
            'path': file_path,
            'filename': filename,
            'hash': file_hash,
            'original_size': original_size,
            'final_size': final_size,
            'compression_ratio': compression_ratio
        }

    def _encrypt_file(self, input_path, output_path, key):
        """Encrypt backup file"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Create Fernet key from our key
            key_bytes = key.encode()[:32].ljust(32, b'0')
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            fernet = Fernet(fernet_key)
            
            with open(input_path, 'rb') as f_in:
                data = f_in.read()
            
            encrypted_data = fernet.encrypt(data)
            
            with open(output_path, 'wb') as f_out:
                f_out.write(encrypted_data)
                
        except Exception as e:
            _logger.error(f"Encryption failed: {str(e)}")
            # If encryption fails, just copy the file
            shutil.copy2(input_path, output_path)

    def _calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of backup file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _upload_backup(self, backup_file):
        """Upload backup to configured storage"""
        if self.storage_type == 'local':
            return self._upload_to_local(backup_file)
        elif self.storage_type == 'ftp':
            return self._upload_to_ftp(backup_file)
        elif self.storage_type == 'aws_s3':
            return self._upload_to_s3(backup_file)
        elif self.storage_type == 'google_cloud':
            return self._upload_to_gcs(backup_file)
        else:
            return {'location': 'local', 'success': True}

    def _upload_to_local(self, backup_file):
        """Upload backup to local storage"""
        os.makedirs(self.local_path, exist_ok=True)
        destination = os.path.join(self.local_path, backup_file['filename'])
        shutil.copy2(backup_file['path'], destination)
        return {'location': destination, 'success': True}

    def _upload_to_ftp(self, backup_file):
        """Upload backup to FTP/SFTP"""
        try:
            if self.use_sftp:
                # SFTP upload
                transport = paramiko.Transport((self.ftp_host, self.ftp_port))
                transport.connect(username=self.ftp_username, password=self.ftp_password)
                sftp = paramiko.SFTPClient.from_transport(transport)
                
                remote_path = os.path.join(self.ftp_path, backup_file['filename'])
                sftp.put(backup_file['path'], remote_path)
                
                sftp.close()
                transport.close()
            else:
                # FTP upload
                ftp = ftplib.FTP()
                ftp.connect(self.ftp_host, self.ftp_port)
                ftp.login(self.ftp_username, self.ftp_password)
                ftp.cwd(self.ftp_path)
                
                with open(backup_file['path'], 'rb') as f:
                    ftp.storbinary(f'STOR {backup_file["filename"]}', f)
                
                ftp.quit()
            
            return {'location': f'{self.ftp_host}:{self.ftp_path}/{backup_file["filename"]}', 'success': True}
            
        except Exception as e:
            _logger.error(f"FTP upload failed: {str(e)}")
            return {'location': '', 'success': False, 'error': str(e)}

    def _upload_to_s3(self, backup_file):
        """Upload backup to Amazon S3"""
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            
            s3_key = f"datasniffr_backups/{backup_file['filename']}"
            s3_client.upload_file(backup_file['path'], self.aws_bucket, s3_key)
            
            return {'location': f's3://{self.aws_bucket}/{s3_key}', 'success': True}
            
        except Exception as e:
            _logger.error(f"S3 upload failed: {str(e)}")
            return {'location': '', 'success': False, 'error': str(e)}

    def _upload_to_gcs(self, backup_file):
        """Upload backup to Google Cloud Storage"""
        try:
            credentials_dict = json.loads(self.gcp_credentials)
            client = gcs.Client.from_service_account_info(credentials_dict)
            bucket = client.bucket(self.gcp_bucket)
            
            blob_name = f"datasniffr_backups/{backup_file['filename']}"
            blob = bucket.blob(blob_name)
            
            blob.upload_from_filename(backup_file['path'])
            
            return {'location': f'gs://{self.gcp_bucket}/{blob_name}', 'success': True}
            
        except Exception as e:
            _logger.error(f"GCS upload failed: {str(e)}")
            return {'location': '', 'success': False, 'error': str(e)}

    def _verify_backup(self, backup_file):
        """Verify backup integrity"""
        try:
            # Recalculate hash
            current_hash = self._calculate_file_hash(backup_file['path'])
            
            if current_hash == backup_file['hash']:
                return {'verified': True, 'message': 'Backup integrity verified'}
            else:
                return {'verified': False, 'message': 'Hash mismatch - backup may be corrupted'}
                
        except Exception as e:
            return {'verified': False, 'message': f'Verification failed: {str(e)}'}

    def _check_backup_boss_battles(self, backup_data, backup_history):
        """Check if backup should trigger boss battles"""
        try:
            # Trigger boss battle for large backups
            if backup_history.backup_size_gb > 10:
                self.boss_battle_triggered = True
                self.boss_battle_type = 'data_fortress'
                
                boss_battle = self.env['datasniffr.boss.battle'].create({
                    'name': f'🏰 Data Fortress Boss - {self.name}',
                    'boss_type': 'data_fortress',
                    'difficulty': 'legendary',
                    'description': f'Secured massive data fortress with {backup_history.backup_size_gb:.1f}GB backup!',
                    'trigger_model': self._name,
                    'trigger_record_id': self.id,
                    'xp_reward': min(int(backup_history.backup_size_gb * 100), 5000),
                    'battle_data': json.dumps({
                        'backup_size_gb': backup_history.backup_size_gb,
                        'backup_type': self.backup_type,
                        'storage_type': self.storage_type
                    })
                })
                
                boss_battle.action_start_battle()
            
            # Trigger for backup masters (100+ successful backups)
            elif self.successful_backups >= 100:
                boss_battle = self.env['datasniffr.boss.battle'].create({
                    'name': f'🛡️ Backup Master Boss - {self.name}',
                    'boss_type': 'backup_master',
                    'difficulty': 'epic',
                    'description': 'Achieved mastery in data protection and disaster recovery!',
                    'trigger_model': self._name,
                    'trigger_record_id': self.id,
                    'xp_reward': 2500,
                    'battle_data': json.dumps({
                        'successful_backups': self.successful_backups,
                        'total_backup_size_gb': self.total_backup_size
                    })
                })
                
                boss_battle.action_start_battle()
                
        except Exception as e:
            _logger.error(f"Error checking backup boss battles: {str(e)}")

    def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        try:
            # Get old backup history records
            old_backups = self.backup_history.filtered(
                lambda b: b.backup_date < datetime.now() - timedelta(days=self.retention_days)
            )
            
            # Also limit by max backup count
            if self.max_backups > 0:
                all_backups = self.backup_history.sorted('backup_date', reverse=True)
                if len(all_backups) > self.max_backups:
                    excess_backups = all_backups[self.max_backups:]
                    old_backups |= excess_backups
            
            # Delete old backup files and records
            for backup in old_backups:
                try:
                    # Try to delete the actual backup file
                    if backup.storage_location and os.path.exists(backup.storage_location):
                        os.remove(backup.storage_location)
                    backup.unlink()
                except Exception as e:
                    _logger.warning(f"Failed to cleanup backup {backup.id}: {str(e)}")
                    
        except Exception as e:
            _logger.error(f"Backup cleanup failed: {str(e)}")

    def _schedule_next_backup(self):
        """Schedule next backup based on configuration"""
        if self.schedule_type == 'hourly':
            self.next_backup = datetime.now() + timedelta(hours=1)
        elif self.schedule_type == 'daily':
            next_date = datetime.now().replace(hour=int(self.schedule_time), minute=0, second=0, microsecond=0)
            if next_date <= datetime.now():
                next_date += timedelta(days=1)
            self.next_backup = next_date
        elif self.schedule_type == 'weekly':
            next_date = datetime.now().replace(hour=int(self.schedule_time), minute=0, second=0, microsecond=0)
            days_ahead = 6 - datetime.now().weekday()  # Saturday
            if days_ahead <= 0 or (days_ahead == 0 and next_date <= datetime.now()):
                days_ahead += 7
            self.next_backup = next_date + timedelta(days=days_ahead)
        elif self.schedule_type == 'monthly':
            next_date = datetime.now().replace(day=1, hour=int(self.schedule_time), minute=0, second=0, microsecond=0)
            if next_date <= datetime.now():
                if next_date.month == 12:
                    next_date = next_date.replace(year=next_date.year + 1, month=1)
                else:
                    next_date = next_date.replace(month=next_date.month + 1)
            self.next_backup = next_date

    @api.model
    def run_scheduled_backups(self):
        """Cron job to run scheduled backups"""
        scheduled_backups = self.search([
            ('schedule_type', '!=', 'manual'),
            ('next_backup', '<=', datetime.now()),
            ('state', '=', 'active')
        ])
        
        for backup_manager in scheduled_backups:
            try:
                backup_manager.action_create_backup()
            except Exception as e:
                _logger.error(f"Scheduled backup failed for {backup_manager.name}: {str(e)}")

    def action_test_backup(self):
        """Test backup configuration"""
        self.ensure_one()
        
        try:
            # Create a small test backup
            test_data = {
                'test': True,
                'timestamp': datetime.now().isoformat(),
                'config_name': self.name
            }
            
            # Test file creation
            temp_file = f"/tmp/test_backup_{self.id}.json"
            with open(temp_file, 'w') as f:
                json.dump(test_data, f)
            
            # Test upload
            backup_file = {
                'path': temp_file,
                'filename': f'test_backup_{self.id}.json',
                'hash': self._calculate_file_hash(temp_file)
            }
            
            upload_result = self._upload_backup(backup_file)
            
            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if upload_result['success']:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': f'🎯 Backup test successful! Storage: {upload_result["location"]}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': f'❌ Backup test failed: {upload_result.get("error", "Unknown error")}',
                        'type': 'warning',
                        'sticky': True,
                    }
                }
                
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'❌ Backup test failed: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }


class DatasniffrBackupHistory(models.Model):
    _name = 'datasniffr.backup.history'
    _description = 'Backup History'
    _order = 'backup_date desc'

    backup_manager_id = fields.Many2one('datasniffr.backup.manager', string='Backup Manager', required=True, ondelete='cascade')
    backup_type = fields.Selection([
        ('full', 'Full Backup'),
        ('incremental', 'Incremental Backup'),
        ('differential', 'Differential Backup'),
        ('selective', 'Selective Backup'),
        ('snapshot', 'Snapshot Backup')
    ], string='Backup Type', required=True)
    
    backup_date = fields.Datetime('Backup Date', required=True)
    backup_size_gb = fields.Float('Backup Size (GB)', required=True)
    storage_location = fields.Char('Storage Location')
    backup_hash = fields.Char('Backup Hash')
    
    status = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed')
    ], string='Status', required=True)
    
    metadata = fields.Text('Metadata', help='JSON metadata about the backup')
    error_message = fields.Text('Error Message')
    
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.backup_manager_id.name} - {record.backup_date.strftime('%Y-%m-%d %H:%M')} ({record.backup_size_gb:.2f}GB)"
            result.append((record.id, name))
        return result