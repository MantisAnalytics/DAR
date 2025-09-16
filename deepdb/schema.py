from typing import Literal
from pydantic import BaseModel, Field

class BigQueryAnalysis(BaseModel):
    """Model representing a specific BigQuery analysis task."""

    analysis_description: str = Field(
        description="A clear description of what data analysis needs to be performed."
    )
    target_tables: list[str] = Field(
        description="List of specific tables to analyze (user-provided)."
    )
    max_rows_per_query: int = Field(
        default=1000,
        description="Maximum number of rows to analyze per query to control BigQuery costs."
    )


class ResearchCorrection(BaseModel):
    """Model for specifying required corrections to research findings."""

    section_identifier: str = Field(
        description="The specific section, paragraph, or statement identifier where the issue was found"
    )
    problematic_content: str = Field(
        description="The exact text or claim that appears hallucinated or questionable"
    )
    issue_type: Literal[
        "hallucination", "unsupported_claim", "contradictory_info", "overgeneralization", "missing_context"] = Field(
        description="The type of factual accuracy issue identified"
    )
    correction_instruction: str = Field(
        description="Specific instruction on how to correct or verify this content"
    )


class Feedback(BaseModel):
    """Model for providing evaluation feedback on research quality and factual accuracy."""

    grade: Literal["pass", "fail"] = Field(
        description="Evaluation result. 'pass' if the research is factually accurate and well-sourced, 'fail' if it contains hallucinations or questionable claims."
    )
    comment: str = Field(
        description="Detailed explanation identifying specific hallucinations, unsupported claims, or questionable statements that need revision."
    )
    corrections_needed: list[ResearchCorrection] | None = Field(
        default=None,
        description="A list of specific corrections needed to fix hallucinated or questionable content. This should be null or empty if the grade is 'pass'.",
    )
