// Shared section table used by all role sections.
// Renders: metadata cols (kr, breakdown fields) + 1 col per period per scenario.
import { useMemo } from "react";
import type { R20Record, R20Section } from "../../types/R20";
import { formatValue } from "./R20Formatters";

interface Props {
  section: R20Section;
  scenarios: string[];  // ["OPT","REAL","PESS"] (ACTUAL+DELTA hidden for MVP)
  periodCols: string[];
  records: R20Record[];
  errorIds: Set<string>;
  onEdit: (rec: R20Record, newValue: number | null) => void;
  onAddRow: (section: R20Section, keys: Record<string, string>) => void;
}

// Row key = section-kr_code-breakdown_values
function breakdownKey(r: R20Record, breakdown: string[]): string {
  return breakdown.map((b) => (r as any)[b] ?? "").join("|");
}

export default function R20SectionTable({
  section, scenarios, periodCols, records, errorIds, onEdit,
}: Props) {
  // Filter records matching this section by kr_code
  const sectionRecords = useMemo(
    () => records.filter((r) => r.kr_code && section.kr_codes.includes(r.kr_code)),
    [records, section.kr_codes],
  );

  // Group by (kr_code, breakdown). Each group = 1 row.
  const rowGroups = useMemo(() => {
    const map = new Map<string, { kr_code: string; breakdown: Record<string, string>; byKey: Record<string, R20Record> }>();
    for (const r of sectionRecords) {
      const bkey = breakdownKey(r, section.breakdown);
      const rowId = `${r.kr_code}|${bkey}`;
      if (!map.has(rowId)) {
        const bd: Record<string, string> = {};
        for (const b of section.breakdown) bd[b] = (r as any)[b] ?? "";
        map.set(rowId, { kr_code: r.kr_code!, breakdown: bd, byKey: {} });
      }
      const cellKey = `${r.scenario}__${r.period}`;
      map.get(rowId)!.byKey[cellKey] = r;
    }
    return Array.from(map.values());
  }, [sectionRecords, section.breakdown]);

  return (
    <div className="section">
      <h3>{section.title} <span className={`badge ${section.row_type === "I" ? "in" : "out"}`}>{section.row_type}</span> <small>({section.unit})</small></h3>
      {rowGroups.length === 0 ? (
        <p style={{ color: "#6b7280", fontStyle: "italic" }}>No data. Edit mode: add rows via row_type=I sections in wave 6 enhancement.</p>
      ) : (
        <div style={{ overflow: "auto", maxHeight: 400 }}>
          <table className="r20-grid">
            <thead>
              <tr>
                <th>KR</th>
                {section.breakdown.map((b) => <th key={b}>{b.toUpperCase()}</th>)}
                {scenarios.map((sc) =>
                  periodCols.map((p) => <th key={`${sc}_${p}`}>{sc}<br/>{p}</th>)
                )}
              </tr>
            </thead>
            <tbody>
              {rowGroups.map((row, idx) => {
                const rowHasError = Object.values(row.byKey).some((rec) => errorIds.has(rec.so_row_id));
                return (
                  <tr key={idx} className={rowHasError ? "r20-row-error" : ""}>
                    <td className="meta" title={row.kr_code}>{row.kr_code}</td>
                    {section.breakdown.map((b) => <td key={b} className="meta">{row.breakdown[b] || "—"}</td>)}
                    {scenarios.map((sc) =>
                      periodCols.map((p) => {
                        const rec = row.byKey[`${sc}__${p}`];
                        const v = rec?.value ?? null;
                        if (section.row_type === "O") {
                          return <td key={`${sc}_${p}`} className="readonly">{formatValue(v, section.unit)}</td>;
                        }
                        // Input cell
                        return (
                          <td key={`${sc}_${p}`}>
                            {rec ? (
                              <input
                                type="number"
                                step="0.01"
                                defaultValue={v ?? ""}
                                onBlur={(e) => {
                                  const nv = e.target.value === "" ? null : Number(e.target.value);
                                  onEdit(rec, nv);
                                }}
                              />
                            ) : <span style={{ color: "#9ca3af" }}>—</span>}
                          </td>
                        );
                      })
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
