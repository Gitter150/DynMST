from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.algorithms.dynamic_mst import DynamicMST
from app.algorithms.kruskal import kruskal_mst
from app.core.benchmark import timed_call
from app.core.schemas import EdgeView, MutationRequest, MutationResponse


@dataclass
class MSTService:
    max_nodes: int = 200000
    baseline_repeat: int = 1

    def __post_init__(self) -> None:
        self.dynamic = DynamicMST(self.max_nodes)

    def apply_mutation(self, req: MutationRequest) -> MutationResponse:
        def lct_op() -> None:
            if req.operation == "insert_edge":
                assert req.u is not None and req.v is not None and req.w is not None
                self.dynamic.insert_edge(req.u, req.v, req.w)
            elif req.operation == "delete_edge":
                assert req.u is not None and req.v is not None
                self.dynamic.delete_edge(req.u, req.v)
            elif req.operation == "update_edge_weight":
                assert req.u is not None and req.v is not None and req.w is not None
                self.dynamic.update_edge_weight(req.u, req.v, req.w)
            elif req.operation == "delete_node":
                assert req.node is not None
                self.dynamic.delete_node(req.node)

        _, lct_time_ms = timed_call(lct_op)

        def kruskal_op() -> List[int]:
            return kruskal_mst(self.dynamic.node_ids, self.dynamic.all_edges())

        # For demo visibility, repeat baseline on tiny workloads.
        repeat = self.baseline_repeat
        if len(self.dynamic.all_edges()) < 200:
            repeat = max(repeat, 5)

        kruskal_ids, kruskal_time_ms = timed_call(kruskal_op, repeat=repeat)
        kruskal_set = set(kruskal_ids or [])
        dynamic_set = set(self.dynamic.tree_edges)

        edges = []
        total_w = 0
        for edge_id in sorted(self.dynamic.all_edges()):
            u, v, w = self.dynamic.edges_by_id[edge_id]
            in_mst = edge_id in dynamic_set
            if in_mst:
                total_w += w
            edges.append(EdgeView(id=edge_id, u=u, v=v, w=w, in_mst=in_mst))

        # Prevent "unused" of baseline in strict linting and keep for diagnostics.
        _ = kruskal_set

        return MutationResponse(
            lct_time_ms=lct_time_ms,
            kruskal_time_ms=kruskal_time_ms,
            nodes=sorted(self.dynamic.node_ids),
            edges=edges,
            mst_total_weight=total_w,
        )
