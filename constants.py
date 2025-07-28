import os
from dotenv import load_dotenv

load_dotenv()

# Google Gemini Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in environment. Please set it in the .env file.")

GEMINI_MODEL = "gemini-1.5-pro"

# Vector Database Configuration
VECTOR_DB_PATH = "vector_store"
EMBEDDING_MODEL = "models/embedding-001"  # Google's embedding model
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# File Processing
SUPPORTED_FORMATS = (".pdf",)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Analysis Types
ANALYSIS_TYPES = {
    "insight": "Generate key insights and business metrics",
    "compare": "Compare companies or quarters",
    "risk": "Extract risk disclosures and flagged language",
    "qa": "Answer specific questions about the documents"
}

# Metadata Fields
METADATA_FIELDS = [
    "company_name",
    "year",
    "quarter", 
    "section",
    "source_file",
    "page_number",
    "chunk_index"
]

# Export Options
EXPORT_FORMATS = ("pdf", "excel")
