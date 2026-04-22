// TS types mirroring Pydantic R20RecordModel (AP S1.3, DD-R20-09/10)

export type R20Role = "GH" | "HQ" | "TECH" | "COH" | "CEH" | "DH";
export type Scenario = "OPT" | "REAL" | "PESS";
export type IO = "I" | "O";

export interface R20Record {
  input_id: string | null;
  so_row_id: string;
  session_id: string | null;
  plan_type: string | null;
  zblock_string: string | null;
  io: IO;
  kr_type: string | null;
  kr1: string | null; kr2: string | null; kr3: string | null; kr4: string | null;
  kr5: string | null; kr6: string | null; kr7: string | null; kr8: string | null;
  kr_code: string | null; kr_name: string | null;
  cdt1: string | null; cdt2: string | null; cdt3: string | null; cdt4: string | null;
  pt1: string | null; pt2: string | null; du: string | null;
  pt1_prev: string | null; pt2_prev: string | null; du_prev: string | null;
  own_type: string | null;
  fu1_code: string | null; fu2_code: string | null;
  egt1: string | null; egt2: string | null; egt3: string | null; egt4: string | null; egt5: string | null;
  hr1: string | null; hr2: string | null; hr3: string | null;
  sec: string | null; le1: string | null; le2: string | null;
  period: string;
  value: number | null;  // NaN sanitized to null on receive
  scenario: Scenario;
  role_source: string;
  ppr_file_id: string;
  track_variant: string;
  alloc_znumber: string | null;
  forecast_frequency: string | null;
  noem_grade: string | null;
  upload_batch_id: string;
  created_by: string;
  created_at: string;
}

export interface R20Section {
  id: string;
  title: string;
  row_type: IO;
  kr_codes: string[];
  breakdown: string[];
  unit: "bVND" | "mVND" | "%" | "person" | "USD";
}

export interface R20SchemaResponse {
  role: string;
  metadata_fields: string[];
  scenario_blocks: string[];
  sections: R20Section[];
  kr_list: string[];
  period_cols: string[];
}

export interface R20ValidationError {
  code: string;
  message: string;
  ref_so_row_ids: string[];
}

export interface R20ValidationResult {
  valid: boolean;
  errors: R20ValidationError[];
}

export interface R20IngestResponse {
  batch_id: string | null;
  ingested_count: number;
  status: "INGESTED" | "FAILED" | "SKIPPED";
}
