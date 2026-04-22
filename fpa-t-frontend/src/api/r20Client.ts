// R20 API client (ISP S9)
// NaN sanitizer on receive; snake_case payloads already match Pydantic.

import axios from "axios";
import type {
  R20Record, R20SchemaResponse, R20ValidationResult, R20IngestResponse,
} from "../types/R20";

const api = axios.create({ baseURL: "" });

function sanitizeValue(v: unknown): number | null {
  if (typeof v !== "number") return null;
  if (Number.isNaN(v) || !Number.isFinite(v)) return null;
  return v;
}

function sanitizeRecord(r: R20Record): R20Record {
  return { ...r, value: sanitizeValue(r.value) ?? 0 };
}

export async function r20GetSchema(role: string, ff = "MF"): Promise<R20SchemaResponse> {
  const r = await api.get(`/api/fpa-t/r20/schema/${role}`, { params: { ff } });
  return r.data;
}

export async function r20LoadRecords(
  role: string,
  zblock_string: string,
  variant?: string,
  scenario?: string,
): Promise<R20Record[]> {
  const r = await api.get(`/api/fpa-t/r20/${role}/load`, {
    params: { zblock_string, variant, scenario },
  });
  return (r.data as R20Record[]).map(sanitizeRecord);
}

export async function r20Validate(role: string, records: R20Record[]): Promise<R20ValidationResult> {
  const r = await api.post(`/api/fpa-t/r20/${role}/validate`, records);
  return r.data;
}

export async function r20Submit(
  role: string,
  records: R20Record[],
  variant?: string,
): Promise<R20IngestResponse> {
  const r = await api.post(`/api/fpa-t/r20/${role}/submit`, records, {
    params: variant ? { variant } : {},
  });
  return r.data;
}

export async function r20Rollback(batch_id: string): Promise<{ deleted_count: number }> {
  const r = await api.post(`/api/fpa-t/r20/rollback/${batch_id}`);
  return r.data;
}

export async function r20GetBatch(batch_id: string) {
  const r = await api.get(`/api/fpa-t/r20/batch/${batch_id}`);
  return r.data;
}
