import type { MutationRequest, MutationResponse } from "../types";

const API_BASE = "http://127.0.0.1:8000";

export async function mutateGraph(payload: MutationRequest): Promise<MutationResponse> {
  const res = await fetch(`${API_BASE}/graph/mutate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return (await res.json()) as MutationResponse;
}
