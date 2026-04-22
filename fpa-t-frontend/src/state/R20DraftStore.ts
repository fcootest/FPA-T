// LocalStorage draft (ISP S10 enriched)
import type { R20Record } from "../types/R20";

const DRAFT_NS = "fpa-t.r20.draft";
const MAX_DRAFT_BYTES = 2 * 1024 * 1024;

export function draftKey(
  role: string,
  variant: string | null | undefined,
  zblock: string,
  run: string | null | undefined,
): string {
  return `${DRAFT_NS}.${role}${variant ? `.${variant}` : ""}.${zblock}.${run || ""}`;
}

export function saveDraft(key: string, records: R20Record[]): boolean {
  const json = JSON.stringify(records);
  if (json.length > MAX_DRAFT_BYTES) return false;
  try {
    localStorage.setItem(key, json);
    return true;
  } catch {
    return false;
  }
}

export function loadDraft(key: string): R20Record[] | null {
  try {
    const s = localStorage.getItem(key);
    return s ? (JSON.parse(s) as R20Record[]) : null;
  } catch {
    return null;
  }
}

export function clearDraft(key: string): void {
  localStorage.removeItem(key);
}
