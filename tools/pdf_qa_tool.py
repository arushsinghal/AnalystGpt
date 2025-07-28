from typing import List, Dict, Any
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import constants

class PDFQATool:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=constants.GEMINI_MODEL,
            google_api_key=constants.GOOGLE_API_KEY,
            temperature=0.1
        )
        self.qa_prompt_template = PromptTemplate(
            input_variables=["question", "context"],
            template=self._get_qa_prompt()
        )
    
    def _get_qa_prompt(self) -> str:
        """Get the QA prompt template."""
        return """You are a financial analyst assistant. Answer the user's question based on the provided document context. 

Question: {question}

Context from documents:
{context}

Instructions:
1. Answer the question based ONLY on the information provided in the context
2. If the information is not available in the context, say "I don't have enough information to answer this question"
3. Provide specific numbers and data when available
4. Cite the source (company, year, quarter) when providing information
5. Be precise and professional in your response
6. If the question asks for comparisons, provide clear comparisons with specific data

Please provide a clear, structured answer with:
- Direct answer to the question
- Supporting data and context
- Source information (company, period)
- Any relevant caveats or limitations

Format your response in a professional, analytical tone."""
    
    def answer_question(self, question: str, documents: List[Document]) -> Dict[str, Any]:
        """Answer a specific question based on the provided documents."""
        if not documents:
            return {"error": "No documents provided"}
        
        if not question.strip():
            return {"error": "No question provided"}
        
        # Prepare context from documents
        context = self._prepare_context(documents)
        
        # Generate prompt
        prompt = self.qa_prompt_template.format(
            question=question,
            context=context
        )
        
        try:
            # Generate response
            response = self.llm.predict(prompt)
            
            return {
                "answer": response,
                "question": question,
                "source_documents": len(documents),
                "companies": list(set([doc.metadata.get("company_name", "Unknown") for doc in documents])),
                "quarters": list(set([f"{doc.metadata.get('year', 'Unknown')} {doc.metadata.get('quarter', 'Unknown')}" for doc in documents]))
            }
        
        except Exception as e:
            return {"error": f"Error answering question: {str(e)}"}
    
    def answer_company_question(self, question: str, company_name: str, vector_store) -> Dict[str, Any]:
        """Answer a question about a specific company."""
        # Search for relevant documents from the company
        documents = vector_store.search_by_company(company_name, question, k=8)
        
        if not documents:
            return {"error": f"No documents found for company: {company_name}"}
        
        return self.answer_question(question, documents)
    
    def answer_quarter_question(self, question: str, year: str, quarter: str, vector_store) -> Dict[str, Any]:
        """Answer a question about a specific quarter."""
        # Search for relevant documents from the quarter
        documents = vector_store.search_by_quarter(year, quarter, question, k=8)
        
        if not documents:
            return {"error": f"No documents found for {year} {quarter}"}
        
        return self.answer_question(question, documents)
    
    def answer_general_question(self, question: str, vector_store) -> Dict[str, Any]:
        """Answer a general question across all documents."""
        # Search for relevant documents across all companies
        documents = vector_store.similarity_search(question, k=10)
        
        if not documents:
            return {"error": "No relevant documents found"}
        
        return self.answer_question(question, documents)
    
    def _prepare_context(self, documents: List[Document]) -> str:
        """Prepare context from documents for QA."""
        context_parts = []
        
        for i, doc in enumerate(documents):
            company = doc.metadata.get("company_name", "Unknown")
            year = doc.metadata.get("year", "Unknown")
            quarter = doc.metadata.get("quarter", "Unknown")
            section = doc.metadata.get("section", "Unknown")
            page = doc.metadata.get("page_number", "Unknown")
            
            header = f"Source {i+1}: {company} - {year} {quarter} - {section} (Page {page})"
            content = doc.page_content[:1200]  # Limit content length
            
            context_parts.append(f"{header}\n{content}\n")
        
        return "\n".join(context_parts)
    
    def suggest_questions(self, company_name: str = None, year: str = None, quarter: str = None) -> List[str]:
        """Suggest relevant questions based on available data."""
        questions = []
        
        if company_name:
            questions.extend([
                f"What was {company_name}'s revenue in the most recent quarter?",
                f"What were {company_name}'s key financial metrics?",
                f"What strategic initiatives did {company_name} mention?",
                f"What were {company_name}'s main challenges or risks?",
                f"How did {company_name} perform compared to previous quarters?"
            ])
        else:
            questions.extend([
                "What were the key financial trends across companies?",
                "Which companies showed the strongest growth?",
                "What were the common risk factors mentioned?",
                "What were the main strategic themes across companies?",
                "How did different sectors perform?"
            ])
        
        if year and quarter:
            questions.extend([
                f"What were the key developments in {year} {quarter}?",
                f"Which companies performed best in {year} {quarter}?",
                f"What were the main challenges in {year} {quarter}?"
            ])
        
        return questions

# Example usage
if __name__ == "__main__":
    # This would be used within the main application
    pass 