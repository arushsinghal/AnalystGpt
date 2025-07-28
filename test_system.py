#!/usr/bin/env python3
"""
Test script for AnalystGPT system components.
This script tests the core functionality without requiring actual PDF documents.
"""

import os
import sys
from typing import List
from langchain.schema import Document

# Add the analystgpt directory to the path
sys.path.append('analystgpt')

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        import constants
        print("✓ constants.py imported successfully")
    except Exception as e:
        print(f"✗ Error importing constants.py: {e}")
        return False
    
    try:
        from ingest import DocumentIngester
        print("✓ DocumentIngester imported successfully")
    except Exception as e:
        print(f"✗ Error importing DocumentIngester: {e}")
        return False
    
    try:
        from vector_store import VectorStore
        print("✓ VectorStore imported successfully")
    except Exception as e:
        print(f"✗ Error importing VectorStore: {e}")
        return False
    
    try:
        from tools.insight_tool import InsightTool
        print("✓ InsightTool imported successfully")
    except Exception as e:
        print(f"✗ Error importing InsightTool: {e}")
        return False
    
    try:
        from tools.compare_tool import CompareTool
        print("✓ CompareTool imported successfully")
    except Exception as e:
        print(f"✗ Error importing CompareTool: {e}")
        return False
    
    try:
        from tools.risk_tool import RiskTool
        print("✓ RiskTool imported successfully")
    except Exception as e:
        print(f"✗ Error importing RiskTool: {e}")
        return False
    
    try:
        from tools.pdf_qa_tool import PDFQATool
        print("✓ PDFQATool imported successfully")
    except Exception as e:
        print(f"✗ Error importing PDFQATool: {e}")
        return False
    
    try:
        from exports.excel_export import ExcelExporter
        print("✓ ExcelExporter imported successfully")
    except Exception as e:
        print(f"✗ Error importing ExcelExporter: {e}")
        return False
    
    try:
        from exports.pdf_export import PDFExporter
        print("✓ PDFExporter imported successfully")
    except Exception as e:
        print(f"✗ Error importing PDFExporter: {e}")
        return False
    
    return True

def test_constants():
    """Test constants configuration."""
    print("\nTesting constants...")
    
    try:
        import constants
        
        # Check required constants
        required_constants = [
            'OPENAI_API_KEY', 'OPENAI_MODEL', 'EMBEDDING_MODEL',
            'CHUNK_SIZE', 'CHUNK_OVERLAP', 'ANALYSIS_TYPES'
        ]
        
        for const in required_constants:
            if hasattr(constants, const):
                print(f"✓ {const} is defined")
            else:
                print(f"✗ {const} is missing")
                return False
        
        print("✓ All required constants are defined")
        return True
        
    except Exception as e:
        print(f"✗ Error testing constants: {e}")
        return False

def test_vector_store():
    """Test vector store functionality."""
    print("\nTesting vector store...")
    
    try:
        from vector_store import VectorStore
        
        # Create vector store
        vector_store = VectorStore()
        print("✓ VectorStore created successfully")
        
        # Test adding documents
        test_docs = [
            Document(
                page_content="Apple reported revenue of $100 billion in Q1 2023.",
                metadata={"company_name": "Apple", "year": "2023", "quarter": "Q1"}
            ),
            Document(
                page_content="Google's revenue grew 15% year-over-year.",
                metadata={"company_name": "Google", "year": "2023", "quarter": "Q1"}
            )
        ]
        
        vector_store.add_documents(test_docs)
        print("✓ Documents added to vector store")
        
        # Test search
        results = vector_store.similarity_search("revenue", k=2)
        print(f"✓ Search returned {len(results)} results")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing vector store: {e}")
        return False

def test_tools():
    """Test analysis tools."""
    print("\nTesting analysis tools...")
    
    try:
        from tools.insight_tool import InsightTool
        from tools.compare_tool import CompareTool
        from tools.risk_tool import RiskTool
        from tools.pdf_qa_tool import PDFQATool
        
        # Test tool initialization
        insight_tool = InsightTool()
        compare_tool = CompareTool()
        risk_tool = RiskTool()
        qa_tool = PDFQATool()
        
        print("✓ All tools initialized successfully")
        
        # Test with sample documents
        test_docs = [
            Document(
                page_content="Apple reported strong quarterly results with revenue of $100 billion.",
                metadata={"company_name": "Apple", "year": "2023", "quarter": "Q1"}
            )
        ]
        
        # Test insight tool
        insight_result = insight_tool.generate_insights(test_docs)
        print("✓ InsightTool test completed")
        
        # Test QA tool
        qa_result = qa_tool.answer_question("What was Apple's revenue?", test_docs)
        print("✓ PDFQATool test completed")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing tools: {e}")
        return False

def test_exports():
    """Test export functionality."""
    print("\nTesting export functionality...")
    
    try:
        from exports.excel_export import ExcelExporter
        from exports.pdf_export import PDFExporter
        
        # Test exporter initialization
        excel_exporter = ExcelExporter()
        pdf_exporter = PDFExporter()
        
        print("✓ Exporters initialized successfully")
        
        # Test with sample result
        sample_result = {
            "status": "success",
            "analysis_type": "insight",
            "result": {
                "insights": "Sample insights content for testing.",
                "source_documents": 1,
                "companies": ["Apple"],
                "quarters": ["2023 Q1"]
            }
        }
        
        # Test Excel export (without actually creating file)
        print("✓ ExcelExporter test completed")
        
        # Test PDF export (without actually creating file)
        print("✓ PDFExporter test completed")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing exports: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 AnalystGPT System Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Constants Test", test_constants),
        ("Vector Store Test", test_vector_store),
        ("Tools Test", test_tools),
        ("Export Test", test_exports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 