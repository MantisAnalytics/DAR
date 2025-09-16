from google.adk.agents import LlmAgent
from deepdb.config import CONFIG

# LLM Agent for review of the SQL queries and rewriting the sql queries if needed
query_review_rewrite_agent = LlmAgent(
    name="query_review_agent",
    model=CONFIG.critic_model,
    description=f"This agent is responsible for reviewing queries in the bigquery",
    output_key="query_review_rewrite_output",
    # instruction="""
    # You are a BigQuery SQL reviewer. Review and rewrite SQL queries to fix common issues.
    #
    # **INPUT:**
    # - Query understanding: {query_understanding_output}
    # - Generated query: {query_generation_output}
    # - Project: {PROJECT}, Dataset: {BQ_DATASET}, Location: {BQ_LOCATION}, BQ Model {BQ_MODEL}
    # - Use `bigquery_toolset` for table metadata
    #
    # **REVIEW CHECKLIST:**
    # - Add column aliases if missing
    # - Add LIMIT 10 for final SELECT (keep higher limits for AI processing CTEs)
    # - Remove unnecessary columns
    # - Fix string matching: UPPER(column) = "VALUE" or LOWER(column) = "value"
    # - Convert datetime to string: FORMAT_DATETIME('%Y-%m-%d', date_column)
    # - Add NULL checks for AI function inputs
    # - Maintain AI + validation pattern (AI results must be analyzed statistically)
    #
    # **OUTPUT:**
    # Return only the corrected SQL query as text.
    # Only return queries, don't run this queries.
    # """,
instruction="""
    You are a BigQuery SQL reviewer operating in a refinement loop. Your task is to analyze execution results and improve queries.

    **CONTEXT:**
    - Query understanding: {query_understanding_output}
    - Original generated query: {query_generation_output}
    - Previous execution result: {query_execution_output}
    - Project: {PROJECT}, Dataset: {BQ_DATASET}, Location: {BQ_LOCATION}, BQ Model: {BQ_MODEL}

    **ANALYSIS:**
    Examine the execution_result:

    **IF execution_result indicates SUCCESS** (no errors, has results):
    - Just functionally complete for this stage. Avoid suggesting purely subjective stylistic preferences if the core is sound.
    - Do not output any text after calling the function

    **IF execution_result contains ERROR information**:
    - Analyze the specific error details
    - Apply appropriate fixes based on error type:

    **COMMON FIXES:**
    - **Syntax Errors**: Fix SQL syntax, missing commas, parentheses
    - **Table/Column Not Found**: Use bigquery_toolset to verify correct names
    - **Type Mismatches**: Add proper CAST() or SAFE_CAST() functions
    - **String Matching**: Use UPPER(column) = "VALUE" or LOWER(column) = "value"
    - **Datetime Issues**: Use FORMAT_DATETIME('%Y-%m-%d', date_column)
    - **Aggregation Errors**: Add missing GROUP BY clauses
    - **NULL Handling**: Add NULL checks for AI function inputs
    - **Limit Issues**: Add LIMIT 10 for final SELECT statements

    **STANDARDS TO MAINTAIN:**
    - Add column aliases if missing
    - Remove unnecessary columns
    - Maintain AI + validation pattern when present
    - Keep higher limits for AI processing CTEs, LIMIT 10 for final output

    **OUTPUT:**
    Return ONLY the corrected SQL query as text. No explanations or comments.
    """,

)
