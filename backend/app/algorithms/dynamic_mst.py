from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter_ns
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
        self.mst_adj: Dict[int, Set[int]] = {}
        self.last_delete_search_ms: float = 0.0
        self._next_edge_id = 0

    def _allocate_edge_id(self) -> int:
        self._next_edge_id += 1
        return self._next_edge_id

    def _add_non_tree_edge_local(self, edge_id: int) -> None:
        if edge_id not in self.edges_by_id:
            return
        u, v, _ = self.edges_by_id[edge_id]
        self.non_tree_edges.add(edge_id)
        self.lct.vertex(u).non_tree_edges.add(edge_id)
        self.lct.vertex(v).non_tree_edges.add(edge_id)

    def _remove_non_tree_edge_local(self, edge_id: int) -> None:
        if edge_id not in self.edges_by_id:
            self.non_tree_edges.discard(edge_id)
            return
        u, v, _ = self.edges_by_id[edge_id]
        self.non_tree_edges.discard(edge_id)
        self.lct.vertex(u).non_tree_edges.discard(edge_id)
        self.lct.vertex(v).non_tree_edges.discard(edge_id)

    def _add_mst_adj(self, u: int, v: int) -> None:
        self.mst_adj.setdefault(u, set()).add(v)
        self.mst_adj.setdefault(v, set()).add(u)

    def _remove_mst_adj(self, u: int, v: int) -> None:
        if u in self.mst_adj:
            self.mst_adj[u].discard(v)
        if v in self.mst_adj:
            self.mst_adj[v].discard(u)

    def _link_tree_edge(self, edge_id: int, u: int, v: int, w: int) -> None:
        edge_node = self.lct.new_edge_node(weight=w, edge_id=edge_id)
        self.edge_nodes[edge_id] = edge_node
        self.lct.link(edge_node, self.lct.vertex(u))
        self.lct.link(edge_node, self.lct.vertex(v))
        self.tree_edges.add(edge_id)
        self._add_mst_adj(u, v)
        self._remove_non_tree_edge_local(edge_id)

    def _cut_tree_edge(self, edge_id: int) -> None:
        if edge_id not in self.tree_edges:
            return
        u, v, _ = self.edges_by_id[edge_id]
        edge_node = self.edge_nodes[edge_id]
        self.lct.cut(edge_node, self.lct.vertex(u))
        self.lct.cut(edge_node, self.lct.vertex(v))
        self.tree_edges.remove(edge_id)
        self._remove_mst_adj(u, v)

    def _component_nodes(self, start: int) -> Set[int]:
        seen: Set[int] = set()
        stack = [start]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            for nei in self.mst_adj.get(x, set()):
                if nei not in seen:
                    stack.append(nei)
        return seen

    def _best_replacement_after_cut(self, u: int, v: int) -> Optional[int]:
        comp_u = self._component_nodes(u)
        comp_v = self._component_nodes(v)
        small_comp = comp_u if len(comp_u) <= len(comp_v) else comp_v
        large_root = self.lct.find_root(self.lct.vertex(v if small_comp is comp_u else u))

        best_edge: Optional[Tuple[int, int]] = None
        checked: Set[int] = set()
        for node_id in small_comp:
            for edge_id in self.lct.vertex(node_id).non_tree_edges:
                if edge_id in checked or edge_id not in self.edges_by_id:
                    continue
                checked.add(edge_id)
                a, b, w = self.edges_by_id[edge_id]
                other = b if a == node_id else a
                if self.lct.find_root(self.lct.vertex(other)) is large_root:
                    if best_edge is None or w < best_edge[1]:
                        best_edge = (edge_id, w)
        return None if best_edge is None else best_edge[0]

    def insert_edge(self, u: int, v: int, w: int) -> None:
        self.node_ids.update([u, v])
        key = normalize_edge_key(u, v)
        if key in self.edge_id_by_key:
            self.delete_edge(u, v)

        edge_id = self._allocate_edge_id()
        self.edge_id_by_key[key] = edge_id
        self.edges_by_id[edge_id] = (u, v, w)

        nu, nv = self.lct.vertex(u), self.lct.vertex(v)
        if not self.lct.connected(nu, nv):
            self._link_tree_edge(edge_id, u, v, w)
            return

        max_node = self.lct.path_max_node(nu, nv)
        if max_node is None or max_node.edge_id is None:
            self._add_non_tree_edge_local(edge_id)
            return

        if max_node.val > w:
            self._cut_tree_edge(max_node.edge_id)
            self._add_non_tree_edge_local(max_node.edge_id)
            self._link_tree_edge(edge_id, u, v, w)
        else:
            self._add_non_tree_edge_local(edge_id)

    def insert_node(self, x: int) -> None:
        self.node_ids.add(x)

    def delete_edge(self, u: int, v: int) -> None:
        self.last_delete_search_ms = 0.0
        key = normalize_edge_key(u, v)
        edge_id = self.edge_id_by_key.pop(key, None)
        if edge_id is None:
            return

        if edge_id in self.tree_edges:
            start_ns = perf_counter_ns()
            self._cut_tree_edge(edge_id)
            self.edge_nodes.pop(edge_id, None)
            replacement = self._best_replacement_after_cut(u, v)
            if replacement is not None:
                ru, rv, rw = self.edges_by_id[replacement]
                self._link_tree_edge(replacement, ru, rv, rw)
            self.last_delete_search_ms = (perf_counter_ns() - start_ns) / 1_000_000
        else:
            self._remove_non_tree_edge_local(edge_id)

        self._remove_non_tree_edge_local(edge_id)
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
