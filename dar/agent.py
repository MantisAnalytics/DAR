from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool

from dar.sub_agents.checkers import EscalationChecker
from dar.sub_agents.research_agent.initial_research import initial_research_agent
from dar.sub_agents.research_agent.plan_creator import plan_creator
from dar.sub_agents.research_agent.report_revision import report_revision
from dar.sub_agents.research_agent.report_structure_planner import report_structure_planner
from dar.sub_agents.research_agent.research_evaluator import research_evaluator
from dar.sub_agents.sql_agent.query_understanding import query_understanding_agent
from dar.sub_agents.sql_agent.query_generation import query_generation_agent
from dar.sub_agents.sql_agent.query_review_rewrite import query_review_rewrite_agent
from dar.sub_agents.sql_agent.query_execution import query_execution_agent
from dar.config import CONFIG, before_agent_callback


sql_agent = SequentialAgent(
    name="sql_agent",
    description="An orchestrator agent that coordinates the nl2sql workflow by delegating tasks to specialized "
                "sub-agents.",
    sub_agents=[
        query_understanding_agent,
        query_generation_agent,
        LoopAgent(
            name="query_refinement_loop",
            sub_agents=[
                query_execution_agent,
                query_review_rewrite_agent,
            ],
            max_iterations=5
        )
    ],
)

report_composer = LlmAgent(
    model=CONFIG.critic_model,
    name="report_composer",
    include_contents="none",
    description="Transforms research data and a markdown outline into a final, cited report.",
    output_key="final_report",
    instruction="""
    Transform the provided data into a polished, professional, and meticulously cited research report.

    ---
    ### INPUT DATA
    *   Research Plan: `{research_plan}`
    *   Research Findings: `{section_research_findings}`
    *   Report Structure: `{report_sections}`

    ---

    ### Final Instructions
    The final report must strictly follow the structure provided in the **Report Structure** markdown outline.
    """,
)


research_pipeline = SequentialAgent(
    name="research_pipeline",
    description="Executes a pre-approved research plan. It performs iterative research, evaluation, and composes a "
                "final, cited report.",
    sub_agents=[
        sql_agent,
        report_structure_planner,
        initial_research_agent,
        LoopAgent(
            name="iterative_refinement_loop",
            max_iterations=CONFIG.max_feedback_iterations,
            sub_agents=[
                research_evaluator,
                EscalationChecker(name="escalation_checker"),
                report_revision,
            ],
        ),
        report_composer,
    ],
)

research_initiator_agent = LlmAgent(
    name="research_initiator_agent",
    model=CONFIG.worker_model,
    description="The primary research assistant. It collaborates with the user to create a research plan, and then "
                "executes it upon approval.",
    sub_agents=[research_pipeline],
    tools=[AgentTool(plan_creator)],
    output_key="research_plan",
    before_agent_callback=before_agent_callback,
    global_instruction="""
        You are an integral component of an agentic system designed for deep research and analysis of databases. 
        Your role is to assist in exploring, reasoning, and generating insights from complex database structures and data.
    """,
    instruction="""
    You are a research planning assistant. Your primary function is to convert ANY user request into a research plan.
    
    **CRITICAL RULE: Never answer a question directly or refuse a request.** Your one and only first step is to use the `plan_creator` tool to propose a research plan for the user's topic.
    If the user asks a question, you MUST immediately call `plan_creator` to create a plan to answer the question.
    
    Your workflow is:
    1.  **Plan:** Use `plan_creator` to create a draft plan and present it to the user.
    2.  **Refine:** Incorporate user feedback until the plan is approved.
    3.  **Execute:** Once the user gives EXPLICIT approval (e.g., "looks good, run it"), you MUST delegate the task to the `research_pipeline` agent, passing the approved plan.
    
    Do not perform any research yourself. Your job is to Plan, Refine, and Delegate.
    """,
)

root_agent = research_initiator_agent
