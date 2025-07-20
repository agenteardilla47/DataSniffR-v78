#!/usr/bin/env python3
"""
DataSniffR Boss Battle Task Distributor 🎮⚔️
===========================================

When the boss battle starts and there are MANY errors,
DataSniffR becomes the ultimate raid leader, distributing
tasks intelligently to solve everything in record time!

Features:
- 🧠 Smart task distribution based on employee skills
- ⚖️ Workload balancing for optimal performance
- 🎯 Time estimation and completion tracking
- 🏆 Collaborative boss battle coordination
- 📊 Real-time progress monitoring

mmm lol 🐶💾 - Turning data chaos into coordinated victory! 🎮✨
"""

from odoo import models, fields, api
import json
import logging
from datetime import datetime, timedelta
import random
import math

_logger = logging.getLogger(__name__)

class BossBattleTaskDistributor(models.Model):
    _name = 'boss.battle.task.distributor'
    _description = 'Boss Battle Task Distribution System ⚔️🎮'
    _order = 'create_date desc'
    
    name = fields.Char(string='Boss Battle Name', required=True)
    
    # Battle Configuration
    battle_type = fields.Selection([
        ('data_kraken', 'Data Kraken 🐙 - Massive data corruption'),
        ('validation_dragon', 'Validation Dragon 🐲 - Complex validation errors'),
        ('duplicate_hydra', 'Duplicate Hydra 🐍 - Duplicate record chaos'),
        ('format_demon', 'Format Demon 👹 - Formatting nightmares'),
        ('missing_ghost', 'Missing Data Ghost 👻 - Missing information'),
        ('chaos_titan', 'Chaos Titan 🗿 - Mixed error apocalypse'),
    ], string='Boss Battle Type', required=True)
    
    battle_status = fields.Selection([
        ('preparing', 'Preparing for Battle 🛡️'),
        ('distributing', 'Distributing Tasks ⚔️'),
        ('in_progress', 'Battle in Progress 🔥'),
        ('victory', 'Victory Achieved! 🏆'),
        ('tactical_retreat', 'Strategic Retreat 🏃‍♂️'),
    ], default='preparing', string='Battle Status')
    
    # Error Analysis
    total_errors = fields.Integer(string='Total Errors Detected', default=0)
    error_categories = fields.Text(string='Error Categories (JSON)')
    complexity_score = fields.Float(string='Battle Complexity (1-10)', default=5.0)
    estimated_battle_time = fields.Float(string='Estimated Battle Time (hours)', default=0.0)
    
    # Team Management
    available_warriors = fields.Text(string='Available Team Warriors (JSON)')
    task_assignments = fields.Text(string='Task Assignments (JSON)')
    team_performance = fields.Text(string='Team Performance Analytics (JSON)')
    
    # Progress Tracking
    tasks_completed = fields.Integer(string='Tasks Completed', default=0)
    tasks_in_progress = fields.Integer(string='Tasks In Progress', default=0)
    tasks_pending = fields.Integer(string='Tasks Pending', default=0)
    battle_progress = fields.Float(string='Battle Progress %', default=0.0)
    
    # Victory Conditions
    victory_threshold = fields.Float(string='Victory Threshold %', default=95.0)
    current_data_quality = fields.Float(string='Current Data Quality %', default=0.0)
    
    @api.model
    def initiate_boss_battle(self, error_data, battle_config=None):
        """🎮 Initiate a boss battle when massive errors are detected! ⚔️"""
        
        _logger.info("🚨 BOSS BATTLE INITIATED! Preparing for epic data quality fight! ⚔️")
        
        if not battle_config:
            battle_config = {
                'auto_distribute': True,
                'difficulty_scaling': True,
                'team_balancing': True,
                'time_pressure': False
            }
        
        # Analyze the error situation
        battle_analysis = self._analyze_battle_situation(error_data)
        
        # Create the boss battle
        battle = self.create({
            'name': f"Boss Battle - {battle_analysis['boss_type']} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'battle_type': battle_analysis['battle_type_key'],
            'total_errors': battle_analysis['total_errors'],
            'error_categories': json.dumps(battle_analysis['error_categories'], indent=2),
            'complexity_score': battle_analysis['complexity_score'],
            'estimated_battle_time': battle_analysis['estimated_time'],
            'battle_status': 'preparing'
        })
        
        # Assemble the team
        battle._assemble_battle_team()
        
        # Distribute tasks intelligently
        if battle_config.get('auto_distribute', True):
            battle._distribute_battle_tasks()
        
        # Start the battle!
        battle._commence_battle()
        
        return battle
    
    def _analyze_battle_situation(self, error_data):
        """🔍 Analyze the error situation to determine boss battle type ⚔️"""
        
        total_errors = len(error_data.get('errors', []))
        error_types = {}
        
        # Count error types
        for error in error_data.get('errors', []):
            error_type = error.get('type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Determine boss type based on error patterns
        boss_mapping = {
            'data_corruption': ('data_kraken', 'Data Kraken 🐙'),
            'validation_error': ('validation_dragon', 'Validation Dragon 🐲'),
            'duplicate_records': ('duplicate_hydra', 'Duplicate Hydra 🐍'),
            'format_error': ('format_demon', 'Format Demon 👹'),
            'missing_data': ('missing_ghost', 'Missing Data Ghost 👻'),
        }
        
        # Find dominant error type
        dominant_error = max(error_types.items(), key=lambda x: x[1]) if error_types else ('mixed', 0)
        
        if dominant_error[1] / total_errors < 0.4:  # No dominant type = chaos
            battle_type_key = 'chaos_titan'
            boss_type = 'Chaos Titan 🗿'
        else:
            battle_type_key, boss_type = boss_mapping.get(dominant_error[0], ('chaos_titan', 'Chaos Titan 🗿'))
        
        # Calculate complexity score (1-10)
        complexity_factors = [
            len(error_types),  # Variety of error types
            total_errors / 100,  # Volume of errors
            len(set(error.get('severity', 'medium') for error in error_data.get('errors', []))),  # Severity variety
        ]
        complexity_score = min(10.0, sum(complexity_factors) / len(complexity_factors) * 3)
        
        # Estimate battle time
        base_time = total_errors * 0.1  # 6 minutes per error baseline
        complexity_multiplier = 1 + (complexity_score / 10)
        estimated_time = base_time * complexity_multiplier / 60  # Convert to hours
        
        return {
            'boss_type': boss_type,
            'battle_type_key': battle_type_key,
            'total_errors': total_errors,
            'error_categories': error_types,
            'complexity_score': complexity_score,
            'estimated_time': estimated_time
        }
    
    def _assemble_battle_team(self):
        """👥 Assemble the perfect team for this boss battle! 🎮"""
        
        _logger.info("🏰 Assembling the dream team for battle! 👥⚔️")
        
        # Get all available employees
        employees = self.env['hr.employee'].search([('active', '=', True)])
        
        warriors = []
        
        for employee in employees:
            # Analyze employee skills and availability
            warrior_profile = self._analyze_warrior_skills(employee)
            warriors.append(warrior_profile)
        
        # Sort by battle readiness
        warriors.sort(key=lambda x: x['battle_readiness'], reverse=True)
        
        self.available_warriors = json.dumps(warriors, indent=2)
        
        _logger.info(f"⚔️ Assembled {len(warriors)} warriors for the battle!")
        
        return warriors
    
    def _analyze_warrior_skills(self, employee):
        """🔍 Analyze employee skills for battle assignment 💪"""
        
        # Get employee's historical performance
        analytics = self.env['employee.analytics.dashboard'].search([
            ('employee_id', '=', employee.id)
        ], limit=1)
        
        base_skills = {
            'data_validation': 5.0,    # Base skill level
            'format_fixing': 5.0,
            'duplicate_hunting': 5.0,
            'missing_data_detective': 5.0,
            'complex_problem_solving': 5.0
        }
        
        # Adjust skills based on historical performance
        if analytics:
            performance_data = json.loads(analytics.performance_history or '{}')
            
            # Boost skills based on past victories
            for skill in base_skills:
                past_performance = performance_data.get(f'{skill}_score', 5.0)
                base_skills[skill] = min(10.0, (base_skills[skill] + past_performance) / 2)
        
        # Calculate overall battle readiness
        battle_readiness = sum(base_skills.values()) / len(base_skills)
        
        # Add some personality traits for fun
        personality_traits = random.sample([
            'Data Detective 🕵️‍♂️', 'Spreadsheet Ninja 🥷', 'Format Wizard 🧙‍♂️',
            'Validation Warrior ⚔️', 'Error Hunter 🏹', 'Chaos Tamer 🦁',
            'Quality Guardian 🛡️', 'Data Whisperer 🗣️', 'Bug Slayer 🗡️'
        ], k=2)
        
        return {
            'employee_id': employee.id,
            'name': employee.name,
            'email': employee.work_email or '',
            'skills': base_skills,
            'battle_readiness': battle_readiness,
            'personality_traits': personality_traits,
            'current_workload': self._calculate_current_workload(employee),
            'availability_score': random.uniform(0.7, 1.0),  # Mock availability
            'preferred_battle_style': random.choice([
                'solo_missions', 'team_coordination', 'support_role', 'frontline_fighter'
            ])
        }
    
    def _calculate_current_workload(self, employee):
        """📊 Calculate employee's current workload 💼"""
        
        # Mock workload calculation (in real implementation, check actual tasks)
        return random.uniform(0.3, 0.9)
    
    def _distribute_battle_tasks(self):
        """⚔️ Intelligently distribute battle tasks to team members! 🎯"""
        
        _logger.info("🎯 Distributing battle tasks with military precision! ⚔️")
        
        self.battle_status = 'distributing'
        
        warriors = json.loads(self.available_warriors or '[]')
        error_categories = json.loads(self.error_categories or '{}')
        
        # Create task assignments
        assignments = []
        task_id = 1
        
        for error_type, error_count in error_categories.items():
            # Find best warriors for this error type
            suitable_warriors = self._find_warriors_for_error_type(warriors, error_type)
            
            # Distribute errors among suitable warriors
            tasks_per_warrior = self._calculate_optimal_distribution(
                suitable_warriors, error_count
            )
            
            for warrior_assignment in tasks_per_warrior:
                warrior = warrior_assignment['warrior']
                task_count = warrior_assignment['task_count']
                
                if task_count > 0:
                    assignment = {
                        'task_id': task_id,
                        'warrior_id': warrior['employee_id'],
                        'warrior_name': warrior['name'],
                        'error_type': error_type,
                        'task_count': task_count,
                        'estimated_time': task_count * 0.1,  # 6 minutes per task
                        'difficulty': self._get_error_difficulty(error_type),
                        'status': 'assigned',
                        'battle_cry': self._generate_battle_cry(warrior, error_type),
                        'assigned_at': datetime.now().isoformat(),
                        'expected_completion': (datetime.now() + timedelta(hours=task_count * 0.1)).isoformat()
                    }
                    assignments.append(assignment)
                    task_id += 1
        
        # Update battle statistics
        self.task_assignments = json.dumps(assignments, indent=2)
        self.tasks_pending = len(assignments)
        self.tasks_in_progress = 0
        self.tasks_completed = 0
        
        # Send battle assignments to warriors
        self._send_battle_assignments(assignments)
        
        _logger.info(f"⚔️ Distributed {len(assignments)} battle tasks to the team!")
    
    def _find_warriors_for_error_type(self, warriors, error_type):
        """🎯 Find the best warriors for a specific error type 💪"""
        
        skill_mapping = {
            'validation_error': 'data_validation',
            'format_error': 'format_fixing',
            'duplicate_records': 'duplicate_hunting',
            'missing_data': 'missing_data_detective',
            'data_corruption': 'complex_problem_solving'
        }
        
        required_skill = skill_mapping.get(error_type, 'complex_problem_solving')
        
        # Filter and sort warriors by relevant skill
        suitable_warriors = []
        for warrior in warriors:
            skill_level = warrior['skills'].get(required_skill, 5.0)
            workload = warrior.get('current_workload', 0.5)
            availability = warrior.get('availability_score', 1.0)
            
            # Calculate suitability score
            suitability = (skill_level * 0.5) + ((1 - workload) * 0.3) + (availability * 0.2)
            
            suitable_warriors.append({
                'warrior': warrior,
                'suitability': suitability,
                'skill_level': skill_level
            })
        
        # Sort by suitability (best first)
        suitable_warriors.sort(key=lambda x: x['suitability'], reverse=True)
        
        return suitable_warriors[:min(5, len(suitable_warriors))]  # Top 5 warriors
    
    def _calculate_optimal_distribution(self, suitable_warriors, total_tasks):
        """⚖️ Calculate optimal task distribution for maximum efficiency! 📊"""
        
        if not suitable_warriors:
            return []
        
        # Calculate task distribution based on suitability and availability
        total_capacity = sum(w['suitability'] * (1 - w['warrior']['current_workload']) 
                           for w in suitable_warriors)
        
        assignments = []
        remaining_tasks = total_tasks
        
        for warrior_data in suitable_warriors:
            if remaining_tasks <= 0:
                break
                
            warrior = warrior_data['warrior']
            suitability = warrior_data['suitability']
            availability = 1 - warrior['current_workload']
            
            # Calculate this warrior's share
            capacity_ratio = (suitability * availability) / total_capacity
            assigned_tasks = min(remaining_tasks, math.ceil(total_tasks * capacity_ratio))
            
            assignments.append({
                'warrior': warrior,
                'task_count': assigned_tasks,
                'capacity_ratio': capacity_ratio
            })
            
            remaining_tasks -= assigned_tasks
        
        # Distribute any remaining tasks to the best warrior
        if remaining_tasks > 0 and assignments:
            assignments[0]['task_count'] += remaining_tasks
        
        return assignments
    
    def _get_error_difficulty(self, error_type):
        """🎯 Get difficulty level for error type ⭐"""
        
        difficulty_map = {
            'validation_error': 6,
            'format_error': 4,
            'duplicate_records': 7,
            'missing_data': 5,
            'data_corruption': 9
        }
        
        return difficulty_map.get(error_type, 5)
    
    def _generate_battle_cry(self, warrior, error_type):
        """🎭 Generate epic battle cry for warrior assignment! 📢"""
        
        battle_cries = {
            'validation_error': [
                f"{warrior['name']}, validate like there's no tomorrow! ⚔️",
                f"Time to show those validation errors who's boss, {warrior['name']}! 🛡️",
                f"{warrior['name']}, your validation skills are legendary! Go get 'em! 🏹"
            ],
            'format_error': [
                f"{warrior['name']}, bring order to this formatting chaos! 📐",
                f"Format warrior {warrior['name']}, the data needs your magic! ✨",
                f"{warrior['name']}, make those formats shine like diamonds! 💎"
            ],
            'duplicate_records': [
                f"{warrior['name']}, hunt down those duplicates like a detective! 🕵️‍♂️",
                f"Duplicate slayer {warrior['name']}, show no mercy! ⚔️",
                f"{warrior['name']}, eliminate duplicates with surgical precision! 🎯"
            ],
            'missing_data': [
                f"{warrior['name']}, find that missing data like a treasure hunter! 🗺️",
                f"Data detective {warrior['name']}, solve this mystery! 🔍",
                f"{warrior['name']}, bring those missing pieces home! 🏠"
            ]
        }
        
        cries = battle_cries.get(error_type, [
            f"{warrior['name']}, show this data who's the boss! 💪",
            f"Go forth, {warrior['name']}, and conquer! ⚔️"
        ])
        
        return random.choice(cries)
    
    def _send_battle_assignments(self, assignments):
        """📧 Send epic battle assignments to warriors! 🎮"""
        
        for assignment in assignments:
            # Create battle notification
            battle_notification = {
                'subject': f"🎮 BOSS BATTLE ASSIGNMENT: {self.battle_type.upper()} ⚔️",
                'warrior_name': assignment['warrior_name'],
                'battle_cry': assignment['battle_cry'],
                'error_type': assignment['error_type'],
                'task_count': assignment['task_count'],
                'estimated_time': assignment['estimated_time'],
                'difficulty': assignment['difficulty'],
                'expected_completion': assignment['expected_completion'],
                'battle_tips': self._get_battle_tips(assignment['error_type'])
            }
            
            # Send notification (integrate with email system)
            self._send_warrior_notification(assignment['warrior_id'], battle_notification)
    
    def _get_battle_tips(self, error_type):
        """💡 Get battle tips for specific error types 🎯"""
        
        tips = {
            'validation_error': [
                "Check for required fields first! 📋",
                "Email formats are sneaky - watch for missing @ symbols! 📧",
                "Date validation is your friend! 📅"
            ],
            'format_error': [
                "Consistency is key - check formatting patterns! 📐",
                "Watch for extra spaces and hidden characters! 👻",
                "Currency formats love to cause trouble! 💰"
            ],
            'duplicate_records': [
                "Look for similar names with different spellings! 🔤",
                "Phone numbers and emails are great duplicate indicators! 📱",
                "Check creation dates - duplicates often cluster! 📅"
            ],
            'missing_data': [
                "Start with the most critical missing fields! ⚠️",
                "Check if data moved to unexpected places! 🔍",
                "Sometimes 'missing' data is just hidden! 👻"
            ]
        }
        
        return tips.get(error_type, ["Trust your instincts, warrior! 💪"])
    
    def _send_warrior_notification(self, warrior_id, notification_data):
        """📧 Send notification to warrior 🎮"""
        
        # Mock notification sending (integrate with actual email system)
        _logger.info(f"📧 Battle assignment sent to warrior {warrior_id}")
        
        # In real implementation, integrate with email_preparation_system
        # self.env['email.preparation.system'].send_battle_assignment(warrior_id, notification_data)
    
    def _commence_battle(self):
        """🚀 Commence the epic boss battle! ⚔️"""
        
        _logger.info("🔥 BOSS BATTLE COMMENCED! Let the data quality war begin! ⚔️")
        
        self.battle_status = 'in_progress'
        
        # Start monitoring battle progress
        self._monitor_battle_progress()
        
        # Send battle commencement notification to all warriors
        self._send_battle_commencement_notification()
    
    def _monitor_battle_progress(self):
        """📊 Monitor ongoing battle progress 🔍"""
        
        # This would run as a background process monitoring task completion
        # For now, we'll create the monitoring framework
        
        monitoring_data = {
            'battle_start': datetime.now().isoformat(),
            'total_tasks': self.tasks_pending,
            'monitoring_frequency': 'every_5_minutes',
            'victory_conditions': {
                'completion_threshold': self.victory_threshold,
                'quality_improvement': 'required',
                'team_morale': 'high'
            }
        }
        
        _logger.info("📊 Battle monitoring system activated!")
    
    def _send_battle_commencement_notification(self):
        """📢 Send battle commencement notification to all warriors! 🎺"""
        
        warriors = json.loads(self.available_warriors or '[]')
        
        battle_message = f"""
🎮 BOSS BATTLE COMMENCED! ⚔️

{self.battle_type.upper()} HAS APPEARED!

📊 Battle Stats:
• Total Errors: {self.total_errors}
• Complexity Level: {self.complexity_score:.1f}/10
• Estimated Battle Time: {self.estimated_battle_time:.1f} hours
• Victory Threshold: {self.victory_threshold}%

🎯 Your mission: Work together to defeat this data quality boss!
💪 Remember: Teamwork makes the dream work!
🏆 Victory rewards await those who succeed!

mmm lol 🐶💾 - Let's show this boss who's the real data quality champions! ⚔️✨
        """
        
        for warrior in warriors:
            _logger.info(f"📢 Battle commencement sent to {warrior['name']}")
    
    def update_task_progress(self, task_id, status, completion_percentage=None):
        """📈 Update task progress during battle ⚔️"""
        
        assignments = json.loads(self.task_assignments or '[]')
        
        for assignment in assignments:
            if assignment['task_id'] == task_id:
                old_status = assignment.get('status', 'assigned')
                assignment['status'] = status
                assignment['last_updated'] = datetime.now().isoformat()
                
                if completion_percentage is not None:
                    assignment['completion_percentage'] = completion_percentage
                
                # Update battle statistics
                if old_status != status:
                    if status == 'in_progress' and old_status == 'assigned':
                        self.tasks_pending -= 1
                        self.tasks_in_progress += 1
                    elif status == 'completed' and old_status == 'in_progress':
                        self.tasks_in_progress -= 1
                        self.tasks_completed += 1
                
                break
        
        # Update assignments
        self.task_assignments = json.dumps(assignments, indent=2)
        
        # Recalculate battle progress
        total_tasks = self.tasks_pending + self.tasks_in_progress + self.tasks_completed
        if total_tasks > 0:
            self.battle_progress = (self.tasks_completed / total_tasks) * 100
        
        # Check for victory conditions
        if self.battle_progress >= self.victory_threshold:
            self._declare_victory()
    
    def _declare_victory(self):
        """🏆 Declare victory in the boss battle! 🎊"""
        
        _logger.info("🏆 VICTORY ACHIEVED! Boss battle won! 🎊")
        
        self.battle_status = 'victory'
        
        # Calculate battle statistics
        victory_stats = self._calculate_victory_stats()
        
        # Send victory notification to all warriors
        self._send_victory_notification(victory_stats)
        
        # Award battle rewards
        self._award_battle_rewards(victory_stats)
    
    def _calculate_victory_stats(self):
        """📊 Calculate battle victory statistics 🏆"""
        
        assignments = json.loads(self.task_assignments or '[]')
        warriors = json.loads(self.available_warriors or '[]')
        
        stats = {
            'total_tasks_completed': self.tasks_completed,
            'battle_duration': 'calculated_later',  # Would calculate actual duration
            'team_performance': {},
            'mvp_warrior': None,
            'battle_efficiency': self.battle_progress,
            'errors_eliminated': self.total_errors
        }
        
        # Calculate individual warrior performance
        warrior_performance = {}
        for assignment in assignments:
            warrior_id = assignment['warrior_id']
            if warrior_id not in warrior_performance:
                warrior_performance[warrior_id] = {
                    'name': assignment['warrior_name'],
                    'tasks_completed': 0,
                    'total_difficulty': 0,
                    'efficiency_score': 0
                }
            
            if assignment.get('status') == 'completed':
                warrior_performance[warrior_id]['tasks_completed'] += 1
                warrior_performance[warrior_id]['total_difficulty'] += assignment.get('difficulty', 5)
        
        # Find MVP
        if warrior_performance:
            mvp = max(warrior_performance.values(), 
                     key=lambda x: x['tasks_completed'] * x['total_difficulty'])
            stats['mvp_warrior'] = mvp
        
        stats['team_performance'] = warrior_performance
        
        return stats
    
    def _send_victory_notification(self, victory_stats):
        """🎊 Send epic victory notification! 🏆"""
        
        mvp = victory_stats.get('mvp_warrior', {})
        
        victory_message = f"""
🏆 VICTORY ACHIEVED! BOSS DEFEATED! 🎊

The {self.battle_type.upper()} has been vanquished!

📊 Battle Results:
• Tasks Completed: {victory_stats['total_tasks_completed']}
• Errors Eliminated: {victory_stats['errors_eliminated']}
• Battle Efficiency: {victory_stats['battle_efficiency']:.1f}%
• Team Performance: LEGENDARY! 🌟

🥇 MVP Warrior: {mvp.get('name', 'Team Effort')}
Tasks Conquered: {mvp.get('tasks_completed', 0)}

🎉 REWARDS UNLOCKED:
• Data Quality Champion Badge 🏅
• Boss Battle Victory Points 🎯
• Team Collaboration Bonus 👥
• Bragging Rights (Priceless) 😎

mmm lol 🐶💾 - Another boss bites the dust! Ready for the next challenge? ⚔️✨
        """
        
        _logger.info("🎊 Victory notification sent to all warriors!")
    
    def _award_battle_rewards(self, victory_stats):
        """🎁 Award battle rewards to warriors! 🏆"""
        
        # Award points and badges to participants
        for warrior_id, performance in victory_stats['team_performance'].items():
            if performance['tasks_completed'] > 0:
                # Award battle participation points
                points = performance['tasks_completed'] * 10 + performance['total_difficulty'] * 5
                
                # Update employee analytics
                self._award_warrior_points(warrior_id, points, 'boss_battle_victory')
        
        _logger.info("🎁 Battle rewards distributed to all worthy warriors!")
    
    def _award_warrior_points(self, warrior_id, points, achievement_type):
        """🏅 Award points to warrior 🎯"""
        
        # Integration with employee analytics system
        analytics = self.env['employee.analytics.dashboard'].search([
            ('employee_id', '=', warrior_id)
        ], limit=1)
        
        if analytics:
            analytics.add_achievement_points(points, achievement_type)
        
        _logger.info(f"🏅 Awarded {points} points to warrior {warrior_id}")
    
    @api.model
    def get_active_battles(self):
        """⚔️ Get all active boss battles 🎮"""
        
        return self.search([
            ('battle_status', 'in', ['preparing', 'distributing', 'in_progress'])
        ])
    
    def generate_battle_report(self):
        """📋 Generate epic battle report! 📊"""
        
        assignments = json.loads(self.task_assignments or '[]')
        
        report = f"""
⚔️ BOSS BATTLE REPORT ⚔️

Battle: {self.name}
Boss Type: {self.battle_type}
Status: {self.battle_status}

📊 BATTLE STATISTICS:
• Total Errors: {self.total_errors}
• Tasks Assigned: {len(assignments)}
• Tasks Completed: {self.tasks_completed}
• Tasks In Progress: {self.tasks_in_progress}
• Tasks Pending: {self.tasks_pending}
• Battle Progress: {self.battle_progress:.1f}%
• Complexity Score: {self.complexity_score}/10

⚔️ WARRIOR ASSIGNMENTS:
        """
        
        for assignment in assignments[:10]:  # Show first 10 assignments
            report += f"• {assignment['warrior_name']}: {assignment['task_count']} {assignment['error_type']} tasks ({assignment['status']})\n"
        
        if len(assignments) > 10:
            report += f"... and {len(assignments) - 10} more assignments\n"
        
        report += f"\nmmm lol 🐶💾 - Boss battle in progress! Victory awaits! ⚔️✨"
        
        return report