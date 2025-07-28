from typing import List, Dict, Any
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import constants

class InsightTool:
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
        """Load the insight prompt template."""
        try:
            with open("prompts/insight_prompt.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default prompt if template file is not found."""
        return """You are a senior financial analyst specializing in extracting key insights from earnings reports and financial documents. Your task is to analyze the provided document chunks and generate comprehensive business insights.

Context: {context}

Please provide a structured analysis with:
1. Executive Summary (2-3 sentences)
2. Key Financial Metrics (with specific numbers)
3. Business Highlights (3-5 bullet points)
4. Strategic Initiatives (2-3 points)
5. Risk Factors (if any significant ones mentioned)
6. Outlook and Forward-Looking Statements

Format your response in a professional, analytical tone suitable for investment decision-making."""
    
    def generate_insights(self, documents: List[Document]) -> Dict[str, Any]:
        """Generate insights from the provided documents."""
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
                "insights": response,
                "source_documents": len(documents),
                "companies": list(set([doc.metadata.get("company_name", "Unknown") for doc in documents])),
                "quarters": list(set([f"{doc.metadata.get('year', 'Unknown')} {doc.metadata.get('quarter', 'Unknown')}" for doc in documents]))
            }
        
        except Exception as e:
            return {"error": f"Error generating insights: {str(e)}"}
    
    def generate_company_insights(self, company_name: str, vector_store) -> Dict[str, Any]:
        """Generate insights for a specific company."""
        # Search for documents from the company
        documents = vector_store.search_by_company(company_name, "financial performance", k=10)
        
        if not documents:
            return {"error": f"No documents found for company: {company_name}"}
        
        return self.generate_insights(documents)
    
    def generate_quarter_insights(self, year: str, quarter: str, vector_store) -> Dict[str, Any]:
        """Generate insights for a specific quarter."""
        # Search for documents from the quarter
        documents = vector_store.search_by_quarter(year, quarter, "financial performance", k=10)
        
        if not documents:
            return {"error": f"No documents found for {year} {quarter}"}
        
        return self.generate_insights(documents)
    
    def _prepare_context(self, documents: List[Document]) -> str:
        """Prepare context from documents for analysis."""
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

# Example usage
if __name__ == "__main__":
    # This would be used within the main application
    pass 