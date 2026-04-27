from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


MutationType = Literal[
    "insert_edge",
    "delete_edge",
    "update_edge_weight",
    "delete_node",
]


class MutationRequest(BaseModel):
    operation: MutationType
    u: Optional[int] = None
    v: Optional[int] = None
    w: Optional[int] = None
    node: Optional[int] = None


class EdgeView(BaseModel):
    id: int
    u: int
    v: int
    w: int
    in_mst: bool = Field(default=False)


class MutationResponse(BaseModel):
    lct_time_ms: float
    kruskal_time_ms: float
    nodes: List[int]
    edges: List[EdgeView]
    mst_total_weight: int
