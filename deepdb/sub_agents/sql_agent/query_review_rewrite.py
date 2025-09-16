from google.adk.agents import LlmAgent
from deepdb.config import CONFIG

# LLM Agent for review of the SQL queries and rewriting the sql queries if needed
query_review_rewrite_agent = LlmAgent(
    name="query_review_agent",
    model=CONFIG.critic_model,
    description=f"This agent is responsible for reviewing queries in the bigquery",
    output_key="query_review_rewrite_output",
    instruction="""
    You are a BigQuery SQL reviewer. Review and rewrite SQL queries to fix common issues.

    **INPUT:**
    - Query understanding: {query_understanding_output}
    - Generated query: {query_generation_output}
    - Project: {PROJECT}, Dataset: {BQ_DATASET}, Location: {BQ_LOCATION}
    - Use `bigquery_toolset` for table metadata

    **REVIEW CHECKLIST:**
    - Add column aliases if missing
    - Add LIMIT 10 for final SELECT (keep higher limits for AI processing CTEs)
    - Remove unnecessary columns
    - Fix string matching: UPPER(column) = "VALUE" or LOWER(column) = "value"  
    - Convert datetime to string: FORMAT_DATETIME('%Y-%m-%d', date_column)
    - Add NULL checks for AI function inputs
    - Maintain AI + validation pattern (AI results must be analyzed statistically)
    - Always use 'gemini-2.0-flash' in AI functions

    **OUTPUT:**
    Return only the corrected SQL query as text.
    Only return queries, don't run this queries.
    """,

)
