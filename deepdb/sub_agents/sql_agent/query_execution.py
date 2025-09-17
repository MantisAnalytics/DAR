from google.adk.agents import LlmAgent
from deepdb.tools.bigquery_tools import bigquery_toolset
from deepdb.config import CONFIG


query_execution_agent = LlmAgent(
    name="query_execution_agent",
    model=CONFIG.worker_model,
    description=f"This agent is responsible for execution of queries in the bigquery and present the result as "
                f"markdown table",
    tools=[bigquery_toolset],
    output_key="query_execution_output",
    instruction="""
    Execute the current SQL query using BigQuery tools.

    Original Query:
    {query_generation_output}

    Current Query:
    {query_review_rewrite_output?}

    Project: {PROJECT}, Dataset: {BQ_DATASET}, Location: {BQ_LOCATION}

    After execution:

    **IF SUCCESSFUL** (query returns results without errors):
    - Display the results of query execution.
    - Ensure the content strictly matches the query output (no fabricated or altered values).
    - Do not include any additional text, commentary, or explanations outside the query execution results.
    
    **IF FAILED** (query has errors, syntax issues, or execution problems):
    - Output the specific error details for the review agent
    - Include error type, line numbers, and problematic parts
    - Do not call any functions

    The loop will automatically handle failed executions by triggering query refinement.
    """,
)
