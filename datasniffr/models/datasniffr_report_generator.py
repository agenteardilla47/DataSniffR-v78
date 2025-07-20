# -*- coding: utf-8 -*-

import json
import base64
import io
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import xlsxwriter
import csv

_logger = logging.getLogger(__name__)

class DatasniffrReportGenerator(models.Model):
    _name = 'datasniffr.report.generator'
    _description = 'DataSniffR Report Generator - Custom Report Creation'
    _order = 'create_date desc'

    name = fields.Char('Report Name', required=True)
    description = fields.Text('Description')
    model_name = fields.Char('Target Model', required=True, help='Model to generate reports for')
    report_type = fields.Selection([
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Analysis'),
        ('comparison', 'Comparison Report'),
        ('trend', 'Trend Analysis'),
        ('quality', 'Data Quality Report'),
        ('custom', 'Custom Report')
    ], string='Report Type', required=True, default='summary')
    
    output_format = fields.Selection([
        ('pdf', 'PDF Document'),
        ('excel', 'Excel Spreadsheet'),
        ('csv', 'CSV File'),
        ('json', 'JSON Data'),
        ('html', 'HTML Report'),
        ('dashboard', 'Interactive Dashboard')
    ], string='Output Format', required=True, default='pdf')
    
    template_id = fields.Many2one('datasniffr.report.template', string='Report Template')
    schedule_type = fields.Selection([
        ('manual', 'Manual'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly')
    ], string='Schedule', default='manual')
    
    next_run = fields.Datetime('Next Scheduled Run')
    last_run = fields.Datetime('Last Run', readonly=True)
    
    # Configuration
    config = fields.Text('Report Configuration', default='{}', help='JSON configuration for report generation')
    filters = fields.Text('Report Filters', default='{}', help='JSON filters to apply')
    fields_to_include = fields.Text('Fields to Include', help='Comma-separated list of fields')
    
    # AI Integration
    ai_insights = fields.Boolean('Enable AI Insights', default=True)
    ai_provider = fields.Selection([
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI GPT'),
        ('claude', 'Anthropic Claude')
    ], string='AI Provider', default='gemini')
    
    # Results
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('scheduled', 'Scheduled')
    ], string='Status', default='draft', readonly=True)
    
    result_data = fields.Text('Report Data', readonly=True)
    generated_file = fields.Binary('Generated Report', readonly=True)
    generated_filename = fields.Char('Filename', readonly=True)
    
    # Statistics
    records_processed = fields.Integer('Records Processed', readonly=True)
    generation_time = fields.Float('Generation Time (seconds)', readonly=True)
    file_size = fields.Float('File Size (MB)', readonly=True)
    
    # Boss Battle Integration
    boss_battle_triggered = fields.Boolean('Boss Battle Triggered', readonly=True)
    boss_battle_type = fields.Char('Boss Battle Type', readonly=True)
    
    @api.model
    def create(self, vals):
        """Override create to set up initial configuration"""
        if 'config' not in vals or not vals['config']:
            vals['config'] = json.dumps({
                'charts': True,
                'summaries': True,
                'ai_insights': True,
                'color_scheme': 'professional',
                'include_metadata': True
            })
        return super(DatasniffrReportGenerator, self).create(vals)

    def action_generate_report(self):
        """Generate the report based on configuration"""
        self.ensure_one()
        
        try:
            self.state = 'running'
            start_time = datetime.now()
            
            # Get data to report on
            data = self._get_report_data()
            
            # Generate report based on format
            if self.output_format == 'pdf':
                result = self._generate_pdf_report(data)
            elif self.output_format == 'excel':
                result = self._generate_excel_report(data)
            elif self.output_format == 'csv':
                result = self._generate_csv_report(data)
            elif self.output_format == 'json':
                result = self._generate_json_report(data)
            elif self.output_format == 'html':
                result = self._generate_html_report(data)
            else:
                result = self._generate_dashboard_report(data)
            
            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # Update record
            self.write({
                'state': 'completed',
                'last_run': datetime.now(),
                'generated_file': result['file_data'],
                'generated_filename': result['filename'],
                'records_processed': len(data),
                'generation_time': generation_time,
                'file_size': len(result['file_data']) / (1024 * 1024) if result['file_data'] else 0,
                'result_data': json.dumps(result.get('metadata', {}))
            })
            
            # Check for boss battle triggers
            self._check_boss_battle_triggers(data, result)
            
            # Schedule next run if needed
            if self.schedule_type != 'manual':
                self._schedule_next_run()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'🎯 Report "{self.name}" generated successfully! {len(data)} records processed in {generation_time:.2f}s',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Report generation failed: {str(e)}")
            self.state = 'failed'
            raise UserError(f"Report generation failed: {str(e)}")

    def _get_report_data(self):
        """Get data for the report based on model and filters"""
        try:
            model = self.env[self.model_name]
            
            # Apply filters
            filters = json.loads(self.filters) if self.filters else {}
            domain = []
            
            for field, condition in filters.items():
                if isinstance(condition, dict):
                    operator = condition.get('operator', '=')
                    value = condition.get('value')
                    domain.append((field, operator, value))
                else:
                    domain.append((field, '=', condition))
            
            # Get records
            records = model.search(domain)
            
            # Convert to data structure
            fields_list = self.fields_to_include.split(',') if self.fields_to_include else []
            if not fields_list:
                fields_list = ['id', 'name', 'create_date']
            
            data = []
            for record in records:
                record_data = {}
                for field in fields_list:
                    field = field.strip()
                    if hasattr(record, field):
                        value = getattr(record, field)
                        if hasattr(value, 'name'):
                            value = value.name
                        record_data[field] = value
                data.append(record_data)
            
            return data
            
        except Exception as e:
            _logger.error(f"Error getting report data: {str(e)}")
            raise

    def _generate_pdf_report(self, data):
        """Generate PDF report"""
        buffer = io.BytesIO()
        
        try:
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#2E86AB')
            )
            story.append(Paragraph(self.name, title_style))
            story.append(Spacer(1, 12))
            
            # Summary
            summary = self._generate_summary(data)
            story.append(Paragraph(f"<b>Summary:</b> {summary}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Data table
            if data:
                table_data = [list(data[0].keys())]  # Headers
                for record in data[:50]:  # Limit to first 50 records
                    table_data.append(list(record.values()))
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
            
            # AI Insights
            if self.ai_insights and data:
                insights = self._generate_ai_insights(data)
                story.append(Spacer(1, 20))
                story.append(Paragraph("<b>🤖 AI Insights:</b>", styles['Heading2']))
                story.append(Paragraph(insights, styles['Normal']))
            
            doc.build(story)
            
            return {
                'file_data': base64.b64encode(buffer.getvalue()),
                'filename': f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                'metadata': {'format': 'pdf', 'pages': 1, 'records': len(data)}
            }
            
        finally:
            buffer.close()

    def _generate_excel_report(self, data):
        """Generate Excel report"""
        buffer = io.BytesIO()
        
        try:
            workbook = xlsxwriter.Workbook(buffer)
            worksheet = workbook.add_worksheet('Report Data')
            
            # Formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#2E86AB',
                'font_color': 'white',
                'align': 'center'
            })
            
            if data:
                # Write headers
                headers = list(data[0].keys())
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header, header_format)
                
                # Write data
                for row, record in enumerate(data, 1):
                    for col, value in enumerate(record.values()):
                        worksheet.write(row, col, str(value))
                
                # Auto-adjust column widths
                for col, header in enumerate(headers):
                    worksheet.set_column(col, col, len(header) + 5)
            
            # Add summary sheet
            summary_sheet = workbook.add_worksheet('Summary')
            summary = self._generate_summary(data)
            summary_sheet.write(0, 0, 'Report Summary', header_format)
            summary_sheet.write(1, 0, summary)
            
            workbook.close()
            
            return {
                'file_data': base64.b64encode(buffer.getvalue()),
                'filename': f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                'metadata': {'format': 'excel', 'sheets': 2, 'records': len(data)}
            }
            
        finally:
            buffer.close()

    def _generate_csv_report(self, data):
        """Generate CSV report"""
        buffer = io.StringIO()
        
        try:
            if data:
                writer = csv.DictWriter(buffer, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            csv_content = buffer.getvalue()
            
            return {
                'file_data': base64.b64encode(csv_content.encode('utf-8')),
                'filename': f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                'metadata': {'format': 'csv', 'records': len(data)}
            }
            
        finally:
            buffer.close()

    def _generate_json_report(self, data):
        """Generate JSON report"""
        report_data = {
            'report_name': self.name,
            'generated_at': datetime.now().isoformat(),
            'summary': self._generate_summary(data),
            'data': data,
            'metadata': {
                'total_records': len(data),
                'model': self.model_name,
                'report_type': self.report_type
            }
        }
        
        if self.ai_insights and data:
            report_data['ai_insights'] = self._generate_ai_insights(data)
        
        json_content = json.dumps(report_data, indent=2, default=str)
        
        return {
            'file_data': base64.b64encode(json_content.encode('utf-8')),
            'filename': f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            'metadata': {'format': 'json', 'records': len(data)}
        }

    def _generate_html_report(self, data):
        """Generate HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2E86AB; color: white; padding: 20px; border-radius: 5px; }}
                .summary {{ background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #2E86AB; color: white; }}
                .insights {{ background: #e8f4f8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 {self.name}</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Summary</h2>
                <p>{self._generate_summary(data)}</p>
            </div>
        """
        
        if data:
            html_content += """
            <h2>📋 Data</h2>
            <table>
                <tr>
            """
            
            # Headers
            for header in data[0].keys():
                html_content += f"<th>{header}</th>"
            html_content += "</tr>"
            
            # Data rows (limit to first 100)
            for record in data[:100]:
                html_content += "<tr>"
                for value in record.values():
                    html_content += f"<td>{value}</td>"
                html_content += "</tr>"
            
            html_content += "</table>"
        
        if self.ai_insights and data:
            insights = self._generate_ai_insights(data)
            html_content += f"""
            <div class="insights">
                <h2>🤖 AI Insights</h2>
                <p>{insights}</p>
            </div>
            """
        
        html_content += "</body></html>"
        
        return {
            'file_data': base64.b64encode(html_content.encode('utf-8')),
            'filename': f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            'metadata': {'format': 'html', 'records': len(data)}
        }

    def _generate_summary(self, data):
        """Generate report summary"""
        if not data:
            return "No data found for the specified criteria."
        
        summary = f"Report contains {len(data)} records from {self.model_name}. "
        
        # Add some basic statistics
        if data and isinstance(data[0], dict):
            fields = list(data[0].keys())
            summary += f"Fields included: {', '.join(fields[:5])}{'...' if len(fields) > 5 else ''}."
        
        return summary

    def _generate_ai_insights(self, data):
        """Generate AI insights for the report data"""
        try:
            if not data:
                return "No data available for AI analysis."
            
            # Prepare data summary for AI
            data_summary = {
                'total_records': len(data),
                'fields': list(data[0].keys()) if data else [],
                'sample_data': data[:5] if len(data) > 5 else data
            }
            
            # Mock AI insights (in real implementation, call actual AI service)
            insights = f"""
            Based on the analysis of {len(data)} records:
            
            📈 **Key Findings:**
            • Dataset contains {len(data)} records with {len(data[0].keys()) if data else 0} fields
            • Data appears to be from {self.model_name} model
            • Report generated for {self.report_type} analysis
            
            🎯 **Recommendations:**
            • Consider implementing data validation rules
            • Monitor data quality trends over time
            • Set up automated alerts for anomalies
            
            💡 **Next Steps:**
            • Schedule regular data quality checks
            • Implement data governance policies
            • Consider data enrichment opportunities
            """
            
            return insights
            
        except Exception as e:
            _logger.error(f"Error generating AI insights: {str(e)}")
            return "AI insights temporarily unavailable."

    def _check_boss_battle_triggers(self, data, result):
        """Check if report generation should trigger boss battles"""
        try:
            config = json.loads(self.config) if self.config else {}
            
            # Trigger boss battle for large reports
            if len(data) > 10000:
                self.boss_battle_triggered = True
                self.boss_battle_type = 'data_mountain'
                
                # Create boss battle
                boss_battle = self.env['datasniffr.boss.battle'].create({
                    'name': f'🏔️ Data Mountain Boss - {self.name}',
                    'boss_type': 'data_mountain',
                    'difficulty': 'epic',
                    'description': f'Conquered massive dataset with {len(data)} records!',
                    'trigger_model': self._name,
                    'trigger_record_id': self.id,
                    'xp_reward': min(len(data) // 100, 1000),
                    'battle_data': json.dumps({
                        'records_processed': len(data),
                        'report_type': self.report_type,
                        'generation_time': self.generation_time
                    })
                })
                
                boss_battle.action_start_battle()
            
            # Trigger for complex reports
            elif self.report_type == 'custom' and self.ai_insights:
                self.boss_battle_triggered = True
                self.boss_battle_type = 'insight_wizard'
                
                boss_battle = self.env['datasniffr.boss.battle'].create({
                    'name': f'🧙‍♂️ Insight Wizard Boss - {self.name}',
                    'boss_type': 'insight_wizard',
                    'difficulty': 'legendary',
                    'description': 'Mastered the art of AI-powered report generation!',
                    'trigger_model': self._name,
                    'trigger_record_id': self.id,
                    'xp_reward': 750,
                    'battle_data': json.dumps({
                        'ai_provider': self.ai_provider,
                        'output_format': self.output_format
                    })
                })
                
                boss_battle.action_start_battle()
                
        except Exception as e:
            _logger.error(f"Error checking boss battle triggers: {str(e)}")

    def _schedule_next_run(self):
        """Schedule the next run based on schedule type"""
        if self.schedule_type == 'daily':
            self.next_run = datetime.now() + timedelta(days=1)
        elif self.schedule_type == 'weekly':
            self.next_run = datetime.now() + timedelta(weeks=1)
        elif self.schedule_type == 'monthly':
            self.next_run = datetime.now() + timedelta(days=30)
        elif self.schedule_type == 'quarterly':
            self.next_run = datetime.now() + timedelta(days=90)

    @api.model
    def run_scheduled_reports(self):
        """Cron job to run scheduled reports"""
        scheduled_reports = self.search([
            ('schedule_type', '!=', 'manual'),
            ('next_run', '<=', datetime.now()),
            ('state', 'in', ['draft', 'completed', 'scheduled'])
        ])
        
        for report in scheduled_reports:
            try:
                report.action_generate_report()
            except Exception as e:
                _logger.error(f"Failed to run scheduled report {report.name}: {str(e)}")

    def action_download_report(self):
        """Download the generated report"""
        self.ensure_one()
        
        if not self.generated_file:
            raise UserError("No report file available. Please generate the report first.")
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/datasniffr.report.generator/{self.id}/generated_file/{self.generated_filename}?download=true',
            'target': 'new',
        }

    def action_duplicate_report(self):
        """Duplicate the report configuration"""
        self.ensure_one()
        
        new_report = self.copy({
            'name': f"{self.name} (Copy)",
            'state': 'draft',
            'last_run': False,
            'generated_file': False,
            'generated_filename': False,
            'result_data': False,
            'boss_battle_triggered': False
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'datasniffr.report.generator',
            'res_id': new_report.id,
            'view_mode': 'form',
            'target': 'current',
        }


class DatasniffrReportTemplate(models.Model):
    _name = 'datasniffr.report.template'
    _description = 'DataSniffR Report Templates'

    name = fields.Char('Template Name', required=True)
    description = fields.Text('Description')
    report_type = fields.Selection([
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Analysis'),
        ('comparison', 'Comparison Report'),
        ('trend', 'Trend Analysis'),
        ('quality', 'Data Quality Report'),
        ('custom', 'Custom Report')
    ], string='Report Type', required=True)
    
    template_config = fields.Text('Template Configuration', default='{}')
    default_fields = fields.Text('Default Fields')
    styling_config = fields.Text('Styling Configuration', default='{}')
    
    active = fields.Boolean('Active', default=True)