import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, List, Union
import os

class ReportGenerator:
    def __init__(self, config):
        self.config = config
        self.export_dir = config.EXPORT_DIR
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_pdf_report(self, assessment_data: Dict, output_path: str = None) -> str:
        """Generate a PDF report for an assessment."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.export_dir / f"assessment_report_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph(f"Assessment Report for {assessment_data['employee_name']}", title_style))
        
        # Employee Information
        info_data = [
            ["Employee Name", assessment_data['employee_name']],
            ["Department", assessment_data['department']],
            ["Date", assessment_data['date']],
            ["Performance Rating", str(assessment_data['performance_rating'])]
        ]
        
        info_table = Table(info_data, colWidths=[150, 300])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # Review Content
        elements.append(Paragraph("Review Content", styles['Heading2']))
        elements.append(Paragraph(assessment_data['review_content'], styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Analysis Results
        elements.append(Paragraph("Analysis Results", styles['Heading2']))
        analysis_data = [
            ["Metric", "Value"],
            ["Sentiment Score", f"{assessment_data['sentiment_score']:.2f}"],
            ["Promotion Recommended", "Yes" if assessment_data['promotion_recommended'] else "No"],
            ["Confidence Score", f"{assessment_data['confidence_score']:.2f}"]
        ]
        
        analysis_table = Table(analysis_data, colWidths=[150, 300])
        analysis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(analysis_table)
        elements.append(Spacer(1, 20))
        
        # Areas for Improvement
        if assessment_data.get('areas_for_improvement'):
            elements.append(Paragraph("Areas for Improvement", styles['Heading2']))
            for area in assessment_data['areas_for_improvement']:
                elements.append(Paragraph(f"• {area}", styles['Normal']))
            elements.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(elements)
        return str(output_path)
    
    def generate_csv_report(self, assessment_data: Dict, output_path: str = None) -> str:
        """Generate a CSV report for an assessment."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.export_dir / f"assessment_report_{timestamp}.csv"
        
        # Convert assessment data to DataFrame
        df = pd.DataFrame([{
            'employee_name': assessment_data['employee_name'],
            'department': assessment_data['department'],
            'date': assessment_data['date'],
            'performance_rating': assessment_data['performance_rating'],
            'sentiment_score': assessment_data['sentiment_score'],
            'promotion_recommended': assessment_data['promotion_recommended'],
            'confidence_score': assessment_data['confidence_score'],
            'review_content': assessment_data['review_content'],
            'areas_for_improvement': '; '.join(assessment_data.get('areas_for_improvement', [])),
            'bias_details': assessment_data.get('bias_details', '')
        }])
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        return str(output_path)
    
    def generate_fairness_report(self, validation_data: Dict, output_path: str = None) -> str:
        """Generate a PDF report for fairness validation results."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.export_dir / f"fairness_report_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph("Fairness Validation Report", title_style))
        
        # Summary
        summary_data = [
            ["Total Validations", str(validation_data['total_validations'])],
            ["Passed", str(validation_data['passed_validations'])],
            ["Failed", str(validation_data['failed_validations'])]
        ]
        
        summary_table = Table(summary_data, colWidths=[150, 300])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Detailed Results
        elements.append(Paragraph("Detailed Results", styles['Heading2']))
        
        for metric, results in validation_data['metrics'].items():
            elements.append(Paragraph(metric.replace('_', ' ').title(), styles['Heading3']))
            
            for result in results:
                result_data = [
                    ["Value", f"{result['value']:.2f}"],
                    ["Threshold", f"{result['threshold']:.2f}"],
                    ["Status", result['status']]
                ]
                
                result_table = Table(result_data, colWidths=[100, 350])
                result_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(result_table)
                elements.append(Spacer(1, 10))
            
            elements.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(elements)
        return str(output_path) 