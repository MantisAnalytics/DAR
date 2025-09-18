from google.adk.agents import LlmAgent
from deepdb.config import CONFIG

report_structure_planner = LlmAgent(
    model=CONFIG.worker_model,
    name="report_structure_planner",
    description="Breaks down the research plan into a structured markdown outline of report sections.",
    instruction="""
    You are an expert report architect. Using the research topic and the plan from the 'research_plan' state key, 
    design a logical structure for the final report.

    - Ignore the tag names ([MODIFIED], [NEW], [RESEARCH], [DELIVERABLE]) when generating section titles, 
      but ensure the intent and content of each task is preserved in the outline.
    - Aim for 4-6 main sections. Adjust slightly if necessary to maintain clarity and logical flow.
    - Use markdown format with `#` for main sections and `##` for subsections or bullet points.
    - For each section, provide a brief overview of what it covers.
    - Do not include a "References" or "Sources" section in your outline.
    - Ensure the outline is clear, comprehensive, and avoids overlapping content between sections.
    """,
    output_key="report_sections",
)
