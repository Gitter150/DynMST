import { useMemo, useState } from "react";
import { applyNodeChanges, type Node, type EdgeChange, type NodeChange } from "reactflow";
import { mutateGraph } from "./services/api";
import type { MutationOperation, MutationResponse } from "./types";
import { GraphCanvas } from "./components/GraphCanvas";
import { PerformanceDashboard } from "./components/PerformanceDashboard";

const OPS: MutationOperation[] = ["insert_node", "insert_edge", "delete_edge", "update_edge_weight", "delete_node"];

function makeNodes(data: MutationResponse | null, oldNodes: Node[]): Node[] {
  if (!data) return oldNodes;
  const existing = new Map(oldNodes.map((n) => [Number(n.id), n]));
  return data.nodes.map((id, idx) => {
    const prev = existing.get(id);
    return {
      id: String(id),
      position: prev?.position ?? { x: 120 + (idx % 6) * 120, y: 80 + Math.floor(idx / 6) * 100 },
      data: { label: `Node ${id}` },
    };
  });
}

export default function App() {
  const [operation, setOperation] = useState<MutationOperation>("insert_edge");
  const [u, setU] = useState("1");
  const [v, setV] = useState("2");
  const [w, setW] = useState("5");
  const [node, setNode] = useState("1");
  const [result, setResult] = useState<MutationResponse | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [error, setError] = useState<string>("");

  const onNodesChange = (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds));
  const onEdgesChange = (_changes: EdgeChange[]) => {};

  const canUseEdgeFields = operation !== "delete_node" && operation !== "insert_node";
  const canUseWeight = operation === "insert_edge" || operation === "update_edge_weight";

  const statusText = useMemo(() => {
    if (!result) return "Ready";
    return `Nodes: ${result.nodes.length}, Edges: ${result.edges.length}`;
  }, [result]);

  async function submitMutation() {
    setError("");
    try {
      const payload =
        operation === "delete_node" || operation === "insert_node"
          ? { operation, node: Number(node) }
          : {
              operation,
              u: Number(u),
              v: Number(v),
              ...(canUseWeight ? { w: Number(w) } : {}),
            };
      const data = await mutateGraph(payload);
      setResult(data);
      setNodes((old) => makeNodes(data, old));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    }
  }

  return (
    <div className="app">
      <h1>Dynamic MST Visualizer</h1>
      <p className="status">{statusText}</p>
      <div className="layout">
        <div className="left">
          <div className="panel">
            <h2>Mutation Controls</h2>
            <label>
              Operation
              <select value={operation} onChange={(e) => setOperation(e.target.value as MutationOperation)}>
                {OPS.map((op) => (
                  <option key={op} value={op}>
                    {op}
                  </option>
                ))}
              </select>
            </label>
            {canUseEdgeFields && (
              <>
                <label>
                  u
                  <input value={u} onChange={(e) => setU(e.target.value)} />
                </label>
                <label>
                  v
                  <input value={v} onChange={(e) => setV(e.target.value)} />
                </label>
              </>
            )}
            {canUseWeight && (
              <label>
                w
                <input value={w} onChange={(e) => setW(e.target.value)} />
              </label>
            )}
            {!canUseEdgeFields && (
              <label>
                node
                <input value={node} onChange={(e) => setNode(e.target.value)} />
              </label>
            )}
            <button onClick={submitMutation}>Apply Mutation</button>
            {error && <p className="error">{error}</p>}
          </div>
          <PerformanceDashboard data={result} />
        </div>
        <GraphCanvas data={result} nodes={nodes} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} />
      </div>
    </div>
  );
}
