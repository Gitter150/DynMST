from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from app.algorithms.lct import LCTNode, LinkCutTree


def normalize_edge_key(u: int, v: int) -> Tuple[int, int]:
    return (u, v) if u < v else (v, u)


@dataclass
class DynamicMST:
    max_nodes: int

    def __post_init__(self) -> None:
        self.lct = LinkCutTree(self.max_nodes)
        self.node_ids: Set[int] = set()
        self.edges_by_id: Dict[int, Tuple[int, int, int]] = {}
        self.edge_id_by_key: Dict[Tuple[int, int], int] = {}
        self.edge_nodes: Dict[int, LCTNode] = {}
        self.tree_edges: Set[int] = set()
        self.non_tree_edges: Set[int] = set()
        self._next_edge_id = 0

    def _allocate_edge_id(self) -> int:
        self._next_edge_id += 1
        return self._next_edge_id

    def _link_tree_edge(self, edge_id: int, u: int, v: int, w: int) -> None:
        edge_node = self.lct.new_edge_node(weight=w, edge_id=edge_id)
        self.edge_nodes[edge_id] = edge_node
        self.lct.link(edge_node, self.lct.vertex(u))
        self.lct.link(edge_node, self.lct.vertex(v))
        self.tree_edges.add(edge_id)
        self.non_tree_edges.discard(edge_id)

    def _cut_tree_edge(self, edge_id: int) -> None:
        if edge_id not in self.tree_edges:
            return
        u, v, _ = self.edges_by_id[edge_id]
        edge_node = self.edge_nodes[edge_id]
        self.lct.cut(edge_node, self.lct.vertex(u))
        self.lct.cut(edge_node, self.lct.vertex(v))
        self.tree_edges.remove(edge_id)

    def _best_replacement_for_components(self) -> Optional[int]:
        best: Optional[Tuple[int, int]] = None
        for edge_id in self.non_tree_edges:
            u, v, w = self.edges_by_id[edge_id]
            if not self.lct.connected(self.lct.vertex(u), self.lct.vertex(v)):
                if best is None or w < best[1]:
                    best = (edge_id, w)
        return None if best is None else best[0]

    def insert_edge(self, u: int, v: int, w: int) -> None:
        self.node_ids.update([u, v])
        key = normalize_edge_key(u, v)
        if key in self.edge_id_by_key:
            old_id = self.edge_id_by_key[key]
            self.delete_edge(u, v)
            self.edges_by_id.pop(old_id, None)
            self.edge_nodes.pop(old_id, None)

        edge_id = self._allocate_edge_id()
        self.edge_id_by_key[key] = edge_id
        self.edges_by_id[edge_id] = (u, v, w)

        nu, nv = self.lct.vertex(u), self.lct.vertex(v)
        if not self.lct.connected(nu, nv):
            self._link_tree_edge(edge_id, u, v, w)
            return

        max_node = self.lct.path_max_node(nu, nv)
        if max_node is None or max_node.edge_id is None:
            self.non_tree_edges.add(edge_id)
            return

        if max_node.val > w:
            self._cut_tree_edge(max_node.edge_id)
            self.non_tree_edges.add(max_node.edge_id)
            self._link_tree_edge(edge_id, u, v, w)
        else:
            self.non_tree_edges.add(edge_id)

    def delete_edge(self, u: int, v: int) -> None:
        key = normalize_edge_key(u, v)
        edge_id = self.edge_id_by_key.pop(key, None)
        if edge_id is None:
            return

        if edge_id in self.tree_edges:
            self._cut_tree_edge(edge_id)
            self.edge_nodes.pop(edge_id, None)
            replacement = self._best_replacement_for_components()
            if replacement is not None:
                ru, rv, rw = self.edges_by_id[replacement]
                self._link_tree_edge(replacement, ru, rv, rw)
        else:
            self.non_tree_edges.discard(edge_id)

        self.edges_by_id.pop(edge_id, None)
        self.edge_nodes.pop(edge_id, None)

    def update_edge_weight(self, u: int, v: int, new_w: int) -> None:
        self.delete_edge(u, v)
        self.insert_edge(u, v, new_w)

    def delete_node(self, x: int) -> None:
        if x not in self.node_ids:
            return
        incident: List[Tuple[int, int]] = []
        for edge_id, (u, v, _w) in list(self.edges_by_id.items()):
            if u == x or v == x:
                incident.append((u, v))
        for u, v in incident:
            self.delete_edge(u, v)
        self.node_ids.discard(x)

    def mst_edges(self) -> List[Tuple[int, int, int, int]]:
        out = []
        for edge_id in sorted(self.tree_edges):
            u, v, w = self.edges_by_id[edge_id]
            out.append((edge_id, u, v, w))
        return out

    def all_edges(self) -> Dict[int, Tuple[int, int, int]]:
        return dict(self.edges_by_id)
