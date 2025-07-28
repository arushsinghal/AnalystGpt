from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from typing import Dict, Any, List
from datetime import datetime
import os

class PDFExporter:
    def __init__(self):
        self.export_dir = "exports"
        os.makedirs(self.export_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.styles.add(ParagraphStyle(
            name='Heading1',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['BodyText'],
            fontSize=10,
            spaceAfter=6
        ))
    
    def export_analysis_result(self, result: Dict[str, Any], analysis_type: str) -> str:
        """Export analysis result to PDF."""
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analystgpt_{analysis_type}_{timestamp}.pdf"
            filepath = os.path.join(self.export_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Add title
            story.append(Paragraph(f"AnalystGPT - {analysis_type.title()} Analysis", self.styles['Heading1']))
            story.append(Spacer(1, 12))
            
            # Add metadata
            story.extend(self._create_metadata_section(result))
            story.append(Spacer(1, 12))
            
            # Add main analysis content
            story.extend(self._create_analysis_section(result, analysis_type))
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting to PDF: {str(e)}")
    
    def _create_metadata_section(self, result: Dict[str, Any]) -> List:
        """Create metadata section for PDF."""
        elements = []
        
        elements.append(Paragraph("Analysis Information", self.styles['Heading2']))
        
        # Create metadata table
        metadata_data = [
            ["Field", "Value"],
            ["Analysis Type", result.get("analysis_type", "").title()],
            ["Status", result.get("status", "").title()],
            ["Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        if "result" in result:
            analysis_result = result["result"]
            metadata_data.extend([
                ["Source Documents", str(analysis_result.get("source_documents", 0))],
                ["Companies", ", ".join(analysis_result.get("companies", []))],
                ["Quarters", ", ".join(analysis_result.get("quarters", []))]
            ])
        
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(metadata_table)
        elements.append(Spacer(1, 12))
        
        return elements
    
    def _create_analysis_section(self, result: Dict[str, Any], analysis_type: str) -> List:
        """Create main analysis section for PDF."""
        elements = []
        
        if "result" not in result:
            elements.append(Paragraph("No analysis results available", self.styles['BodyText']))
            return elements
        
        analysis_result = result["result"]
        
        if analysis_type == "insight":
            elements.extend(self._create_insight_section(analysis_result))
        elif analysis_type == "compare":
            elements.extend(self._create_compare_section(analysis_result))
        elif analysis_type == "risk":
            elements.extend(self._create_risk_section(analysis_result))
        elif analysis_type == "qa":
            elements.extend(self._create_qa_section(analysis_result))
        
        return elements
    
    def _create_insight_section(self, result: Dict[str, Any]) -> List:
        """Create insight analysis section."""
        elements = []
        
        elements.append(Paragraph("Financial Insights Analysis", self.styles['Heading2']))
        elements.append(Spacer(1, 8))
        
        if "insights" in result:
            insights_text = result["insights"]
            elements.append(Paragraph(insights_text, self.styles['BodyText']))
        else:
            elements.append(Paragraph("No insights available", self.styles['BodyText']))
        
        return elements
    
    def _create_compare_section(self, result: Dict[str, Any]) -> List:
        """Create comparison analysis section."""
        elements = []
        
        elements.append(Paragraph("Comparative Analysis", self.styles['Heading2']))
        elements.append(Spacer(1, 8))
        
        if "comparison" in result:
            comparison_text = result["comparison"]
            elements.append(Paragraph(comparison_text, self.styles['BodyText']))
        else:
            elements.append(Paragraph("No comparison available", self.styles['BodyText']))
        
        return elements
    
    def _create_risk_section(self, result: Dict[str, Any]) -> List:
        """Create risk analysis section."""
        elements = []
        
        elements.append(Paragraph("Risk Analysis", self.styles['Heading2']))
        elements.append(Spacer(1, 8))
        
        if "risk_analysis" in result:
            risk_text = result["risk_analysis"]
            elements.append(Paragraph(risk_text, self.styles['BodyText']))
        else:
            elements.append(Paragraph("No risk analysis available", self.styles['BodyText']))
        
        return elements
    
    def _create_qa_section(self, result: Dict[str, Any]) -> List:
        """Create Q&A analysis section."""
        elements = []
        
        elements.append(Paragraph("Question & Answer Analysis", self.styles['Heading2']))
        elements.append(Spacer(1, 8))
        
        if "answer" in result:
            # Create Q&A table
            qa_data = [
                ["Question", result.get("question", "")],
                ["Answer", result.get("answer", "")]
            ]
            
            qa_table = Table(qa_data, colWidths=[1.5*inch, 4.5*inch])
            qa_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 1), (0, 1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(qa_table)
            elements.append(Spacer(1, 12))
            
            # Add source information
            elements.append(Paragraph("Source Information", self.styles['Heading2']))
            source_data = [
                ["Source Documents", str(result.get("source_documents", 0))],
                ["Companies", ", ".join(result.get("companies", []))],
                ["Quarters", ", ".join(result.get("quarters", []))]
            ]
            
            source_table = Table(source_data, colWidths=[2*inch, 4*inch])
            source_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(source_table)
        else:
            elements.append(Paragraph("No Q&A available", self.styles['BodyText']))
        
        return elements

# Example usage
if __name__ == "__main__":
    exporter = PDFExporter()
    
    # Example result
    result = {
        "status": "success",
        "analysis_type": "insight",
        "result": {
            "insights": "Sample insights content...",
            "source_documents": 5,
            "companies": ["Apple", "Google"],
            "quarters": ["2023 Q1", "2023 Q2"]
        }
    }
    
    # filepath = exporter.export_analysis_result(result, "insight")
    # print(f"Exported to: {filepath}")
