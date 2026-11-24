from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.graph.nodes.human import human_review, human_selection
from app.graph.nodes.planner import plan_topics
from app.graph.nodes.visualizer import extract_visuals, generate_images
from app.graph.nodes.writer import write_draft
from app.graph.state import AgentState


def route_after_review(state: AgentState) -> str:
    """审稿后的条件路由：APPROVE 向下走，否则回退重写。"""
    feedback = state.get("review_feedback", "")
    if feedback == "APPROVE":
        return "extract_visuals"
    return "write_draft"


def build_workflow(checkpointer) -> CompiledStateGraph:
    graph: StateGraph = StateGraph(AgentState)

    graph.add_node("plan_topics", plan_topics)
    graph.add_node("human_selection", human_selection)
    graph.add_node("write_draft", write_draft)
    graph.add_node("human_review", human_review)
    graph.add_node("extract_visuals", extract_visuals)
    graph.add_node("generate_images", generate_images)

    graph.add_edge(START, "plan_topics")
    graph.add_edge("plan_topics", "human_selection")
    graph.add_edge("human_selection", "write_draft")
    graph.add_edge("write_draft", "human_review")

    graph.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "extract_visuals": "extract_visuals",
            "write_draft": "write_draft",
        },
    )

    graph.add_edge("extract_visuals", "generate_images")
    graph.add_edge("generate_images", END)

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_selection", "human_review"],
    )
