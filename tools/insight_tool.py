from typing import List, Dict, Any
import os
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import constants

class InsightTool:
    def __init__(self):
        print("🚀 Initializing InsightTool...")
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=constants.GEMINI_MODEL,
                google_api_key=constants.GOOGLE_API_KEY,
                temperature=0.1
            )
            print("✅ LLM initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing LLM: {e}")
            raise
        
        self.prompt_template = PromptTemplate(
            input_variables=["context"],
            template=self._load_prompt_template()
        )
    
    def _load_prompt_template(self) -> str:
        """Load the insight prompt template."""
        # Fix path resolution
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        prompt_path = os.path.join(project_root, "prompts", "insight_prompt.txt")
        
        try:
            with open(prompt_path, "r", encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️ Template file not found at: {prompt_path}, using default")
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
        print(f"🔍 Starting insight generation with {len(documents)} documents")
        
        if not documents:
            print("❌ No documents provided")
            return {"error": "No documents provided"}
        
        try:
            # Prepare context from documents
            context = self._prepare_context(documents)
            print(f"📝 Context prepared, length: {len(context)} characters")
            
            # Check context length
            if len(context) > 25000:
                context = context[:25000] + "\n...[Content truncated]"
                print("⚠️ Context truncated due to length")
            
            # Generate prompt
            prompt = self.prompt_template.format(context=context)
            print("📋 Prompt generated")
            
            # Make API call using invoke (not predict)
            print("🚀 Making API call...")
            response = self.llm.invoke(prompt)
            print("✅ API call successful")
            
            # Extract content from response
            if hasattr(response, 'content'):
                insights_text = response.content
            elif hasattr(response, 'text'):
                insights_text = response.text
            else:
                insights_text = str(response)
            
            # Safely extract metadata
            companies = []
            quarters = []
            
            for doc in documents:
                try:
                    if hasattr(doc, 'metadata') and doc.metadata:
                        company = doc.metadata.get("company_name", "Unknown")
                        if company and company != "Unknown":
                            companies.append(company)
                        
                        year = doc.metadata.get("year", "Unknown")
                        quarter = doc.metadata.get("quarter", "Unknown")
                        if year and quarter and year != "Unknown" and quarter != "Unknown":
                            quarters.append(f"{year} {quarter}")
                except Exception as e:
                    print(f"⚠️ Error extracting metadata from document: {e}")
                    continue
            
            result = {
                "insights": insights_text,
                "source_documents": len(documents),
                "companies": list(set(companies)) if companies else ["Unknown"],
                "quarters": list(set(quarters)) if quarters else ["Unknown"]
            }
            
            print("✅ Insights generated successfully")
            return result
        
        except Exception as e:
            error_msg = f"Error generating insights: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {"error": error_msg}
    
    def generate_company_insights(self, company_name: str, vector_store) -> Dict[str, Any]:
        """Generate insights for a specific company."""
        print(f"🏢 Generating insights for company: {company_name}")
        
        try:
            # Check if vector_store has required methods
            if hasattr(vector_store, 'search_by_company'):
                documents = vector_store.search_by_company(company_name, "financial performance", k=10)
            elif hasattr(vector_store, 'similarity_search'):
                documents = vector_store.similarity_search(f"financial performance {company_name}", k=10)
            else:
                return {"error": "Vector store does not support required search methods"}
            
            print(f"📚 Found {len(documents)} documents for {company_name}")
            
            if not documents:
                return {"error": f"No documents found for company: {company_name}"}
            
            return self.generate_insights(documents)
        
        except Exception as e:
            error_msg = f"Error searching for company documents: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def generate_quarter_insights(self, year: str, quarter: str, vector_store) -> Dict[str, Any]:
        """Generate insights for a specific quarter."""
        print(f"📅 Generating insights for quarter: {year} {quarter}")
        
        try:
            # Check if vector_store has required methods
            if hasattr(vector_store, 'search_by_quarter'):
                documents = vector_store.search_by_quarter(year, quarter, "financial performance", k=10)
            elif hasattr(vector_store, 'similarity_search'):
                documents = vector_store.similarity_search(f"financial performance {year} {quarter}", k=10)
            else:
                return {"error": "Vector store does not support required search methods"}
            
            print(f"📚 Found {len(documents)} documents for {year} {quarter}")
            
            if not documents:
                return {"error": f"No documents found for {year} {quarter}"}
            
            return self.generate_insights(documents)
        
        except Exception as e:
            error_msg = f"Error searching for quarter documents: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def _prepare_context(self, documents: List[Document]) -> str:
        """Prepare context from documents for analysis."""
        print(f"📝 Preparing context from {len(documents)} documents")
        
        context_parts = []
        
        for i, doc in enumerate(documents):
            try:
                # Safely extract metadata
                if hasattr(doc, 'metadata') and doc.metadata:
                    company = doc.metadata.get("company_name", "Unknown")
                    year = doc.metadata.get("year", "Unknown")
                    quarter = doc.metadata.get("quarter", "Unknown")
                    section = doc.metadata.get("section", "Unknown")
                else:
                    company = year = quarter = section = "Unknown"
                
                header = f"Document {i+1}: {company} - {year} {quarter} - {section}"
                
                # Safely extract content
                if hasattr(doc, 'page_content') and doc.page_content:
                    content = str(doc.page_content)[:1200]  # Increased limit
                    # Clean content
                    content = content.replace('\x00', '').replace('\r', '\n').strip()
                else:
                    content = "No content available"
                
                context_parts.append(f"{header}\n{content}\n{'-'*50}\n")
                
            except Exception as e:
                print(f"⚠️ Error processing document {i}: {e}")
                context_parts.append(f"Document {i+1}: Error processing document\n{'-'*50}\n")
        
        # Join all parts and return
        final_context = "\n".join(context_parts)
        print(f"✅ Context prepared, final length: {len(final_context)} characters")
        return final_context
    
    def test_connection(self) -> bool:
        """Test if the LLM connection is working."""
        try:
            print("🧪 Testing LLM connection...")
            test_response = self.llm.invoke("Hello, please respond with 'Connection successful'")
            
            if hasattr(test_response, 'content'):
                response_text = test_response.content
            else:
                response_text = str(test_response)
            
            print(f"✅ Test response: {response_text[:100]}...")
            return True
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

# Test the tool
if __name__ == "__main__":
    try:
        print("🚀 Testing InsightTool...")
        tool = InsightTool()
        
        # Test connection
        if tool.test_connection():
            print("✅ Tool is working correctly")
        else:
            print("❌ Tool connection failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")