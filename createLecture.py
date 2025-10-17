from typing import TypedDict, Annotated, List
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END

# --- Part 1: LangChain and LangGraph Workflow Definition ---
# This part of the file defines the core, reusable lecture generation logic.

class LectureState(TypedDict):
    """Represents the state of our lecture generation workflow."""
    text: str
    lecture: str
    status: Annotated[str, "The current status of the lecture, e.g., 'needs_revision', 'approved'."]
    outline: Annotated[List[dict], "A list of dictionaries representing the lecture outline."]

# Define the LangChain runnables for content generation and evaluation.
def create_lecture_runnable(state: LectureState):
    """
    LangChain Runnable to generate a lecture based on an outline and raw text.
    """
    outline = state["outline"]
    text = state["text"]
    
    final_lecture_parts = []
    
    for section in outline:
        title = section['title']
        
        prompt = PromptTemplate(
            template="""
            You are a professional content creator and public speaker. Your task is to expand the following lecture section title into detailed, engaging, and professional lecture content.
            Use the provided raw text as your primary source of information. The content should be suitable for a seminar.
            
            Lecture Section Title: {title}
            Raw Text:
            {text}
            
            Generate the content for this section below, without including the section title.
            """,
            input_variables=["title", "text"],
        )
        
        llm = ChatOllama(model="llama3", temperature=0.7)
        chain = prompt | llm
        
        content = chain.invoke({"title": title, "text": text})
        final_lecture_parts.append(f"## {title}\n\n{content.content}")
        
    final_lecture = "\n\n".join(final_lecture_parts)
    return {"lecture": final_lecture, "status": "pending_evaluation"}

def evaluate_lecture_runnable(state: LectureState):
    """
    LangChain Runnable to evaluate a lecture and decide if it's approved.
    """
    lecture = state["lecture"]
    
    prompt = PromptTemplate(
        template="""
        You are a highly critical and experienced editor. Your task is to review the following lecture content for clarity, completeness, and professionalism.
        
        If the lecture is ready for a seminar, your final response must start with the word "APPROVED".
        If it needs revision, your final response must start with the phrase "NEEDS REVISION" and include specific, actionable feedback on how to improve the lecture.
        
        Lecture Content:
        {lecture}
        
        Your response must start with 'APPROVED' or 'NEEDS REVISION'.
        """,
        input_variables=["lecture"]
    )
    
    llm = ChatOllama(model="llama3", temperature=0)
    chain = prompt | llm | StrOutputParser()
    
    decision = chain.invoke({"lecture": lecture}).strip()
    
    if "APPROVED" in decision.upper():
        return {"status": "approved"}
    else:
        return {"status": "needs_revision"}

# Define the LangGraph workflow
workflow = StateGraph(LectureState)
workflow.add_node("create_lecture", create_lecture_runnable)
workflow.add_node("evaluate_lecture", evaluate_lecture_runnable)

# Add edges
workflow.add_edge(START, "create_lecture")
workflow.add_edge("create_lecture", "evaluate_lecture")

# Define the conditional edge from the evaluator
def decide_next_step(state):
    if state["status"] == "approved":
        return END
    else:
        return "create_lecture"

workflow.add_conditional_edges(
    "evaluate_lecture",
    decide_next_step
)

lecture_app = workflow.compile()