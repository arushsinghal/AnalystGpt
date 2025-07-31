from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
import constants

# Import our tools
from tools.insight_tool import InsightTool
from tools.compare_tool import CompareTool
from tools.risk_tool import RiskTool
from tools.pdf_qa_tool import PDFQATool

class AnalystGPTAgent:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = ChatGoogleGenerativeAI(
            model=constants.GEMINI_MODEL,
            google_api_key=constants.GOOGLE_API_KEY,
            temperature=0.1
        )

        self.insight_tool = InsightTool()
        self.compare_tool = CompareTool()
        self.risk_tool = RiskTool()
        self.qa_tool = PDFQATool()

        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(state_schema=Dict[str, Any])

        workflow.add_node("route", self._route_request)
        workflow.add_node("insight", self._run_insight_analysis)
        workflow.add_node("compare", self._run_compare_analysis)
        workflow.add_node("risk", self._run_risk_analysis)
        workflow.add_node("qa", self._run_qa_analysis)
        workflow.add_node("format_response", self._format_response)


        workflow.add_conditional_edges(
            "route",
            self._route_request,
            {
                "insight": "insight",
                "compare": "compare",
                "risk": "risk",
                "qa": "qa"
            }
        )

        workflow.add_edge("insight", "format_response")
        workflow.add_edge("compare", "format_response")
        workflow.add_edge("risk", "format_response")
        workflow.add_edge("qa", "format_response")
        workflow.add_edge("format_response", END)

        workflow.set_entry_point("route")

        return workflow.compile()
    def _route_request(self, state: Dict[str, Any]) -> str:
        analysis_type = state.get("analysis_type", "qa")
        return analysis_type if analysis_type in {"insight", "compare", "risk", "qa"} else "qa"

    def _run_insight_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            company = state.get("company")
            year = state.get("year")
            quarter = state.get("quarter")

            if company:
                result = self.insight_tool.generate_company_insights(company, self.vector_store)
            elif year and quarter:
                result = self.insight_tool.generate_quarter_insights(year, quarter, self.vector_store)
            else:
                documents = self.vector_store.similarity_search("financial performance", k=10)
                result = self.insight_tool.generate_insights(documents)

            state["analysis_result"] = result
            return state

        except Exception as e:
            state["error"] = f"Error in insight analysis: {str(e)}"
            return state

    def _run_compare_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            company1 = state.get("company1")
            company2 = state.get("company2")
            year1 = state.get("year1")
            quarter1 = state.get("quarter1")
            year2 = state.get("year2")
            quarter2 = state.get("quarter2")

            if company1 and company2:
                result = self.compare_tool.compare_companies(company1, company2, self.vector_store)
            elif year1 and quarter1 and year2 and quarter2:
                result = self.compare_tool.compare_quarters(year1, quarter1, year2, quarter2, self.vector_store)
            else:
                state["error"] = "Insufficient parameters for comparison"
                return state

            state["analysis_result"] = result
            return state

        except Exception as e:
            state["error"] = f"Error in compare analysis: {str(e)}"
            return state

    def _run_risk_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            company = state.get("company")
            year = state.get("year")
            quarter = state.get("quarter")

            if company:
                result = self.risk_tool.analyze_company_risks(company, self.vector_store)
            elif year and quarter:
                result = self.risk_tool.analyze_quarter_risks(year, quarter, self.vector_store)
            else:
                documents = self.vector_store.similarity_search("risk factors", k=10)
                result = self.risk_tool.analyze_risks(documents)

            state["analysis_result"] = result
            return state

        except Exception as e:
            state["error"] = f"Error in risk analysis: {str(e)}"
            return state

    def _run_qa_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            question = state.get("question", "")
            company = state.get("company")
            year = state.get("year")
            quarter = state.get("quarter")

            if not question:
                state["error"] = "No question provided"
                return state

            if company:
                result = self.qa_tool.answer_company_question(question, company, self.vector_store)
            elif year and quarter:
                result = self.qa_tool.answer_quarter_question(question, year, quarter, self.vector_store)
            else:
                result = self.qa_tool.answer_general_question(question, self.vector_store)

            state["analysis_result"] = result
            return state

        except Exception as e:
            state["error"] = f"Error in QA analysis: {str(e)}"
            return state

    def _format_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        analysis_type = state.get("analysis_type", "qa")
        analysis_result = state.get("analysis_result", {})
        error = state.get("error")

        if error:
            state["response"] = {
                "status": "error",
                "message": error,
                "analysis_type": analysis_type
            }
        else:
            state["response"] = {
                "status": "success",
                "analysis_type": analysis_type,
                "result": analysis_result
            }

        return state

    def run_analysis(self, analysis_type: str, **kwargs) -> Dict[str, Any]:
        state = {"analysis_type": analysis_type, **kwargs}
        result = self.graph.invoke(state)
        return result.get("response", {"status": "error", "message": "Unknown error"})

    def get_available_companies(self) -> List[str]:
        return self.vector_store.get_all_companies()

    def get_available_quarters(self) -> List[Dict[str, str]]:
        return self.vector_store.get_all_quarters()

    def get_store_stats(self) -> Dict[str, Any]:
        return self.vector_store.get_store_stats()
