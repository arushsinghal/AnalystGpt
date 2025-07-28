# AnalystGPT - AI-Powered Financial Document Analysis

AnalystGPT is an intelligent financial document analysis system that ingests PDF earnings reports, extracts structured insights, and answers analytical queries using Retrieval-Augmented Generation (RAG). The system simulates the capabilities of a junior equity research analyst.


🛠️ Technical Summary
AnalystGPT is a full-stack AI application for financial document analysis, built with the following architecture:
Frontend:
Streamlit web app for interactive document upload, analysis selection, and results visualization.
Backend Processing:
PDF ingestion and parsing using PyMuPDF.
Document chunking with LangChain’s RecursiveCharacterTextSplitter.
Metadata extraction (company, year, quarter, section) from filenames and content.
Vector Database:
Embedding of document chunks using Google Gemini’s embedding model.
Storage and retrieval via FAISS for fast semantic search.
AI Analysis Layer:
Four modular tools (Insight, Compare, Risk, Q&A) orchestrated via a LangGraph agent.
Each tool uses retrieval-augmented generation (RAG): relevant chunks are retrieved and passed to Google Gemini LLM for context-aware analysis.
Export & Reporting:
Results can be exported to Excel or PDF with full metadata and source attribution.
Configuration & Extensibility:
Environment variables and constants for easy model/API switching.
Modular codebase for adding new analysis tools or data sources.

💼 Business-Focused Summary
AnalystGPT is an AI-powered research assistant designed to transform how financial professionals analyze and extract value from earnings reports and other financial documents.
Automates Analysis:
Instantly processes and analyzes large volumes of financial PDFs, saving hours of manual work.
Delivers Actionable Insights:
Extracts key business metrics, strategic highlights, and risk factors in clear, structured formats.
Enables Smart Comparisons:
Compares companies or time periods across financial and strategic dimensions, supporting better investment decisions.
On-Demand Q&A:
Answers complex, document-grounded questions, enabling deep dives without manual searching.
Professional Reporting:
Exports results to Excel or PDF for easy sharing and compliance.
For Analysts, Investors, and Executives:
Empowers financial teams to make faster, more informed decisions with AI-driven insights and risk analysis.
In short:
AnalystGPT combines the power of AI, vector search, and modern web technology to deliver a scalable, explainable, and user-friendly platform for financial document intelligence—bridging the gap between raw data and actionable business insight.


## 🚀 Features

### Core Capabilities
- **Document Ingestion**: Process multiple PDF earnings reports with automatic metadata extraction
- **Vector Storage**: Store document chunks with embeddings for efficient retrieval
- **Multi-Tool Analysis**: Four specialized analysis tools:
  - **InsightTool**: Generate key business insights and metrics
  - **CompareTool**: Compare companies or quarters across metrics
  - **RiskTool**: Extract and analyze risk disclosures
  - **PDFQATool**: Answer specific questions about documents
- **LangGraph Agent**: Orchestrated workflow with intelligent routing
- **Streamlit Interface**: User-friendly web application
- **Export Functionality**: Export results to Excel or PDF

### Analysis Types
1. **Insight Analysis**: Extract key financial metrics, business highlights, and strategic initiatives
2. **Comparative Analysis**: Compare companies or quarters across multiple dimensions
3. **Risk Analysis**: Identify and categorize risk factors and disclosures
4. **Question & Answer**: Ask specific questions about document content

## 🏗️ Architecture

