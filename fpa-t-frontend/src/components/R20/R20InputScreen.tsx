// R20 Input screen — single screen handling all 6 role variants.
// MVP: render sections from schema, edit values, validate + submit + rollback.
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import type { R20Record, R20SchemaResponse, R20ValidationError } from "../../types/R20";
import R20SectionTable from "./R20SectionTable";
import { r20Validate, r20Submit, r20Rollback } from "../../api/r20Client";
import { draftKey, saveDraft, loadDraft, clearDraft } from "../../state/R20DraftStore";

type BatchState = "DRAFT" | "SAVED_DRAFT" | "VALIDATING" | "INGESTING" | "INGESTED" | "ROLLED_BACK";

interface Props {
  role: string;
  variant: string | null;
  zblock: string;
  schema: R20SchemaResponse;
  initialRecords: R20Record[];
  onReload: () => Promise<void>;
}

export default function R20InputScreen({ role, variant, zblock, schema, initialRecords, onReload }: Props) {
  const [records, setRecords] = useState<R20Record[]>(initialRecords);
  const [state, setState] = useState<BatchState>("DRAFT");
  const [batchId, setBatchId] = useState<string | null>(null);
  const [errors, setErrors] = useState<R20ValidationError[]>([]);

  const key = useMemo(() => draftKey(role, variant, zblock, null), [role, variant, zblock]);

  // Restore draft on mount (merge with server — server wins on batch_id non-empty)
  useEffect(() => {
    if (initialRecords.length > 0) return;  // have server data
    const draft = loadDraft(key);
    if (draft) {
      setRecords(draft);
      setState("SAVED_DRAFT");
      toast.info("Draft restored from localStorage");
    }
  }, [key, initialRecords.length]);

  const scenarios = ["OPT", "REAL", "PESS"];  // MVP hides ACTUAL/DELTA

  const errorRefIds = useMemo(() => {
    const s = new Set<string>();
    for (const e of errors) for (const id of e.ref_so_row_ids) s.add(id);
    return s;
  }, [errors]);

  function onEdit(rec: R20Record, newValue: number | null) {
    setRecords((rs) => rs.map((r) => r.so_row_id === rec.so_row_id ? { ...r, value: newValue ?? 0 } : r));
    setState("DRAFT");
  }

  async function onSaveDraft() {
    const ok = saveDraft(key, records);
    if (!ok) {
      toast.error("Draft too large for localStorage (>2MB). Please submit.");
      return;
    }
    setState("SAVED_DRAFT");
    toast.success(`Draft saved locally (${records.length} rows)`);
  }

  async function onSubmit() {
    setState("VALIDATING");
    setErrors([]);
    try {
      const v = await r20Validate(role, records);
      if (!v.valid) {
        setErrors(v.errors);
        setState("DRAFT");
        toast.error(`Validation failed: ${v.errors.length} error(s)`);
        return;
      }
      setState("INGESTING");
      const ingest = await r20Submit(role, records, variant ?? undefined);
      if (ingest.status === "SKIPPED") {
        toast.info("Nothing to submit");
        setState("DRAFT");
        return;
      }
      setBatchId(ingest.batch_id);
      setState("INGESTED");
      clearDraft(key);
      toast.success(`Ingested batch ${ingest.batch_id} (${ingest.ingested_count} rows)`);
      await onReload();
    } catch (e: any) {
      const msg = e?.response?.data?.detail
        ? (typeof e.response.data.detail === "string" ? e.response.data.detail : JSON.stringify(e.response.data.detail))
        : String(e);
      toast.error("Submit failed: " + msg);
      setState("DRAFT");
    }
  }

  async function onRollback() {
    if (!batchId) return;
    if (!confirm(`Rollback batch ${batchId}?`)) return;
    try {
      const r = await r20Rollback(batchId);
      toast.success(`Rolled back ${r.deleted_count} rows`);
      setBatchId(null);
      setState("ROLLED_BACK");
      await onReload();
    } catch (e: any) {
      toast.error("Rollback failed: " + (e?.message ?? String(e)));
    }
  }

  const isBusy = state === "VALIDATING" || state === "INGESTING";

  return (
    <div>
      <div className="toolbar">
        <strong>R20 {role}{variant ? ` / ${variant}` : ""}</strong>
        <span style={{ color: "#6b7280" }}>ZBlock: {zblock}</span>
        <span style={{ marginLeft: "auto" }}>State: <b>{state}</b></span>
        {batchId && <span>Batch: <code>{batchId}</code></span>}
        <button onClick={onSaveDraft} disabled={isBusy}>Save draft</button>
        <button className="primary" onClick={onSubmit} disabled={isBusy || records.length === 0}>
          {isBusy ? "..." : "Submit"}
        </button>
        {batchId && state === "INGESTED" && (
          <button className="danger" onClick={onRollback}>Rollback</button>
        )}
      </div>

      {errors.length > 0 && (
        <div className="error-banner">
          <strong>{errors.length} validation error(s):</strong>
          <ul style={{ margin: "0.25rem 0" }}>
            {errors.map((e, i) => <li key={i}><code>{e.code}</code> — {e.message}</li>)}
          </ul>
        </div>
      )}

      {state === "INGESTED" && batchId && (
        <div className="success-banner">
          ✓ Batch <code>{batchId}</code> ingested. Use Rollback if needed.
        </div>
      )}

      {records.length === 0 && (
        <div className="section">
          <p style={{ color: "#6b7280" }}>
            No records yet. In V1.0 MVP, seed records via API or unit test fixtures.
            A per-role row builder UI is planned for V1.1.
          </p>
        </div>
      )}

      {schema.sections.map((sec) => (
        <R20SectionTable
          key={sec.id}
          section={sec}
          scenarios={scenarios}
          periodCols={schema.period_cols}
          records={records}
          errorIds={errorRefIds}
          onEdit={onEdit}
          onAddRow={() => {}}
        />
      ))}
    </div>
  );
}
