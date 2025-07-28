from typing import List, Dict, Any
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import constants

class CompareTool:
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
        """Load the compare prompt template."""
        try:
            with open("prompts/compare_prompt.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default prompt if template file is not found."""
        return """You are a comparative financial analyst specializing in analyzing and comparing financial data across companies and time periods. Your task is to analyze the provided document chunks and generate comprehensive comparative analysis.

Context: {context}

Please provide a structured comparative analysis with:
1. Executive Summary of Key Comparisons (2-3 sentences)
2. Quantitative Metrics Comparison (with specific numbers)
3. Performance Analysis (growth rates, margins, etc.)
4. Strategic Differences and Similarities
5. Market Position Comparison
6. Forward-Looking Comparative Outlook

Format your response in a professional, analytical tone suitable for investment decision-making."""
    
    def compare_companies(self, company1: str, company2: str, vector_store) -> Dict[str, Any]:
        """Compare two companies."""
        # Search for documents from both companies
        docs1 = vector_store.search_by_company(company1, "financial performance", k=8)
        docs2 = vector_store.search_by_company(company2, "financial performance", k=8)
        
        if not docs1 and not docs2:
            return {"error": f"No documents found for comparison"}
        
        # Combine documents
        all_docs = docs1 + docs2
        context = self._prepare_context(all_docs)
        
        # Generate prompt
        prompt = self.prompt_template.format(context=context)
        
        try:
            # Generate response
            response = self.llm.predict(prompt)
            
            return {
                "comparison": response,
                "companies": [company1, company2],
                "source_documents": len(all_docs)
            }
        
        except Exception as e:
            return {"error": f"Error comparing companies: {str(e)}"}
    
    def compare_quarters(self, year1: str, quarter1: str, year2: str, quarter2: str, vector_store) -> Dict[str, Any]:
        """Compare two quarters."""
        # Search for documents from both quarters
        docs1 = vector_store.search_by_quarter(year1, quarter1, "financial performance", k=8)
        docs2 = vector_store.search_by_quarter(year2, quarter2, "financial performance", k=8)
        
        if not docs1 and not docs2:
            return {"error": f"No documents found for comparison"}
        
        # Combine documents
        all_docs = docs1 + docs2
        context = self._prepare_context(all_docs)
        
        # Generate prompt
        prompt = self.prompt_template.format(context=context)
        
        try:
            # Generate response
            response = self.llm.predict(prompt)
            
            return {
                "comparison": response,
                "quarters": [f"{year1} {quarter1}", f"{year2} {quarter2}"],
                "source_documents": len(all_docs)
            }
        
        except Exception as e:
            return {"error": f"Error comparing quarters: {str(e)}"}
    
    def _prepare_context(self, documents: List[Document]) -> str:
        """Prepare context from documents for comparison."""
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