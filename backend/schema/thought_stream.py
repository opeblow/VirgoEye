from typing import List

from pydantic import BaseModel, Field


class ThoughtChunk(BaseModel):
    """A single chunk of the deliberation stream"""

    chunk_id: int
    text: str
    referenced_entities: List[str] = Field(
        default_factory=list, description="Entity IDs referenced"
    )
    reasoning_type: str = Field(
        ..., description="spatial|relational|causal|comparative"
    )


class ThoughtChain(BaseModel):
    """Complete Stage 2 thought chain"""

    chunks: List[ThoughtChunk]
    total_tokens: int
    reasoning_depth: int = Field(..., description="Number of reasoning steps")
    entities_analyzed: List[str]
    entities_skipped: List[str]
