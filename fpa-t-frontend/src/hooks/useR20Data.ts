// Async init (ISP S11) — parallel fetch schema + records
import { useEffect, useState } from "react";
import type { R20Record, R20SchemaResponse } from "../types/R20";
import { r20GetSchema, r20LoadRecords } from "../api/r20Client";

export interface R20DataState {
  loading: boolean;
  error: string | null;
  schema: R20SchemaResponse | null;
  records: R20Record[];
}

export function useR20Data(
  role: string,
  zblock: string | null,
  variant: string | null,
  ff: string,
): R20DataState & { reload: () => Promise<void> } {
  const [state, setState] = useState<R20DataState>({
    loading: false,
    error: null,
    schema: null,
    records: [],
  });

  async function load() {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const [schema, records] = await Promise.all([
        r20GetSchema(role, ff),
        zblock ? r20LoadRecords(role, zblock, variant ?? undefined) : Promise.resolve([]),
      ]);
      setState({ loading: false, error: null, schema, records });
    } catch (e) {
      const err = e instanceof Error ? e.message : String(e);
      setState((s) => ({ ...s, loading: false, error: err }));
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role, zblock, variant, ff]);

  return { ...state, reload: load };
}
