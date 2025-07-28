import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
import os

class ExcelExporter:
    def __init__(self):
        self.export_dir = "exports"
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_analysis_result(self, result: Dict[str, Any], analysis_type: str) -> str:
        """Export analysis result to Excel."""
        try:
            # Create a new Excel writer
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analystgpt_{analysis_type}_{timestamp}.xlsx"
            filepath = os.path.join(self.export_dir, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Export main analysis
                self._export_main_analysis(result, analysis_type, writer)
                
                # Export metadata
                self._export_metadata(result, writer)
                
                # Export source information
                self._export_source_info(result, writer)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting to Excel: {str(e)}")
    
    def _export_main_analysis(self, result: Dict[str, Any], analysis_type: str, writer):
        """Export the main analysis content."""
        if "result" not in result:
            return
        
        analysis_result = result["result"]
        
        if analysis_type == "insight":
            self._export_insight_analysis(analysis_result, writer)
        elif analysis_type == "compare":
            self._export_compare_analysis(analysis_result, writer)
        elif analysis_type == "risk":
            self._export_risk_analysis(analysis_result, writer)
        elif analysis_type == "qa":
            self._export_qa_analysis(analysis_result, writer)
    
    def _export_insight_analysis(self, result: Dict[str, Any], writer):
        """Export insight analysis to Excel."""
        if "insights" in result:
            # Create DataFrame for insights
            insights_text = result["insights"]
            
            # Split insights into sections (basic parsing)
            sections = self._parse_insights_sections(insights_text)
            
            for section_name, content in sections.items():
                df = pd.DataFrame({
                    "Section": [section_name],
                    "Content": [content]
                })
                df.to_excel(writer, sheet_name=section_name[:31], index=False)
    
    def _export_compare_analysis(self, result: Dict[str, Any], writer):
        """Export comparison analysis to Excel."""
        if "comparison" in result:
            comparison_text = result["comparison"]
            
            # Split comparison into sections
            sections = self._parse_comparison_sections(comparison_text)
            
            for section_name, content in sections.items():
                df = pd.DataFrame({
                    "Section": [section_name],
                    "Content": [content]
                })
                df.to_excel(writer, sheet_name=section_name[:31], index=False)
    
    def _export_risk_analysis(self, result: Dict[str, Any], writer):
        """Export risk analysis to Excel."""
        if "risk_analysis" in result:
            risk_text = result["risk_analysis"]
            
            # Split risk analysis into sections
            sections = self._parse_risk_sections(risk_text)
            
            for section_name, content in sections.items():
                df = pd.DataFrame({
                    "Section": [section_name],
                    "Content": [content]
                })
                df.to_excel(writer, sheet_name=section_name[:31], index=False)
    
    def _export_qa_analysis(self, result: Dict[str, Any], writer):
        """Export QA analysis to Excel."""
        if "answer" in result:
            df = pd.DataFrame({
                "Question": [result.get("question", "")],
                "Answer": [result.get("answer", "")],
                "Source Documents": [result.get("source_documents", 0)],
                "Companies": [", ".join(result.get("companies", []))],
                "Quarters": [", ".join(result.get("quarters", []))]
            })
            df.to_excel(writer, sheet_name="Q&A Analysis", index=False)
    
    def _export_metadata(self, result: Dict[str, Any], writer):
        """Export metadata to Excel."""
        metadata = {
            "Analysis Type": result.get("analysis_type", ""),
            "Status": result.get("status", ""),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Source Documents": result.get("result", {}).get("source_documents", 0),
            "Companies": ", ".join(result.get("result", {}).get("companies", [])),
            "Quarters": ", ".join(result.get("result", {}).get("quarters", []))
        }
        
        df = pd.DataFrame(list(metadata.items()), columns=["Field", "Value"])
        df.to_excel(writer, sheet_name="Metadata", index=False)
    
    def _export_source_info(self, result: Dict[str, Any], writer):
        """Export source information to Excel."""
        if "result" in result:
            analysis_result = result["result"]
            
            source_info = {
                "Source Documents": analysis_result.get("source_documents", 0),
                "Companies": ", ".join(analysis_result.get("companies", [])),
                "Quarters": ", ".join(analysis_result.get("quarters", []))
            }
            
            df = pd.DataFrame(list(source_info.items()), columns=["Field", "Value"])
            df.to_excel(writer, sheet_name="Source Info", index=False)
    
    def _parse_insights_sections(self, text: str) -> Dict[str, str]:
        """Parse insights text into sections."""
        sections = {}
        current_section = "General"
        current_content = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if any(keyword in line.lower() for keyword in ["executive summary", "key financial metrics", "business highlights", "strategic initiatives", "risk factors", "outlook"]):
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _parse_comparison_sections(self, text: str) -> Dict[str, str]:
        """Parse comparison text into sections."""
        sections = {}
        current_section = "General"
        current_content = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if any(keyword in line.lower() for keyword in ["executive summary", "key metrics comparison", "performance analysis", "strategic comparison", "risk and outlook", "investment implications"]):
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _parse_risk_sections(self, text: str) -> Dict[str, str]:
        """Parse risk analysis text into sections."""
        sections = {}
        current_section = "General"
        current_content = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if any(keyword in line.lower() for keyword in ["executive summary", "risk categories", "risk assessment", "risk mitigation", "emerging risks", "risk metrics", "investment implications"]):
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

# Example usage
if __name__ == "__main__":
    exporter = ExcelExporter()
    
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
