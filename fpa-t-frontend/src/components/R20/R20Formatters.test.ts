import { describe, it, expect } from "vitest";
import { formatValue, formatDelta } from "./R20Formatters";

describe("formatValue", () => {
  it("null → —", () => {
    expect(formatValue(null, "bVND")).toBe("—");
    expect(formatValue(NaN, "bVND")).toBe("—");
  });
  it("bVND 2dp", () => {
    expect(formatValue(1234.5, "bVND")).toBe("1,234.50");
  });
  it("mVND 0dp", () => {
    expect(formatValue(23375, "mVND")).toBe("23,375");
  });
  it("% 2dp + suffix", () => {
    expect(formatValue(25, "%")).toBe("25.00%");
  });
  it("person integer", () => {
    expect(formatValue(4, "person")).toBe("4");
  });
});

describe("formatDelta", () => {
  it("null → IDLE", () => expect(formatDelta(null)).toBe("IDLE"));
  it("positive signed", () => expect(formatDelta(12.34)).toBe("+12.34"));
  it("negative signed", () => expect(formatDelta(-5.5)).toBe("-5.50"));
});
