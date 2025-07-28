import streamlit as st
import os
import tempfile
from typing import Dict, Any
import constants
from ingest import DocumentIngester
from vector_store import VectorStore
from graph import AnalystGPTAgent
from exports.excel_export import ExcelExporter
from exports.pdf_export import PDFExporter

# Page configuration
st.set_page_config(
    page_title="AnalystGPT - Financial Document Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False

def initialize_system():
    """Initialize the vector store and agent."""
    try:
        if st.session_state.vector_store is None:
            st.session_state.vector_store = VectorStore()
        
        if st.session_state.agent is None:
            st.session_state.agent = AnalystGPTAgent(st.session_state.vector_store)
        
        return True
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        return False

def upload_and_process_documents():
    """Handle document upload and processing."""
    st.header("📁 Document Upload")
    
    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload multiple PDF files for analysis"
    )
    
    if uploaded_files:
        if st.button("Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                try:
                    # Initialize system
                    if not initialize_system():
                        return
                    
                    # Create temporary directory for uploaded files
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Save uploaded files
                        file_paths = []
                        for uploaded_file in uploaded_files:
                            file_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getvalue())
                            file_paths.append(file_path)
                        
                        # Process documents
                        ingester = DocumentIngester()
                        all_chunks = []
                        
                        for file_path in file_paths:
                            chunks = ingester.process_pdf(file_path)
                            if not chunks:
                                st.warning(f"No chunks extracted from {file_path} pdf might be empty")
                                continue
                            all_chunks.extend(chunks)
                        
                        # Add to vector store
                        st.session_state.vector_store.add_documents(all_chunks)
                        st.session_state.documents_loaded = True
                        
                        st.success(f"Successfully processed {len(uploaded_files)} documents with {len(all_chunks)} chunks")
                        
                except Exception as e:
                    st.error(f"Error processing documents: {str(e)}")

