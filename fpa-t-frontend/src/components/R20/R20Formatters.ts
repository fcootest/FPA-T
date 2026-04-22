// Display formatters per AP S9

const fmt2dp = new Intl.NumberFormat("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmt0dp = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
const fmtSigned = new Intl.NumberFormat("en-US", {
  signDisplay: "always", minimumFractionDigits: 2, maximumFractionDigits: 2,
});

export function formatValue(val: number | null, unit: string): string {
  if (val == null || Number.isNaN(val) || !Number.isFinite(val)) return "—";
  switch (unit) {
    case "bVND": return fmt2dp.format(val);
    case "mVND": return fmt0dp.format(val);
    case "USD": return fmt2dp.format(val);
    case "%": return val.toFixed(2) + "%";
    case "person": return fmt0dp.format(val);
    default: return String(val);
  }
}

export function formatDelta(val: number | null): string {
  if (val == null) return "IDLE";
  return fmtSigned.format(val);
}
