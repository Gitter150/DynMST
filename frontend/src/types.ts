export type MutationOperation =
  | "insert_node"
  | "insert_edge"
  | "delete_edge"
  | "update_edge_weight"
  | "delete_node";

export interface MutationRequest {
  operation: MutationOperation;
  u?: number;
  v?: number;
  w?: number;
  node?: number;
}

export interface EdgeView {
  id: number;
  u: number;
  v: number;
  w: number;
  in_mst: boolean;
}

export interface MutationResponse {
  lct_time_ms: number;
  kruskal_time_ms: number;
  deletion_search_time_ms: number;
  nodes: number[];
  edges: EdgeView[];
  mst_total_weight: number;
}
