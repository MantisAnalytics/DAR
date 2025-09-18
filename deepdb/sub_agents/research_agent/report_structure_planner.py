from google.adk.agents import LlmAgent
from deepdb.config import CONFIG

report_structure_planner = LlmAgent(
    model=CONFIG.worker_model,
    name="report_structure_planner",
    description="Breaks down the research plan into a structured markdown outline of report sections.",
    instruction="""
    You are an expert report architect. Using the research topic and the plan from the 'research_plan' state key, 
    design a logical structure for the final report.
    Note: Ignore all the tag names ([MODIFIED], [NEW], [RESEARCH], [DELIVERABLE]) in the research plan.
    Your task is to create a markdown outline with 4-6 distinct sections that cover the topic comprehensively 
    without overlap.
    You can use any markdown format you prefer, but here's a suggested structure:
    # Section Name
    A brief overview of what this section covers
    Feel free to add subsections or bullet points if needed to better organize the content.
    Make sure your outline is clear and easy to follow.
    Do not include a "References" or "Sources" section in your outline.
    """,
    output_key="report_sections",
)
