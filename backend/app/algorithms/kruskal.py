from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass
class DSU:
    parent: List[int]
    rank: List[int]

    @classmethod
    def with_size(cls, n: int) -> "DSU":
        return cls(parent=list(range(n + 1)), rank=[0] * (n + 1))

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal_mst(
    node_ids: Iterable[int],
    edges: Dict[int, Tuple[int, int, int]],
) -> List[int]:
    nodes = sorted(node_ids)
    if not nodes:
        return []
    max_node = max(nodes)
    dsu = DSU.with_size(max_node)

    sorted_edges = sorted(edges.items(), key=lambda item: item[1][2])
    mst_edge_ids: List[int] = []
    for edge_id, (u, v, _w) in sorted_edges:
        if dsu.union(u, v):
            mst_edge_ids.append(edge_id)
    return mst_edge_ids
