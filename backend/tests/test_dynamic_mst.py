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


def test_local_non_tree_adjacency_sets_are_maintained():
    dmst = DynamicMST(max_nodes=10)
    dmst.insert_edge(1, 2, 1)
    dmst.insert_edge(2, 3, 1)
    dmst.insert_edge(1, 3, 5)  # non-tree
    edge_id = dmst.edge_id_by_key[(1, 3)]

    assert edge_id in dmst.lct.vertex(1).non_tree_edges
    assert edge_id in dmst.lct.vertex(3).non_tree_edges

    dmst.delete_edge(1, 3)
    assert edge_id not in dmst.lct.vertex(1).non_tree_edges
    assert edge_id not in dmst.lct.vertex(3).non_tree_edges


def test_insert_node_adds_isolated_vertex():
    dmst = DynamicMST(max_nodes=10)
    dmst.insert_node(7)
    assert 7 in dmst.node_ids
    assert dmst.all_edges() == {}
