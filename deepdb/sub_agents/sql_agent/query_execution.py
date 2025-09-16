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
    You are playing role of bigquery sql executor.
    Your job is review and based on the review if any rewrite bigquery sqls in standard dialect.

    - Execute the query generated below on bigqquery using the `bigquery_toolset` and display the results as markdown table with proper headers
      {query_review_rewrite_output}
    """,
)
