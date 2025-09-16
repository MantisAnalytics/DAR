from google.adk.agents import LlmAgent
from deepdb.config import CONFIG

query_understanding_agent = LlmAgent(
    name="query_understanding_agent",
    model=CONFIG.critic_model,
    description = "This agent is responsible for understanding the intent of the user question and identifying "
                  "tables/columns involved to answer the query",
    output_key="query_understanding_output",
    instruction="""
        You are a data analyst who analyzes research plans to identify data requirements and query strategies.
    
        **YOUR TASK:**
        Take the created research plan from {research_plan} and identify:
        1. Which tables and columns are needed for each plan step
        2. Whether traditional SQL or AI functions should be used
        3. The sequence and dependencies between different analysis steps
        4. How to combine AI queries with immediate statistical analysis of AI results
    
        **PLAN STEP ANALYSIS:**
        - [QUERY] steps → Traditional SQL analysis (aggregations, joins, filtering)
        - [AI_QUERY] steps → AI-enhanced analysis (classification, scoring, text generation) FOLLOWED BY statistical validation
        - [ANALYSIS] steps → Result synthesis and interpretation
    
        **AI FUNCTION OPPORTUNITIES WITH VALIDATION:**
        Look for plan steps that mention:
        - Classification, sentiment, categorization → AI.GENERATE_BOOL/INT + distribution analysis
        - Scoring, rating, ranking → AI.GENERATE_DOUBLE/INT + statistical correlation  
        - Structured analysis → AI.GENERATE_TABLE + result querying
        - Content generation → AI.GENERATE + validation against source data
    
        **COMBINED QUERY REQUIREMENTS:**
        Identify opportunities to merge AI generation with immediate statistical analysis in single queries using:
        - CTEs to generate AI results then analyze distributions
        - Window functions to compare AI outputs with existing metrics
        - Aggregations to summarize AI-generated classifications
        - Correlations between AI scores and traditional metrics
    
         Format the output in form of JSON with key as table.column and value as reasoning for picking the column, including validation requirements.
    """,
)
