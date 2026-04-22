import { describe, it, expect, beforeEach } from "vitest";
import { draftKey, saveDraft, loadDraft, clearDraft } from "./R20DraftStore";

describe("R20DraftStore", () => {
  beforeEach(() => localStorage.clear());

  it("draftKey includes role + zblock", () => {
    const k = draftKey("GH", null, "PLN/T/OPT/G/MF/2026", null);
    expect(k).toContain("fpa-t.r20.draft.GH");
    expect(k).toContain("PLN/T/OPT/G/MF/2026");
  });

  it("draftKey includes variant when set", () => {
    const k = draftKey("COH", "TER", "PLN/T/OPT/G/MF/2026", null);
    expect(k).toContain("COH.TER");
  });

  it("save + load roundtrip", () => {
    const key = draftKey("GH", null, "z1", null);
    const recs = [{ so_row_id: "x", value: 42 } as any];
    expect(saveDraft(key, recs)).toBe(true);
    expect(loadDraft(key)).toEqual(recs);
  });

  it("load missing key → null", () => {
    expect(loadDraft("nonexistent")).toBe(null);
  });

  it("clear removes key", () => {
    const key = draftKey("GH", null, "z1", null);
    saveDraft(key, [{ so_row_id: "x" } as any]);
    clearDraft(key);
    expect(loadDraft(key)).toBe(null);
  });
});
