import type {
  FairnessOpinion,
  FairnessOpinionDetail,
  Valuation,
  ValuationRequest,
  ValuationSummary,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    cache: "no-store",
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ? JSON.stringify(body.detail) : detail;
    } catch {
      // response had no JSON body
    }
    throw new ApiError(res.status, detail);
  }

  return res.json() as Promise<T>;
}

export function createValuation(payload: ValuationRequest): Promise<Valuation> {
  return request<Valuation>("/api/valuations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getValuation(id: string): Promise<Valuation> {
  return request<Valuation>(`/api/valuations/${id}`);
}

export function listValuations(): Promise<ValuationSummary[]> {
  return request<ValuationSummary[]>("/api/valuations");
}

export function generateFairnessOpinion(valuationId: string): Promise<FairnessOpinion> {
  return request<FairnessOpinion>(`/api/valuations/${valuationId}/opinion`, {
    method: "POST",
  });
}

export function getFairnessOpinion(id: string): Promise<FairnessOpinionDetail> {
  return request<FairnessOpinionDetail>(`/api/opinions/${id}`);
}

export function listFairnessOpinions(): Promise<FairnessOpinion[]> {
  return request<FairnessOpinion[]>("/api/opinions");
}
