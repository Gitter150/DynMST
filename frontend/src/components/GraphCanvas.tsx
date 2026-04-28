import { useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  type Edge,
  type Node,
  type OnNodesChange,
  type OnEdgesChange,
} from "reactflow";
import "reactflow/dist/style.css";
import type { MutationResponse } from "../types";

interface Props {
  data: MutationResponse | null;
  nodes: Node[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
}

export function GraphCanvas({ data, nodes, onNodesChange, onEdgesChange }: Props) {
  const edges: Edge[] = useMemo(() => {
    if (!data) return [];
    return data.edges.map((e) => ({
      id: String(e.id),
      source: String(e.u),
      target: String(e.v),
      label: String(e.w),
      style: {
        stroke: e.in_mst ? "#1f6feb" : "#6b7280",
        strokeWidth: e.in_mst ? 3 : 1.5,
      },
    }));
  }, [data]);

  return (
    <div className="canvas">
      <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
