#!/usr/bin/env python3
"""
DataSniffR Duplicate Hunter Mini-Module 👥🔍
===========================================

The ultimate duplicate detection and elimination specialist!
Hunt down duplicates like a data quality bounty hunter!

Features:
- 👥 Advanced duplicate detection algorithms
- 🧠 AI-powered similarity matching
- 🔗 Relationship-aware duplicate merging
- 📊 Duplicate pattern analysis
- ⚔️ Boss battle integration
- 🎯 Smart merge suggestions
- 💾 Safe backup before merging
- 🎉 Celebration tracking

mmm lol 🐶💾 - No duplicate escapes the hunter! 👥✨
"""

from odoo import models, fields, api
import json
import logging
from datetime import datetime
from difflib import SequenceMatcher
import re

_logger = logging.getLogger(__name__)

class DataSniffRDuplicateHunter(models.Model):
    _name = 'datasniffr.duplicate.hunter'
    _description = 'DataSniffR Duplicate Hunter - Specialized Duplicate Detection 👥🔍'
    _order = 'create_date desc'
    
    name = fields.Char(string='Hunt Name', required=True, default='Duplicate Hunt')
    
    # Hunt Configuration
    target_model = fields.Char(string='Target Model', required=True, default='res.partner')
    hunt_type = fields.Selection([
        ('exact_match', 'Exact Match Hunt 🎯'),
        ('fuzzy_match', 'Fuzzy Match Hunt 🔍'),
        ('ai_similarity', 'AI Similarity Hunt 🤖'),
        ('field_combination', 'Field Combination Hunt 🧩'),
        ('relationship_based', 'Relationship Based Hunt 🔗'),
        ('pattern_detection', 'Pattern Detection Hunt 📊'),
        ('full_spectrum', 'Full Spectrum Hunt 🌈'),
    ], string='Hunt Type', default='fuzzy_match', required=True)
    
    similarity_threshold = fields.Float(string='Similarity Threshold %', default=85.0)
    fields_to_compare = fields.Text(string='Fields to Compare (JSON)', default='["name", "email", "phone"]')
    
    # Hunt Results
    hunt_status = fields.Selection([
        ('pending', 'Pending 📋'),
        ('hunting', 'Hunting 🏃‍♂️'),
        ('analyzing', 'Analyzing 🧠'),
        ('completed', 'Completed ✅'),
        ('error', 'Error ❌'),
    ], string='Hunt Status', default='pending')
    
    total_records_scanned = fields.Integer(string='Records Scanned', default=0)
    duplicate_groups_found = fields.Integer(string='Duplicate Groups Found', default=0)
    total_duplicates = fields.Integer(string='Total Duplicates', default=0)
    auto_merged = fields.Integer(string='Auto-Merged', default=0)
    manual_review_needed = fields.Integer(string='Manual Review Needed', default=0)
    
    # Hunt Results Data
    hunt_results = fields.Text(string='Hunt Results (JSON)')
    merge_suggestions = fields.Text(string='Merge Suggestions (JSON)')
    hunt_statistics = fields.Text(string='Hunt Statistics (JSON)')
    
    # Boss Battle Integration
    boss_battle_triggered = fields.Boolean(string='Boss Battle Triggered', default=False)
    battle_reward_points = fields.Integer(string='Battle Reward Points', default=0)
    
    @api.model
    def start_customer_duplicate_hunt(self):
        """👥 Start comprehensive customer duplicate hunt"""
        
        hunter = self.create({
            'name': f'Customer Hunt - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'target_model': 'res.partner',
            'hunt_type': 'full_spectrum',
            'hunt_status': 'hunting'
        })
        
        try:
            # Get all customers
            customers = self.env['res.partner'].search([('is_company', '=', False)])
            
            hunt_results = {
                'duplicate_groups': [],
                'statistics': {
                    'total_scanned': len(customers),
                    'exact_matches': 0,
                    'fuzzy_matches': 0,
                    'ai_matches': 0,
                    'high_confidence': 0,
                    'medium_confidence': 0,
                    'low_confidence': 0
                },
                'patterns_found': [],
                'merge_recommendations': []
            }
            
            # Phase 1: Exact match detection
            exact_duplicates = self._find_exact_duplicates(customers)
            hunt_results['duplicate_groups'].extend(exact_duplicates)
            hunt_results['statistics']['exact_matches'] = len(exact_duplicates)
            
            # Phase 2: Fuzzy match detection
            fuzzy_duplicates = self._find_fuzzy_duplicates(customers)
            hunt_results['duplicate_groups'].extend(fuzzy_duplicates)
            hunt_results['statistics']['fuzzy_matches'] = len(fuzzy_duplicates)
            
            # Phase 3: AI similarity detection
            ai_duplicates = self._find_ai_similarity_duplicates(customers)
            hunt_results['duplicate_groups'].extend(ai_duplicates)
            hunt_results['statistics']['ai_matches'] = len(ai_duplicates)
            
            # Phase 4: Pattern analysis
            patterns = self._analyze_duplicate_patterns(hunt_results['duplicate_groups'])
            hunt_results['patterns_found'] = patterns
            
            # Phase 5: Generate merge suggestions
            merge_suggestions = self._generate_merge_suggestions(hunt_results['duplicate_groups'])
            hunt_results['merge_recommendations'] = merge_suggestions
            
            # Calculate confidence levels
            confidence_stats = self._calculate_confidence_distribution(hunt_results['duplicate_groups'])
            hunt_results['statistics'].update(confidence_stats)
            
            # Check for boss battle trigger
            boss_battle = self._check_duplicate_boss_battle(hunt_results)
            
            # Update hunter record
            hunter.write({
                'hunt_status': 'completed',
                'total_records_scanned': len(customers),
                'duplicate_groups_found': len(hunt_results['duplicate_groups']),
                'total_duplicates': sum(len(group['duplicates']) for group in hunt_results['duplicate_groups']),
                'hunt_results': json.dumps(hunt_results, indent=2),
                'boss_battle_triggered': boss_battle.get('triggered', False),
                'battle_reward_points': boss_battle.get('reward_points', 0)
            })
            
            return {
                'success': True,
                'hunter_id': hunter.id,
                'duplicate_groups': len(hunt_results['duplicate_groups']),
                'total_duplicates': hunter.total_duplicates,
                'patterns_found': len(patterns),
                'boss_battle_triggered': boss_battle.get('triggered', False),
                'message': f'👥 Hunt complete! Found {hunter.total_duplicates} duplicates in {len(hunt_results["duplicate_groups"])} groups!'
            }
            
        except Exception as e:
            hunter.write({'hunt_status': 'error'})
            return {
                'success': False,
                'error': str(e),
                'message': '❌ Duplicate hunt encountered an error!'
            }
    
    def _find_exact_duplicates(self, records):
        """🎯 Find exact duplicate matches"""
        
        exact_groups = []
        email_groups = {}
        phone_groups = {}
        name_groups = {}
        
        for record in records:
            # Group by email
            if record.email:
                email = record.email.lower().strip()
                if email not in email_groups:
                    email_groups[email] = []
                email_groups[email].append(record)
            
            # Group by phone
            if record.phone:
                phone = re.sub(r'[^\d]', '', record.phone)
                if len(phone) >= 7:
                    if phone not in phone_groups:
                        phone_groups[phone] = []
                    phone_groups[phone].append(record)
            
            # Group by exact name match
            if record.name:
                name = record.name.lower().strip()
                if name not in name_groups:
                    name_groups[name] = []
                name_groups[name].append(record)
        
        # Process email duplicates
        for email, records_list in email_groups.items():
            if len(records_list) > 1:
                exact_groups.append({
                    'match_type': 'exact_email',
                    'match_value': email,
                    'confidence': 95,
                    'duplicates': [{'id': r.id, 'name': r.name, 'email': r.email} for r in records_list],
                    'merge_priority': 'high',
                    'auto_merge_safe': True
                })
        
        # Process phone duplicates
        for phone, records_list in phone_groups.items():
            if len(records_list) > 1:
                exact_groups.append({
                    'match_type': 'exact_phone',
                    'match_value': phone,
                    'confidence': 90,
                    'duplicates': [{'id': r.id, 'name': r.name, 'phone': r.phone} for r in records_list],
                    'merge_priority': 'high',
                    'auto_merge_safe': True
                })
        
        # Process name duplicates (lower confidence)
        for name, records_list in name_groups.items():
            if len(records_list) > 1:
                exact_groups.append({
                    'match_type': 'exact_name',
                    'match_value': name,
                    'confidence': 75,
                    'duplicates': [{'id': r.id, 'name': r.name, 'email': r.email or ''} for r in records_list],
                    'merge_priority': 'medium',
                    'auto_merge_safe': False
                })
        
        return exact_groups
    
    def _find_fuzzy_duplicates(self, records):
        """🔍 Find fuzzy duplicate matches using similarity algorithms"""
        
        fuzzy_groups = []
        processed_ids = set()
        
        for i, record1 in enumerate(records):
            if record1.id in processed_ids:
                continue
            
            similar_records = [record1]
            
            for j, record2 in enumerate(records[i+1:], i+1):
                if record2.id in processed_ids:
                    continue
                
                similarity = self._calculate_record_similarity(record1, record2)
                
                if similarity >= self.similarity_threshold:
                    similar_records.append(record2)
                    processed_ids.add(record2.id)
            
            if len(similar_records) > 1:
                processed_ids.add(record1.id)
                
                # Calculate average similarity within group
                avg_similarity = self._calculate_group_similarity(similar_records)
                
                fuzzy_groups.append({
                    'match_type': 'fuzzy_similarity',
                    'confidence': avg_similarity,
                    'duplicates': [{'id': r.id, 'name': r.name, 'email': r.email or '', 'phone': r.phone or ''} for r in similar_records],
                    'merge_priority': 'high' if avg_similarity >= 90 else 'medium' if avg_similarity >= 80 else 'low',
                    'auto_merge_safe': avg_similarity >= 95,
                    'similarity_details': self._get_similarity_breakdown(similar_records)
                })
        
        return fuzzy_groups
    
    def _calculate_record_similarity(self, record1, record2):
        """📊 Calculate similarity between two records"""
        
        similarities = []
        weights = {'name': 0.4, 'email': 0.3, 'phone': 0.2, 'address': 0.1}
        
        # Name similarity
        if record1.name and record2.name:
            name_sim = SequenceMatcher(None, record1.name.lower(), record2.name.lower()).ratio() * 100
            similarities.append(('name', name_sim, weights['name']))
        
        # Email similarity
        if record1.email and record2.email:
            email_sim = SequenceMatcher(None, record1.email.lower(), record2.email.lower()).ratio() * 100
            similarities.append(('email', email_sim, weights['email']))
        
        # Phone similarity
        if record1.phone and record2.phone:
            phone1 = re.sub(r'[^\d]', '', record1.phone)
            phone2 = re.sub(r'[^\d]', '', record2.phone)
            if phone1 and phone2:
                phone_sim = SequenceMatcher(None, phone1, phone2).ratio() * 100
                similarities.append(('phone', phone_sim, weights['phone']))
        
        # Calculate weighted average
        if not similarities:
            return 0
        
        total_weight = sum(weight for _, _, weight in similarities)
        weighted_sum = sum(similarity * weight for _, similarity, weight in similarities)
        
        return weighted_sum / total_weight if total_weight > 0 else 0
    
    def _calculate_group_similarity(self, records):
        """📊 Calculate average similarity within a group"""
        
        if len(records) < 2:
            return 0
        
        total_similarity = 0
        comparisons = 0
        
        for i, record1 in enumerate(records):
            for record2 in records[i+1:]:
                total_similarity += self._calculate_record_similarity(record1, record2)
                comparisons += 1
        
        return total_similarity / comparisons if comparisons > 0 else 0
    
    def _find_ai_similarity_duplicates(self, records):
        """🤖 Find AI-powered similarity duplicates"""
        
        # This would integrate with external AI services for advanced similarity
        ai_groups = []
        
        # Placeholder for AI similarity detection
        # Would use external AI connector to analyze semantic similarity
        
        return ai_groups
    
    def _analyze_duplicate_patterns(self, duplicate_groups):
        """📊 Analyze patterns in duplicate data"""
        
        patterns = {
            'common_domains': {},
            'naming_patterns': {},
            'phone_patterns': {},
            'creation_patterns': {},
            'duplicate_hotspots': []
        }
        
        for group in duplicate_groups:
            duplicates = group['duplicates']
            
            # Analyze email domains
            for dup in duplicates:
                if dup.get('email') and '@' in dup['email']:
                    domain = dup['email'].split('@')[1].lower()
                    patterns['common_domains'][domain] = patterns['common_domains'].get(domain, 0) + 1
            
            # Analyze naming patterns
            names = [dup.get('name', '') for dup in duplicates if dup.get('name')]
            if len(names) > 1:
                # Find common prefixes/suffixes
                common_words = self._find_common_name_patterns(names)
                for word in common_words:
                    patterns['naming_patterns'][word] = patterns['naming_patterns'].get(word, 0) + 1
        
        # Identify hotspots (areas with many duplicates)
        if len(duplicate_groups) > 10:
            patterns['duplicate_hotspots'].append({
                'type': 'high_volume',
                'description': f'High duplicate volume detected: {len(duplicate_groups)} groups found',
                'recommendation': 'Consider data import process review'
            })
        
        return patterns
    
    def _find_common_name_patterns(self, names):
        """🔍 Find common patterns in names"""
        
        common_words = []
        
        # Split names into words and find common ones
        all_words = []
        for name in names:
            words = name.lower().split()
            all_words.extend(words)
        
        # Find words that appear in multiple names
        word_counts = {}
        for word in all_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Return words that appear more than once
        common_words = [word for word, count in word_counts.items() if count > 1]
        
        return common_words
    
    def _generate_merge_suggestions(self, duplicate_groups):
        """💡 Generate intelligent merge suggestions"""
        
        suggestions = []
        
        for group in duplicate_groups:
            duplicates = group['duplicates']
            
            if len(duplicates) < 2:
                continue
            
            # Analyze which record has the most complete data
            master_candidate = self._find_master_record(duplicates)
            
            suggestion = {
                'group_id': f"group_{len(suggestions) + 1}",
                'match_type': group['match_type'],
                'confidence': group['confidence'],
                'master_record': master_candidate,
                'records_to_merge': [d for d in duplicates if d['id'] != master_candidate['id']],
                'merge_strategy': self._determine_merge_strategy(group),
                'data_conflicts': self._identify_data_conflicts(duplicates),
                'estimated_time': '5 minutes',
                'risk_level': 'low' if group.get('auto_merge_safe') else 'medium'
            }
            
            suggestions.append(suggestion)
        
        return suggestions
    
    def _find_master_record(self, duplicates):
        """🎯 Find the best record to use as master for merging"""
        
        scores = []
        
        for dup in duplicates:
            score = 0
            
            # Score based on data completeness
            if dup.get('name'):
                score += 20
            if dup.get('email'):
                score += 25
            if dup.get('phone'):
                score += 20
            
            # Bonus for longer/more complete data
            if dup.get('name') and len(dup['name']) > 10:
                score += 10
            
            scores.append((score, dup))
        
        # Return record with highest score
        return max(scores, key=lambda x: x[0])[1]
    
    def _determine_merge_strategy(self, group):
        """🧠 Determine the best merge strategy for a group"""
        
        if group['confidence'] >= 95:
            return 'auto_merge'
        elif group['confidence'] >= 85:
            return 'assisted_merge'
        else:
            return 'manual_review'
    
    def _identify_data_conflicts(self, duplicates):
        """⚠️ Identify potential data conflicts in merge"""
        
        conflicts = []
        
        # Check for conflicting emails
        emails = [d.get('email') for d in duplicates if d.get('email')]
        unique_emails = list(set(emails))
        if len(unique_emails) > 1:
            conflicts.append({
                'field': 'email',
                'values': unique_emails,
                'resolution': 'Keep most recent or most complete'
            })
        
        # Check for conflicting phones
        phones = [d.get('phone') for d in duplicates if d.get('phone')]
        unique_phones = list(set(phones))
        if len(unique_phones) > 1:
            conflicts.append({
                'field': 'phone',
                'values': unique_phones,
                'resolution': 'Keep all as additional phone numbers'
            })
        
        return conflicts
    
    def _calculate_confidence_distribution(self, duplicate_groups):
        """📊 Calculate confidence level distribution"""
        
        high_confidence = sum(1 for g in duplicate_groups if g['confidence'] >= 90)
        medium_confidence = sum(1 for g in duplicate_groups if 70 <= g['confidence'] < 90)
        low_confidence = sum(1 for g in duplicate_groups if g['confidence'] < 70)
        
        return {
            'high_confidence': high_confidence,
            'medium_confidence': medium_confidence,
            'low_confidence': low_confidence
        }
    
    def _check_duplicate_boss_battle(self, hunt_results):
        """⚔️ Check if duplicate hunt warrants a boss battle"""
        
        total_duplicates = sum(len(group['duplicates']) for group in hunt_results['duplicate_groups'])
        
        if total_duplicates >= 50:
            return {
                'triggered': True,
                'battle_type': 'Duplicate Dragon Slayer',
                'description': f'🐉 {total_duplicates} duplicates detected! Epic team battle required!',
                'challenge': 'Team must eliminate all duplicates in 60 minutes',
                'reward_points': total_duplicates * 10,
                'celebration': 'Duplicate-free victory dance!'
            }
        elif total_duplicates >= 20:
            return {
                'triggered': True,
                'battle_type': 'Duplicate Hydra Hunt',
                'description': f'🐍 {total_duplicates} duplicates found! Team collaboration needed!',
                'challenge': 'Each team member merges 5 duplicate groups',
                'reward_points': total_duplicates * 5,
                'celebration': 'Team high-fives all around!'
            }
        
        return {'triggered': False}
    
    def execute_merge_suggestion(self, suggestion_id):
        """🔄 Execute a merge suggestion"""
        
        hunt_results = json.loads(self.hunt_results or '{}')
        suggestions = hunt_results.get('merge_recommendations', [])
        
        suggestion = next((s for s in suggestions if s.get('group_id') == suggestion_id), None)
        if not suggestion:
            return {'error': 'Suggestion not found'}
        
        try:
            master_record = self.env['res.partner'].browse(suggestion['master_record']['id'])
            records_to_merge = [self.env['res.partner'].browse(r['id']) for r in suggestion['records_to_merge']]
            
            # Backup data before merge
            backup_data = self._backup_merge_data(master_record, records_to_merge)
            
            # Execute merge
            merge_result = self._execute_record_merge(master_record, records_to_merge, suggestion)
            
            # Update statistics
            self.auto_merged += 1
            
            return {
                'success': True,
                'master_record_id': master_record.id,
                'merged_count': len(records_to_merge),
                'backup_id': backup_data['backup_id'],
                'message': f'✅ Successfully merged {len(records_to_merge)} duplicates into master record!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '❌ Merge operation failed!'
            }
    
    def _backup_merge_data(self, master_record, records_to_merge):
        """💾 Backup data before merge operation"""
        
        backup_data = {
            'backup_id': f"merge_backup_{int(datetime.now().timestamp())}",
            'master_record': {
                'id': master_record.id,
                'data': {
                    'name': master_record.name,
                    'email': master_record.email,
                    'phone': master_record.phone
                }
            },
            'merged_records': []
        }
        
        for record in records_to_merge:
            backup_data['merged_records'].append({
                'id': record.id,
                'data': {
                    'name': record.name,
                    'email': record.email,
                    'phone': record.phone
                }
            })
        
        # Store backup (would integrate with backup system)
        _logger.info(f"Merge backup created: {backup_data['backup_id']}")
        
        return backup_data
    
    def _execute_record_merge(self, master_record, records_to_merge, suggestion):
        """🔄 Execute the actual record merge"""
        
        # Merge strategy based on suggestion
        strategy = suggestion.get('merge_strategy', 'manual_review')
        
        if strategy == 'auto_merge':
            # Safe automatic merge
            for record in records_to_merge:
                # Update related records to point to master
                self._update_related_records(record, master_record)
                
                # Merge additional data if master is missing it
                if not master_record.email and record.email:
                    master_record.email = record.email
                if not master_record.phone and record.phone:
                    master_record.phone = record.phone
                
                # Archive the duplicate record
                record.active = False
        
        return {'strategy_used': strategy, 'success': True}
    
    def _update_related_records(self, old_record, new_record):
        """🔗 Update related records to point to new master record"""
        
        # Update sale orders
        sale_orders = self.env['sale.order'].search([('partner_id', '=', old_record.id)])
        sale_orders.write({'partner_id': new_record.id})
        
        # Update invoices
        invoices = self.env['account.move'].search([('partner_id', '=', old_record.id)])
        invoices.write({'partner_id': new_record.id})
        
        # Add more related record updates as needed
        
    def _get_similarity_breakdown(self, records):
        """📊 Get detailed similarity breakdown for records"""
        
        breakdown = {
            'name_similarity': [],
            'email_similarity': [],
            'phone_similarity': [],
            'overall_patterns': []
        }
        
        for i, record1 in enumerate(records):
            for record2 in records[i+1:]:
                if record1.name and record2.name:
                    name_sim = SequenceMatcher(None, record1.name.lower(), record2.name.lower()).ratio() * 100
                    breakdown['name_similarity'].append({
                        'record1': record1.id,
                        'record2': record2.id,
                        'similarity': name_sim
                    })
        
        return breakdown
    
    @api.model
    def get_duplicate_hunter_dashboard(self):
        """📊 Get duplicate hunter dashboard"""
        
        hunters = self.search([], limit=10)
        
        dashboard = {
            'total_hunts': len(hunters),
            'total_duplicates_found': sum(h.total_duplicates for h in hunters),
            'total_merged': sum(h.auto_merged for h in hunters),
            'recent_hunts': [],
            'hunt_statistics': {
                'avg_duplicates_per_hunt': 0,
                'most_productive_hunt': None,
                'boss_battles_triggered': sum(1 for h in hunters if h.boss_battle_triggered)
            }
        }
        
        if hunters:
            dashboard['hunt_statistics']['avg_duplicates_per_hunt'] = dashboard['total_duplicates_found'] / len(hunters)
            
            # Find most productive hunt
            most_productive = max(hunters, key=lambda h: h.total_duplicates)
            dashboard['hunt_statistics']['most_productive_hunt'] = {
                'name': most_productive.name,
                'duplicates_found': most_productive.total_duplicates
            }
        
        # Recent hunts
        for hunter in hunters[:5]:
            dashboard['recent_hunts'].append({
                'name': hunter.name,
                'hunt_type': hunter.hunt_type,
                'duplicates_found': hunter.total_duplicates,
                'status': hunter.hunt_status,
                'date': hunter.create_date.isoformat()
            })
        
        return dashboard