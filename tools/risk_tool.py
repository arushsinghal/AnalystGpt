from typing import List, Dict, Any
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import constants

class RiskTool:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=constants.GEMINI_MODEL,
            google_api_key=constants.GOOGLE_API_KEY,
            temperature=0.1
        )
        self.prompt_template = PromptTemplate(
            input_variables=["context"],
            template=self._load_prompt_template()
        )
    
    def _load_prompt_template(self) -> str:
        """Load the risk prompt template."""
        try:
            with open("prompts/risk_prompt.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default prompt if template file is not found."""
        return """You are a risk analyst specializing in identifying and analyzing risk factors from financial documents. Your task is to analyze the provided document chunks and extract comprehensive risk information.

Context: {context}

Please provide a structured risk analysis with:
1. Executive Summary of Key Risks (2-3 sentences)
2. Identified Risk Categories (with specific examples)
3. Risk Severity Assessment (High/Medium/Low)
4. Risk Mitigation Strategies (if mentioned)
5. Regulatory and Compliance Risks
6. Forward-Looking Risk Statements

Format your response in a professional, analytical tone suitable for risk assessment."""
    
    def analyze_risks(self, documents: List[Document]) -> Dict[str, Any]:
        """Analyze risks from the provided documents."""
        if not documents:
            return {"error": "No documents provided"}
        
        # Prepare context from documents
        context = self._prepare_context(documents)
        
        # Generate prompt
        prompt = self.prompt_template.format(context=context)
        
        try:
            # Generate response
            response = self.llm.predict(prompt)
            
            return {
                "result": response,
                "source_documents": len(documents),
                "companies": list(set([doc.metadata.get("company_name", "Unknown") for doc in documents])),
                "quarters": list(set([f"{doc.metadata.get('year', 'Unknown')} {doc.metadata.get('quarter', 'Unknown')}" for doc in documents]))
            }
        
        except Exception as e:
            return {"error": f"Error analyzing risks: {str(e)}"}
    
    def analyze_company_risks(self, company_name: str, vector_store) -> Dict[str, Any]:
        """Analyze risks for a specific company."""
        # Search for documents from the company, focusing on risk-related content
        documents = vector_store.search_by_company(company_name, "risk factors disclosure", k=10)
        
        if not documents:
            # Try broader search if no risk-specific documents found
            documents = vector_store.search_by_company(company_name, "financial performance", k=10)
        
        if not documents:
            return {"error": f"No documents found for company: {company_name}"}
        
        return self.analyze_risks(documents)
    
    def analyze_quarter_risks(self, year: str, quarter: str, vector_store) -> Dict[str, Any]:
        """Analyze risks for a specific quarter."""
        # Search for documents from the quarter, focusing on risk-related content
        documents = vector_store.search_by_quarter(year, quarter, "risk factors", k=10)
        
        if not documents:
            # Try broader search if no risk-specific documents found
            documents = vector_store.search_by_quarter(year, quarter, "financial performance", k=10)
        
        if not documents:
            return {"error": f"No documents found for {year} {quarter}"}
        
        return self.analyze_risks(documents)
    
    def analyze_section_risks(self, section: str, vector_store) -> Dict[str, Any]:
        """Analyze risks from a specific section (e.g., risk factors section)."""
        # Search for documents from the specific section
        documents = vector_store.search_by_section(section, "risk disclosure", k=10)
        
        if not documents:
            return {"error": f"No documents found for section: {section}"}
        
        return self.analyze_risks(documents)
    
    def _prepare_context(self, documents: List[Document]) -> str:
        """Prepare context from documents for risk analysis."""
        context_parts = []
        
        for i, doc in enumerate(documents):
            company = doc.metadata.get("company_name", "Unknown")
            year = doc.metadata.get("year", "Unknown")
            quarter = doc.metadata.get("quarter", "Unknown")
            section = doc.metadata.get("section", "Unknown")
            
            header = f"Document {i+1}: {company} - {year} {quarter} - {section}"
            content = doc.page_content[:1000]  # Limit content length
            
            context_parts.append(f"{header}\n{content}\n")
        
        return "\n".join(context_parts)
    
    def identify_risk_keywords(self, text: str) -> List[str]:
        """Identify risk-related keywords in text."""
        risk_keywords = [
            "risk", "uncertainty", "volatility", "exposure", "vulnerability",
            "threat", "challenge", "adverse", "negative", "decline", "loss",
            "litigation", "legal", "regulatory", "compliance", "penalty",
            "cybersecurity", "data breach", "privacy", "security",
            "supply chain", "disruption", "shortage", "inflation",
            "interest rate", "currency", "exchange rate", "hedge",
            "competition", "market share", "pricing pressure",
            "technology", "innovation", "obsolescence", "disruption"
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in risk_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords

# Example usage
if __name__ == "__main__":
    # This would be used within the main application
    pass 