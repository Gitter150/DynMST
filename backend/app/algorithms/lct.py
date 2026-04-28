from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Set


NEG_INF = -10**18


@dataclass
class LCTNode:
    node_id: int
    val: int = NEG_INF
    edge_id: Optional[int] = None
    left: Optional["LCTNode"] = None
    right: Optional["LCTNode"] = None
    parent: Optional["LCTNode"] = None
    rev: bool = False
    max_val: int = NEG_INF
    max_node: Optional["LCTNode"] = None
    non_tree_edges: Set[int] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.max_val = self.val
        self.max_node = self

    def is_splay_root(self) -> bool:
        return self.parent is None or (
            self.parent.left is not self and self.parent.right is not self
        )


def _max_pair(a_val: int, a_node: Optional[LCTNode], b_val: int, b_node: Optional[LCTNode]):
    if a_val >= b_val:
        return a_val, a_node
    return b_val, b_node


class LinkCutTree:
    """
    LCT variant modeled after USACO 'Link Cut Tree - Paths'.
    We store vertices and edge-nodes; only edge-nodes have finite val.
    """

    def __init__(self, max_nodes: int) -> None:
        self._next_id = max_nodes
        self.vertices = [LCTNode(i) for i in range(max_nodes + 1)]

    def _push_up(self, x: LCTNode) -> None:
        best_val = x.val
        best_node: Optional[LCTNode] = x
        if x.left:
            best_val, best_node = _max_pair(best_val, best_node, x.left.max_val, x.left.max_node)
        if x.right:
            best_val, best_node = _max_pair(best_val, best_node, x.right.max_val, x.right.max_node)
        x.max_val = best_val
        x.max_node = best_node

    def _push_down(self, x: LCTNode) -> None:
        if not x.rev:
            return
        x.left, x.right = x.right, x.left
        if x.left:
            x.left.rev ^= True
        if x.right:
            x.right.rev ^= True
        x.rev = False

    def _rotate(self, x: LCTNode) -> None:
        p = x.parent
        g = p.parent if p else None
        if p is None:
            return
        if not p.is_splay_root() and g is not None:
            if g.left is p:
                g.left = x
            else:
                g.right = x
        x.parent = g

        if p.left is x:
            p.left = x.right
            if x.right:
                x.right.parent = p
            x.right = p
        else:
            p.right = x.left
            if x.left:
                x.left.parent = p
            x.left = p
        p.parent = x

        self._push_up(p)
        self._push_up(x)

    def _splay(self, x: LCTNode) -> None:
        stack = []
        cur: Optional[LCTNode] = x
        while cur is not None:
            stack.append(cur)
            if cur.is_splay_root():
                break
            cur = cur.parent
        while stack:
            self._push_down(stack.pop())

        while not x.is_splay_root():
            p = x.parent
            g = p.parent if p else None
            if p is None:
                break
            if not p.is_splay_root() and g is not None:
                if (g.left is p) == (p.left is x):
                    self._rotate(p)
                else:
                    self._rotate(x)
            self._rotate(x)

    def access(self, x: LCTNode) -> None:
        last: Optional[LCTNode] = None
        cur: Optional[LCTNode] = x
        while cur is not None:
            self._splay(cur)
            cur.right = last
            self._push_up(cur)
            last = cur
            cur = cur.parent
        self._splay(x)

    def make_root(self, x: LCTNode) -> None:
        self.access(x)
        x.rev ^= True
        self._push_down(x)

    def find_root(self, x: LCTNode) -> LCTNode:
        self.access(x)
        cur = x
        self._push_down(cur)
        while cur.left is not None:
            cur = cur.left
            self._push_down(cur)
        self._splay(cur)
        return cur

    def connected(self, u: LCTNode, v: LCTNode) -> bool:
        if u is v:
            return True
        return self.find_root(u) is self.find_root(v)

    def link(self, u: LCTNode, v: LCTNode) -> None:
        self.make_root(u)
        if self.find_root(v) is not u:
            u.parent = v

    def cut(self, u: LCTNode, v: LCTNode) -> None:
        self.make_root(u)
        self.access(v)
        if v.left is u and u.right is None and u.left is None:
            v.left.parent = None
            v.left = None
            self._push_up(v)

    def split(self, u: LCTNode, v: LCTNode) -> None:
        self.make_root(u)
        self.access(v)

    def path_max_node(self, u: LCTNode, v: LCTNode) -> Optional[LCTNode]:
        self.split(u, v)
        return v.max_node

    def new_edge_node(self, weight: int, edge_id: int) -> LCTNode:
        self._next_id += 1
        return LCTNode(node_id=self._next_id, val=weight, edge_id=edge_id)

    def vertex(self, idx: int) -> LCTNode:
        return self.vertices[idx]
