"""PDF Generation Service

Generates beautiful PDF financial reports with:
- Executive summary
- Charts and visualizations
- Financial metrics tables
- Recommendations and insights
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from io import BytesIO

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generates PDF financial reports using ReportLab"""
    
    def __init__(self):
        """Initialize PDF generator."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from reportlab.lib.colors import HexColor
            
            self.letter = letter
            self.A4 = A4
            self.getSampleStyleSheet = getSampleStyleSheet
            self.ParagraphStyle = ParagraphStyle
            self.inch = inch
            self.SimpleDocTemplate = SimpleDocTemplate
            self.Paragraph = Paragraph
            self.Spacer = Spacer
            self.Table = Table
            self.TableStyle = TableStyle
            self.PageBreak = PageBreak
            self.TA_CENTER = TA_CENTER
            self.TA_LEFT = TA_LEFT
            self.TA_RIGHT = TA_RIGHT
            self.HexColor = HexColor
        except ImportError as e:
            logger.error(f"ReportLab not installed: {e}")
            raise
    
    def generate_weekly_report_pdf(self, report) -> bytes:
        """
        Generate PDF from a FinancialReport.
        
        Args:
            report: FinancialReport object
        
        Returns:
            PDF bytes
        """
        try:
            pdf_buffer = BytesIO()
            
            # Create PDF document
            doc = self.SimpleDocTemplate(
                pdf_buffer,
                pagesize=self.letter,
                rightMargin=0.5 * self.inch,
                leftMargin=0.5 * self.inch,
                topMargin=0.5 * self.inch,
                bottomMargin=0.5 * self.inch,
            )
            
            # Container for PDF elements
            elements = []
            
            # Get styles
            styles = self.getSampleStyleSheet()
            title_style = self.ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=self.HexColor('#1e3a8a'),
                spaceAfter=10,
                alignment=self.TA_CENTER,
            )
            
            heading_style = self.ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=self.HexColor('#1e3a8a'),
                spaceAfter=6,
                spaceBefore=6,
            )
            
            # 1. Title Section
            elements.append(self.Paragraph("Financial Report", title_style))
            elements.append(self.Paragraph(
                f"Week of {report.period_start.strftime('%B %d, %Y')} to {report.period_end.strftime('%B %d, %Y')}",
                styles['Normal']
            ))
            elements.append(self.Spacer(1, 0.2 * self.inch))
            
            # 2. Executive Summary
            elements.append(self.Paragraph("Executive Summary", heading_style))
            summary_text = report.summary.get("user_message", "Financial report generated")
            elements.append(self.Paragraph(summary_text, styles['Normal']))
            elements.append(self.Spacer(1, 0.1 * self.inch))
            
            # 3. Key Metrics
            elements.append(self.Paragraph("Key Metrics", heading_style))
            metrics_table = self._create_metrics_table(report.key_metrics, styles)
            elements.append(metrics_table)
            elements.append(self.Spacer(1, 0.1 * self.inch))
            
            # 4. Spending Analysis
            elements.append(self.Paragraph("Spending Analysis", heading_style))
            spending_analysis = report.spending_analysis
            spending_text = f"""
            <b>Weekly Total:</b> ${spending_analysis.get('total_spending', 0):.2f}<br/>
            <b>Transactions:</b> {spending_analysis.get('transaction_count', 0)}<br/>
            <b>Average Transaction:</b> ${spending_analysis.get('average_transaction', 0):.2f}<br/>
            <b>Week-over-Week Change:</b> {spending_analysis.get('week_over_week_change', 0):.1f}%
            """
            elements.append(self.Paragraph(spending_text, styles['Normal']))
            elements.append(self.Spacer(1, 0.1 * self.inch))
            
            # 5. Spending by Category
            if spending_analysis.get('by_category'):
                category_table = self._create_category_table(
                    spending_analysis['by_category'],
                    styles
                )
                elements.append(self.Paragraph("Spending by Category", heading_style))
                elements.append(category_table)
                elements.append(self.Spacer(1, 0.1 * self.inch))
            
            # 6. Top Merchants
            if spending_analysis.get('top_merchants'):
                merchants_table = self._create_merchants_table(
                    spending_analysis['top_merchants'],
                    styles
                )
                elements.append(self.Paragraph("Top Merchants", heading_style))
                elements.append(merchants_table)
                elements.append(self.Spacer(1, 0.1 * self.inch))
            
            # 7. Health Analysis
            if report.health_analysis:
                elements.append(self.PageBreak())
                elements.append(self.Paragraph("Financial Health", heading_style))
                health_text = f"""
                <b>Health Score:</b> {report.health_analysis.get('score', 0):.0f}/100 ({report.health_analysis.get('grade', 'N/A')})<br/>
                <b>Risk Level:</b> {report.health_analysis.get('risk_level', 'Unknown').upper()}<br/>
                """
                elements.append(self.Paragraph(health_text, styles['Normal']))
                elements.append(self.Spacer(1, 0.1 * self.inch))
                
                # Health insights
                if report.health_analysis.get('insights'):
                    elements.append(self.Paragraph("Insights", self.ParagraphStyle(
                        'SubHeading',
                        parent=styles['Heading3'],
                        fontSize=12,
                    )))
                    for insight in report.health_analysis.get('insights', [])[:3]:
                        elements.append(self.Paragraph(f"• {insight}", styles['Normal']))
                    elements.append(self.Spacer(1, 0.1 * self.inch))
            
            # 8. Recommendations
            if report.recommendations:
                elements.append(self.Paragraph("Recommendations", heading_style))
                for i, rec in enumerate(report.recommendations[:5], 1):
                    rec_text = f"""
                    <b>{i}. {rec.get('category', 'Recommendation')}:</b> {rec.get('recommendation', '')}<br/>
                    <font size="8">Confidence: {rec.get('confidence', 0):.0%}</font>
                    """
                    elements.append(self.Paragraph(rec_text, styles['Normal']))
                    elements.append(self.Spacer(1, 0.05 * self.inch))
                elements.append(self.Spacer(1, 0.1 * self.inch))
            
            # 9. Alerts
            if report.alerts:
                elements.append(self.Paragraph("Active Alerts", heading_style))
                for alert in report.alerts[:5]:
                    alert_title = alert.get('title', 'Alert')
                    alert_msg = alert.get('message', '')
                    alert_text = f"<b>{alert_title}:</b> {alert_msg}"
                    elements.append(self.Paragraph(alert_text, styles['Normal']))
                    elements.append(self.Spacer(1, 0.05 * self.inch))
            
            # 10. Footer
            elements.append(self.Spacer(1, 0.2 * self.inch))
            footer_text = f"""
            <font size="8">
            Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
            Confidence: {report.confidence:.0%}
            </font>
            """
            elements.append(self.Paragraph(footer_text, styles['Normal']))
            
            # Build PDF
            doc.build(elements)
            
            # Get bytes
            pdf_buffer.seek(0)
            return pdf_buffer.getvalue()
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise
    
    def _create_metrics_table(self, metrics: Dict, styles) -> 'Table':
        """Create metrics table."""
        try:
            data = [['Metric', 'Value']]
            
            if metrics.get('health_score') is not None:
                data.append(['Health Score', f"{metrics['health_score']:.0f}/100"])
            if metrics.get('health_grade'):
                data.append(['Grade', metrics['health_grade']])
            if metrics.get('weekly_spending') is not None:
                data.append(['Weekly Spending', f"${metrics['weekly_spending']:.2f}"])
            if metrics.get('spending_trend'):
                data.append(['Spending Trend', metrics['spending_trend'].replace('_', ' ').title()])
            if metrics.get('spending_change') is not None:
                change = metrics['spending_change']
                arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
                data.append(['Week-over-Week', f"{arrow} {abs(change):.1f}%"])
            
            table = self.Table(data)
            table.setStyle(self.TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.HexColor('#ffffff')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), self.HexColor('#f3f4f6')),
                ('GRID', (0, 0), (-1, -1), 1, self.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.HexColor('#ffffff'), self.HexColor('#f9fafb')]),
            ]))
            
            return table
        except Exception as e:
            logger.error(f"Error creating metrics table: {e}")
            return self.Table([['Error', 'Could not create table']])
    
    def _create_category_table(self, categories: Dict[str, float], styles) -> 'Table':
        """Create spending by category table."""
        try:
            data = [['Category', 'Amount', '% of Total']]
            
            total = sum(categories.values())
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            
            for category, amount in sorted_categories:
                pct = (amount / total * 100) if total > 0 else 0
                data.append([
                    category.title(),
                    f"${amount:.2f}",
                    f"{pct:.1f}%",
                ])
            
            table = self.Table(data)
            table.setStyle(self.TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.HexColor('#ffffff')),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, self.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.HexColor('#ffffff'), self.HexColor('#f9fafb')]),
            ]))
            
            return table
        except Exception as e:
            logger.error(f"Error creating category table: {e}")
            return self.Table([['Error', 'Could not create table']])
    
    def _create_merchants_table(self, merchants: List[Dict], styles) -> 'Table':
        """Create top merchants table."""
        try:
            data = [['Merchant', 'Amount']]
            
            for merchant in merchants:
                data.append([
                    merchant.get('name', 'Unknown'),
                    f"${merchant.get('amount', 0):.2f}",
                ])
            
            table = self.Table(data)
            table.setStyle(self.TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.HexColor('#ffffff')),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, self.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.HexColor('#ffffff'), self.HexColor('#f9fafb')]),
            ]))
            
            return table
        except Exception as e:
            logger.error(f"Error creating merchants table: {e}")
            return self.Table([['Error', 'Could not create table']])