def analysis_interface():
    """Main analysis interface."""
    st.header("🔍 Analysis Interface")
    
    if not st.session_state.documents_loaded:
        st.warning("Please upload and process documents first.")
        return
    
    # Analysis type selection
    analysis_type = st.selectbox(
        "Select Analysis Type",
        options=list(constants.ANALYSIS_TYPES.keys()),
        format_func=lambda x: constants.ANALYSIS_TYPES[x]
    )
    
    # Get available companies and quarters
    try:
        companies = st.session_state.agent.get_available_companies()
        quarters = st.session_state.agent.get_available_quarters()
    except Exception as e:
        st.error(f"Error getting available data: {str(e)}")
        companies=[]
        quarters=[]
    if not companies:
        companies = []
    if not quarters:
        quarters = []
    
    # Analysis parameters based on type
    if analysis_type == "insight":
        st.subheader("Insight Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            company = st.selectbox("Company (Optional)", [""] + companies)
        with col2:
            quarter_options = [""]
            for q in quarters:
                if isinstance(q,dict) and "year" in q and "quarter" in q:
                    quarter_options.append(f"{q['year']} {q['quarter']}")
            quarter_data = st.selectbox("Quarter (Optional)", quarter_options)
            
        
        if st.button("Generate Insights", type="primary"):
            with st.spinner("Generating insights..."):
                try:
                    params = {}
                    if company:
                        params["company"] = company
                    if quarter_data:
                        year, quarter = quarter_data.split()
                        params["year"] = year
                        params["quarter"] = quarter
                    
                    result = st.session_state.agent.run_analysis("insight", **params)
                    display_result(result, "insight")
                    
                except Exception as e:
                    st.error(f"Error generating insights: {str(e)}")
    
    elif analysis_type == "compare":
        st.subheader("Comparative Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            company1 = st.selectbox("Company 1", companies)
            year1 = st.selectbox("Year 1", ["2023", "2024"], key="year1")
            quarter1 = st.selectbox("Quarter 1", ["Q1", "Q2", "Q3", "Q4"], key="quarter1")
        
        with col2:
            company2 = st.selectbox("Company 2", companies)
            year2 = st.selectbox("Year 2", ["2023", "2024"], key="year2")
            quarter2 = st.selectbox("Quarter 2", ["Q1", "Q2", "Q3", "Q4"], key="quarter2")
        
        if st.button("Compare", type="primary"):
            with st.spinner("Running comparison..."):
                try:
                    result = st.session_state.agent.run_analysis("compare", 
                        company1=company1, company2=company2,
                        year1=year1, quarter1=quarter1,
                        year2=year2, quarter2=quarter2
                    )
                    display_result(result, "compare")
                    
                except Exception as e:
                    st.error(f"Error running comparison: {str(e)}")
    
    elif analysis_type == "risk":
        st.subheader("Risk Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            company = st.selectbox("Company (Optional)", [""] + companies, key="risk_company")
        with col2:
            quarter_options = [""]
            for q in quarters:
                if isinstance(q, dict) and "year" in q and "quarter" in q:
                    quarter_options.append(f"{q['year']} {q['quarter']}")
            quarter_data = st.selectbox("Quarter (Optional)", quarter_options, key="risk_quarter")
            
        
        if st.button("Analyze Risks", type="primary"):
            with st.spinner("Analyzing risks..."):
                try:
                    params = {}
                    if company:
                        params["company"] = company
                    if quarter_data:
                        year, quarter = quarter_data.split()
                        params["year"] = year
                        params["quarter"] = quarter
                    
                    result = st.session_state.agent.run_analysis("risk", **params)
                    display_result(result, "risk")
                    
                except Exception as e:
                    st.error(f"Error analyzing risks: {str(e)}")
    
    elif analysis_type == "qa":
        st.subheader("Question & Answer")
        
        question = st.text_area("Ask a question about the documents:", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            company = st.selectbox("Company (Optional)", [""] + companies, key="qa_company")
        with col2:
            quarter_options = [""]
            for q in quarters:
                if isinstance(q,dict) and "year" in q and "quarter" in q:
                    quarter_options.append(f"{q['year']} {q['quarter']}")
            quarter_data=st.selectbox("Quarter (Optional)",quarter_options, key="qa_quarter")
        if st.button("Get Answer", type="primary"):
            with st.spinner("Finding answer..."):
                try:
                    params = {"question": question}
                    if company:
                        params["company"] = company
                    if quarter_data:
                        year, quarter = quarter_data.split()
                        params["year"] = year
                        params["quarter"] = quarter
                    
                    result = st.session_state.agent.run_analysis("qa", **params)
                    display_result(result, "qa")
                    
                except Exception as e:
                    st.error(f"Error getting answer: {str(e)}")

def display_result(result: Dict[str, Any], analysis_type: str):
    """Display analysis results."""
    if result.get("status") == "error":
        st.error(f"Error: {result.get('message', 'Unknown error')}")
        return
    
    # Display result
    st.subheader("Analysis Results")
    
    analysis_result = result.get("result", {})
    
    if analysis_type == "insight":
        if "insights" in analysis_result:
            st.markdown(analysis_result["insights"])
    
    elif analysis_type == "compare":
        if "comparison" in analysis_result:
            st.markdown(analysis_result["comparison"])
    
    elif analysis_type == "risk":
        if "risk_analysis" in analysis_result:
            st.markdown(analysis_result["risk_analysis"])
    
    elif analysis_type == "qa":
        if "answer" in analysis_result:
            st.markdown(f"**Question:** {analysis_result.get('question', '')}")
            st.markdown(f"**Answer:** {analysis_result.get('answer', '')}")
    
    # Display metadata
    with st.expander("Analysis Details"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Source Documents", analysis_result.get("source_documents", 0))
        with col2:
            st.metric("Companies", len(analysis_result.get("companies", [])))
        with col3:
            st.metric("Quarters", len(analysis_result.get("quarters", [])))
        
        if analysis_result.get("companies"):
            st.write("**Companies:**", ", ".join(analysis_result["companies"]))
        if analysis_result.get("quarters"):
            st.write("**Quarters:**", ", ".join(analysis_result["quarters"]))
    
    # Export options
    st.subheader("Export Results")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export to Excel"):
            try:
                exporter = ExcelExporter()
                filepath = exporter.export_analysis_result(result, analysis_type)
                st.success(f"Exported to: {filepath}")
            except Exception as e:
                st.error(f"Error exporting to Excel: {str(e)}")
    
    with col2:
        if st.button("Export to PDF"):
            try:
                exporter = PDFExporter()
                filepath = exporter.export_analysis_result(result, analysis_type)
                st.success(f"Exported to: {filepath}")
            except Exception as e:
                st.error(f"Error exporting to PDF: {str(e)}")

def system_status():
    """Display system status and statistics."""
    st.header("📊 System Status")
    
    if not initialize_system():
        return
    
    try:
        stats = st.session_state.agent.get_store_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Documents", stats.get("total_documents", 0))
        with col2:
            st.metric("Companies", len(stats.get("companies", [])))
        with col3:
            st.metric("Quarters", len(stats.get("quarters", [])))
        
        if stats.get("companies"):
            st.write("**Available Companies:**", ", ".join(stats["companies"]))
        
        if stats.get("quarters"):
            quarters_str = [f"{q['year']} {q['quarter']}" for q in stats["quarters"]]
            st.write("**Available Quarters:**", ", ".join(quarters_str))
            
    except Exception as e:
        st.error(f"Error getting system status: {str(e)}")

def main():
    """Main application."""
    st.markdown('<h1 class="main-header">📊 AnalystGPT</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Financial Document Analysis</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Upload Documents", "Analysis", "System Status"]
    )
    
    # Page routing
    if page == "Upload Documents":
        upload_and_process_documents()
    elif page == "Analysis":
        analysis_interface()
    elif page == "System Status":
        system_status()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">AnalystGPT - Financial Document Analysis System</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
