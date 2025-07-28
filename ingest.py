import os
import re
import fitz  # PyMuPDF
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import constants

class DocumentIngester:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=constants.CHUNK_SIZE,
            chunk_overlap=constants.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def extract_company_info(self, filename: str) -> Dict[str, str]:
        """Extract company name, year, quarter from filename or content."""
        # Try to extract from filename first
        filename_lower = filename.lower()
        
        # Common company patterns
        company_patterns = {
            'apple': ['apple', 'aapl'],
            'google': ['google', 'alphabet', 'googl'],
            'microsoft': ['microsoft', 'msft'],
            'amazon': ['amazon', 'amzn'],
            'tesla': ['tesla', 'tsla'],
            'netflix': ['netflix', 'nflx'],
            'meta': ['meta', 'facebook', 'fb'],
            'nvidia': ['nvidia', 'nvda']
        }
        
        company_name = "Unknown"
        for company, patterns in company_patterns.items():
            if any(pattern in filename_lower for pattern in patterns):
                company_name = company.title()
                break
        
        # Extract year and quarter
        year_match = re.search(r'20\d{2}', filename)
        year = year_match.group() if year_match else "Unknown"
        
        quarter_match = re.search(r'Q[1-4]', filename, re.IGNORECASE)
        quarter = quarter_match.group().upper() if quarter_match else "Unknown"
        
        return {
            "company_name": company_name,
            "year": year,
            "quarter": quarter
        }
    
    def extract_section_info(self, text: str, page_num: int) -> str:
        """Extract section information from text."""
        # Common financial report sections
        sections = [
            "executive summary", "management discussion", "financial highlights",
            "risk factors", "business overview", "results of operations",
            "liquidity and capital resources", "market risk", "legal proceedings"
        ]
        
        text_lower = text.lower()
        for section in sections:
            if section in text_lower:
                return section.replace(" ", "_")
        
        return f"page_{page_num}"
    
    def process_pdf(self, file_path: str) -> List[Document]:
        """Process a PDF file and return structured chunks."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract basic info from filename
        filename = os.path.basename(file_path)
        company_info = self.extract_company_info(filename)
        print(f"🔍 Processing file: {file_path}")
        print(f"📂 Company Info: {company_info}")
        print(f"[DEBUG] Processing file: {filename}")
        print(f"[DEBUG] Extracted company info: {company_info}")
        
        # Open PDF and extract text
        doc = fitz.open(file_path)
        chunks = []
        chunk_index = 0
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            print(f"📄 Page {page_num+1}: {len(text)} characters extracted")
            print(f"[DEBUG] Page {page_num + 1}: Extracted {len(text)} characters")
            
            if not text.strip():
                print("⚠️ Empty page skipped")
                print(f"[DEBUG] Page {page_num + 1} is empty. Skipping.")

                continue
            
            # Extract section info
            section = self.extract_section_info(text, page_num)
            print(f"[DEBUG] Extracted section: {section}")
            
            # Split text into chunks
            page_chunks = self.text_splitter.split_text(text)
            print(f"[DEBUG] Split into {len(page_chunks)} chunks")
            
            for i, chunk_text in enumerate(page_chunks):
                if not chunk_text.strip():
                    continue
                
                # Create metadata
                metadata = {
                    **company_info,
                    "section": section,
                    "source_file": filename,
                    "page_number": page_num + 1,
                    "chunk_index": chunk_index
                }
                
                # Create Document object
                doc_chunk = Document(
                    page_content=chunk_text,
                    metadata=metadata
                )
                
                chunks.append(doc_chunk)
                chunk_index += 1
        
        doc.close()
        return chunks
    
    def process_directory(self, directory_path: str) -> List[Document]:
        """Process all PDF files in a directory."""
        all_chunks = []
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(directory_path, filename)
                try:
                    chunks = self.process_pdf(file_path)
                    all_chunks.extend(chunks)
                    print(f"Processed {filename}: {len(chunks)} chunks")
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
        
        return all_chunks

# Example usage
if __name__ == "__main__":
    ingester = DocumentIngester()
    
    # Process a single file
    # chunks = ingester.process_pdf("path/to/earnings_report.pdf")
    
    # Process a directory
    # chunks = ingester.process_directory("path/to/documents/")
    
    # print(f"Total chunks: {len(chunks)}")
