from __future__ import annotations

from fastapi import APIRouter

from app.core.schemas import MutationRequest, MutationResponse
from app.core.service import MSTService

router = APIRouter(prefix="/graph", tags=["graph"])
service = MSTService()


@router.post("/mutate", response_model=MutationResponse)
def mutate_graph(req: MutationRequest) -> MutationResponse:
    return service.apply_mutation(req)