```
analystgpt/
├── app.py                 # Main Streamlit application
├── constants.py           # Configuration and constants
├── ingest.py             # Document processing and chunking
├── vector_store.py       # Vector database management
├── graph.py              # LangGraph agent system
├── tools/                # Analysis tools
│   ├── insight_tool.py   # Business insights generation
│   ├── compare_tool.py   # Comparative analysis
│   ├── risk_tool.py      # Risk analysis
│   └── pdf_qa_tool.py    # Question answering
├── exports/              # Export functionality
│   ├── excel_export.py   # Excel export
│   └── pdf_export.py     # PDF export
└── prompts/              # Prompt templates
    ├── insight_prompt.txt
    ├── compare_prompt.txt
    └── risk_prompt.txt
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd analystgpt
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 📖 Usage

### 1. Document Upload
- Navigate to the "Upload Documents" page
- Upload multiple PDF earnings reports
- Click "Process Documents" to ingest and chunk the documents

### 2. Analysis Interface
- Select analysis type (Insight, Compare, Risk, or Q&A)
- Configure parameters (company, quarter, etc.)
- Run analysis and view results

### 3. Export Results
- Export analysis results to Excel or PDF format
- Results include metadata and source information

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google API key for Gemini access

### Constants (constants.py)
- `GEMINI_MODEL`: LLM model to use (default: "gemini-1.5-pro")
- `EMBEDDING_MODEL`: Embedding model (default: "models/embedding-001")
- `CHUNK_SIZE`: Document chunk size (default: 1000)
- `CHUNK_OVERLAP`: Chunk overlap (default: 200)

## 🎯 Example Queries

### Insight Analysis
- "Generate insights for Apple Q1 2023"
- "What are the key business highlights for Google?"

### Comparative Analysis
- "Compare Apple vs Google Q1 2023 revenue"
- "Compare Q1 2023 vs Q1 2024 for Microsoft"

### Risk Analysis
- "Analyze risk factors for Tesla"
- "What are the main risks mentioned in Q1 2023?"

### Question & Answer
- "What was Apple's R&D expense in Q1 2023?"
- "How did revenue growth compare across companies?"

## 🧠 Technical Details

### Document Processing
- Uses PyMuPDF for PDF text extraction
- LangChain's RecursiveCharacterTextSplitter for chunking
- Automatic metadata extraction (company, year, quarter, section)

### Vector Storage
- FAISS vector database for efficient similarity search
- Google Gemini embeddings for document representation
- Metadata filtering for targeted searches

### Agent System
- LangGraph workflow with intelligent routing
- Multi-tool orchestration
- State management and error handling

### Analysis Tools
- **InsightTool**: Generates structured business insights
- **CompareTool**: Performs comparative analysis with quantitative metrics
- **RiskTool**: Identifies and categorizes risk factors
- **PDFQATool**: Answers specific questions with document grounding

## 📊 Export Formats

### Excel Export
- Multiple sheets for different analysis sections
- Metadata and source information
- Structured data tables

### PDF Export
- Professional formatting with custom styles
- Analysis results with metadata
- Source attribution and citations

## 🔍 System Requirements

- Python 3.8+
- Google API access (Gemini)
- Sufficient memory for vector operations
- Internet connection for API calls

## 🚀 Performance Considerations

- Document processing: ~1-2 seconds per page
- Vector search: <100ms for typical queries
- Analysis generation: 5-15 seconds depending on complexity
- Export generation: 1-3 seconds

## 🔧 Troubleshooting

### Common Issues
1. **Google API errors**: Check API key and quota
2. **Memory issues**: Reduce chunk size or document count
3. **Processing errors**: Ensure PDF files are readable
4. **Export failures**: Check write permissions in export directory

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=1
```


## Walkthrough 

🖥️ AnalystGPT Streamlit UI Overview
1. Main Layout
Header:
At the top, you’ll see the title “📊 AnalystGPT” and a subtitle “AI-Powered Financial Document Analysis”.
Sidebar Navigation:
On the left, there’s a sidebar with a dropdown menu labeled “Navigation” where you can choose between:
Upload Documents
Analysis
System Status
2. Pages and Their Functions
A. Upload Documents
Purpose: Upload and process your PDF financial documents.
What you see:
A file uploader to select one or more PDF files.
A “Process Documents” button.
Status messages (success or error) after processing.
How to use:
Click “Browse files” or drag-and-drop your PDFs.
Click “Process Documents”.
Wait for processing to complete (you’ll see a spinner and then a success or error message).
B. Analysis
Purpose: Run AI-powered analyses on your uploaded documents.
What you see:
A dropdown to select the type of analysis:
Insight (business insights)
Compare (compare companies/quarters)
Risk (risk analysis)
Q&A (ask questions)
Depending on the analysis type, you’ll see:
Dropdowns for company and/or quarter selection.
For Q&A, a text box to type your question.
Action buttons (e.g., “Generate Insights”, “Compare”, “Analyze Risks”, “Get Answer”).
After running an analysis:
Results are shown in a formatted section.
An expandable “Analysis Details” section with metadata (number of documents, companies, quarters).
Export buttons to download results as Excel or PDF.
How to use:
Select the analysis type.
Choose companies/quarters or type your question as needed.
Click the relevant action button.
View results and export if desired.
C. System Status
Purpose: View the current state of your document database.
What you see:
Metrics for total documents, companies, and quarters.
Lists of available companies and quarters.
How to use:
Just visit this page to see what’s loaded and available for analysis.
3. Footer
At the bottom, you’ll see a footer with the text:
“AnalystGPT - Financial Document Analysis System”
🧭 How to Navigate
Start on “Upload Documents”
Upload and process your PDFs.
Go to “Analysis”
Select the type of analysis you want, configure options, and run the analysis.
Check “System Status”
See what data is available and confirm your uploads.
Export Results
After any analysis, use the export buttons to download your results.
📝 Tips
You must upload and process documents before running any analysis.
If you see an error, check the message for hints (e.g., empty PDF, processing error).
Use the sidebar to quickly switch between pages.
In summary:
The UI is designed to be intuitive:
Upload → Analyze → Export/Review — all from a clean, sidebar-driven interface!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LangChain for the RAG framework
- Google Gemini for LLM capabilities
- Streamlit for the web interface
- FAISS for vector similarity search

## 📞 Support

For questions or issues, please open an issue on the repository or contact the development team.

---

**AnalystGPT** - Transforming financial document analysis with AI 