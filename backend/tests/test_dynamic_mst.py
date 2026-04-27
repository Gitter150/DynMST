from app.algorithms.dynamic_mst import DynamicMST


def test_cycle_replacement_uses_lighter_edge():
    dmst = DynamicMST(max_nodes=10)
    dmst.insert_edge(1, 2, 4)
    dmst.insert_edge(2, 3, 5)
    dmst.insert_edge(1, 3, 2)  # should replace edge (2,3,5)

    weights = sorted(dmst.edges_by_id[e][2] for e in dmst.tree_edges)
    assert weights == [2, 4]


def test_delete_tree_edge_finds_replacement():
    dmst = DynamicMST(max_nodes=10)
    dmst.insert_edge(1, 2, 1)
    dmst.insert_edge(2, 3, 2)
    dmst.insert_edge(1, 3, 3)  # non-tree
    dmst.delete_edge(2, 3)

    assert len(dmst.tree_edges) == 2
    weights = sorted(dmst.edges_by_id[e][2] for e in dmst.tree_edges)
    assert weights == [1, 3]
