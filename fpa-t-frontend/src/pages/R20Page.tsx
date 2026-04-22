import { useParams, useSearchParams } from "react-router-dom";
import { useR20Data } from "../hooks/useR20Data";
import R20InputScreen from "../components/R20/R20InputScreen";

export default function R20Page() {
  const { role = "GH" } = useParams();
  const [search] = useSearchParams();
  const variant = search.get("variant");
  const zblock = search.get("zblock") ?? "";
  const ff = search.get("ff") ?? "MF";

  const { loading, error, schema, records, reload } = useR20Data(role.toUpperCase(), zblock, variant, ff);

  if (loading) return <p>Loading…</p>;
  if (error) return <div className="error-banner">Error: {error}</div>;
  if (!schema) return <p>No schema.</p>;

  if (!zblock) {
    return (
      <div className="error-banner">
        Missing <code>?zblock=</code> in URL. Example:
        <br /><code>/r20/input/{role}?zblock=PLN/Demo/OPT/G/MF/2026APR22{variant ? `&variant=${variant}` : ""}</code>
      </div>
    );
  }

  return (
    <R20InputScreen
      role={role.toUpperCase()}
      variant={variant}
      zblock={zblock}
      schema={schema}
      initialRecords={records}
      onReload={reload}
    />
  );
}
