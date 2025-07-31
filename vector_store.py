import os
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import constants

class VectorStore:
    def __init__(self, db_path: str = constants.VECTOR_DB_PATH):
        self.db_path = db_path
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=constants.EMBEDDING_MODEL,
            google_api_key=constants.GOOGLE_API_KEY
        )
        self.vector_store = None
        self._load_or_create_store()
    
    def _load_or_create_store(self):
        """Load existing vector store or create new one."""
        if os.path.exists(self.db_path):
            try:
                self.vector_store = FAISS.load_local(
                    self.db_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"Loaded existing vector store from {self.db_path}")
            except Exception as e:
                print(f"Error loading vector store: {e}")
                self.vector_store = None
        else:
            self.vector_store = None
        
        if self.vector_store is None:
            print(f"Vector store will be created when first documents are added")

    def add_documents(self,documents:List[Document])->int:
        if not documents:
            print("No documents to add")
            return 0
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            print(f"Created new vector store with {len(documents)} documents")
        else:
            self.vector_store.add_documents(documents)
            print(f"Added {len(documents)} documents to existing vector store")
        self.save()
        return len(documents)
    
    def save(self):
        """Save the vector store to disk."""
        if self.vector_store:
            self.vector_store.save_local(self.db_path)
            print(f"Saved vector store to {self.db_path}")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents."""
        if not self.vector_store:
            return []
        
        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
    
    def search_by_company(self, company_name: str, query: str = "", k: int = 5) -> List[Document]:
        """Search for documents from a specific company."""
        if not self.vector_store:
            return []
        
        try:
            # Combine company filter with query
            search_query = f"company: {company_name}"
            if query:
                search_query += f" {query}"
            
            return self.vector_store.similarity_search(search_query, k=k)
        except Exception as e:
            print(f"Error in company search: {e}")
            return []
    
    def search_by_quarter(self, year: str, quarter: str, query: str = "", k: int = 5) -> List[Document]:
        """Search for documents from a specific quarter."""
        if not self.vector_store:
            return []
        
        try:
            # Combine quarter filter with query
            search_query = f"quarter: {year} {quarter}"
            if query:
                search_query += f" {query}"
            
            return self.vector_store.similarity_search(search_query, k=k)
        except Exception as e:
            print(f"Error in quarter search: {e}")
            return []
    
    def get_all_companies(self) -> List[str]:
        """Get list of all companies in the store."""
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.docstore._dict.values()
            companies = list(set(doc.metadata.get("company_name", "Unknown") for doc in docs))
            return sorted(c for c in companies if c != "Unknown")
        except Exception as e:
            print(f"Error getting companies: {e}")
            return []
    
    def get_all_quarters(self) -> List[Dict[str, str]]:
        """Get list of all quarters in the store."""
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.docstore._dict.values()
            quarters = list(set(
                {"year": doc.metadata.get("year", "Unknown"), "quarter": doc.metadata.get("quarter", "Unknown")}
                for doc in docs
            ))
            return sorted([q for q in quarters if q["year"] != "Unknown" and q["quarter"] != "Unknown"], key=lambda x: (x["year"], x["quarter"]))
        except Exception as e:
            print(f"Error getting quarters: {e}")
            return []
    
    def get_store_stats(self) -> Dict[str, Any]:
        if not self.vector_store:
            return {"total_documents": 0}
    
        try:
            return {"total_documents": len(self.vector_store.docstore._dict)}
        except Exception as e:
            print(f"Error getting store stats: {e}")
            return {"total_documents": 0}


# Example usage
if __name__ == "__main__":
    vector_store = VectorStore()
    
    # Example search
    # results = vector_store.similarity_search("revenue growth", k=3)
    # for doc in results:
    #     print(f"Company: {doc.metadata.get('company_name')}")
    #     print(f"Content: {doc.page_content[:200]}...")
    #     print("---")
