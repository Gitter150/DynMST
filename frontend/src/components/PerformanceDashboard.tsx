import type { MutationResponse } from "../types";

interface Props {
  data: MutationResponse | null;
}

export function PerformanceDashboard({ data }: Props) {
  return (
    <div className="panel">
      <h2>Performance Dashboard</h2>
      {!data ? (
        <p>No updates yet.</p>
      ) : (
        <div className="metrics">
          <div><strong>LCT update:</strong> {data.lct_time_ms.toFixed(4)} ms</div>
          <div><strong>Kruskal:</strong> {data.kruskal_time_ms.toFixed(4)} ms</div>
          <div><strong>Deletion search:</strong> {data.deletion_search_time_ms.toFixed(4)} ms</div>
          <div><strong>MST total weight:</strong> {data.mst_total_weight}</div>
        </div>
      )}
    </div>
  );
}
