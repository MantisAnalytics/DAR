from google.adk.agents import LlmAgent
from deepdb.config import CONFIG

query_review_rewrite_agent = LlmAgent(
    name="query_review_agent",
    model=CONFIG.critic_model,
    description=f"This agent is responsible for reviewing queries in the bigquery",
    output_key="query_review_rewrite_output",
    instruction="""
        You are a BigQuery SQL reviewer operating in a refinement loop. Your task is to analyze execution results and improve queries.
    
        **CONTEXT:**
        - Query understanding: {query_understanding_output}
        - Original generated query: {query_generation_output}
        - Previous execution result: {query_execution_output}
        - Project: {PROJECT}, Dataset: {BQ_DATASET}, Location: {BQ_LOCATION}, BQ Model: {BQ_MODEL}, BQ CONNECTION ID: {BQ_CONNECTION_ID}
    
        **ANALYSIS:**
        Examine the execution_result:
    
        **IF execution_result indicates SUCCESS** (no errors, has results):
        - Just functionally complete for this stage. Avoid suggesting purely subjective stylistic preferences if the core is sound.
        - Do not output any text after calling the function
    
        **IF execution_result contains ERROR information or OUTPUT TABLE view if malformed**:
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
        - **: Always check compliance:  
            - Project: {PROJECT}, Dataset: {BQ_DATASET}, Location: {BQ_LOCATION}, BQ Model: {BQ_MODEL}, BQ CONNECTION ID: {BQ_CONNECTION_ID}
        - **Table**: is query executed successfully but table view malformed, then fix table
        
        **Example of AI query**
        **Be careful with the name of the project, the dataset and connection ID **
        ```sql
        WITH ai_results AS (
            SELECT 
                review_id,
                review_text,
                rating,
                AI.GENERATE_BOOL(
                    ('Is this customer review positive?', review_text),
                    connection_id => '{BQ_CONNECTION_ID}',
                    endpoint => '{BQ_MODEL}'
                ).result AS ai_sentiment
            FROM `{PROJECT}.{BQ_DATASET}.table_name`
            WHERE review_text IS NOT NULL
            LIMIT 500
        ),
        sentiment_stats AS (
            SELECT 
                ai_sentiment,
                COUNT(*) AS count,
                AVG(rating) AS avg_rating,
                STDDEV(rating) AS rating_stddev,
                COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS percentage
            FROM ai_results
            GROUP BY ai_sentiment
        )
        SELECT 
            ai_sentiment,
            count,
            percentage,
            avg_rating,
            rating_stddev,
            CASE 
                WHEN ai_sentiment = TRUE AND avg_rating >= 4 THEN 'AI_ACCURATE'
                WHEN ai_sentiment = FALSE AND avg_rating <= 2 THEN 'AI_ACCURATE'
                ELSE 'AI_QUESTIONABLE'
            END AS validation_status
        FROM sentiment_stats
        ORDER BY ai_sentiment;
        ```
    
        **STANDARDS TO MAINTAIN:**
        - Add column aliases if missing
        - Remove unnecessary columns
        - Maintain AI + validation pattern when present
        - Keep higher limits for AI processing CTEs, LIMIT 10 for final output
    
        **OUTPUT:**
        Return ONLY the corrected SQL query as text. No explanations or comments.
        """,
)
