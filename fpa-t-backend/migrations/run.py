"""Migration runner (ISP S1).

Usage:
    python migrations/run.py migrations/R20_001_create_tables.sql
    python migrations/run.py migrations/R20_002_create_view.sql
"""
import sys
from pathlib import Path
from google.cloud import bigquery


def _strip_comments(sql: str) -> str:
    """Remove all `-- ...` line comments from SQL (BQ does not have block comments in our DDL)."""
    out_lines = []
    for line in sql.splitlines():
        idx = line.find("--")
        out_lines.append(line[:idx] if idx >= 0 else line)
    return "\n".join(out_lines)


def run_migration(sql_path: str, project: str = "fpa-t-494007") -> None:
    client = bigquery.Client(project=project)
    sql = Path(sql_path).read_text(encoding="utf-8")
    sql_no_comments = _strip_comments(sql)
    statements = [s.strip() for s in sql_no_comments.split(";") if s.strip()]
    for i, stmt in enumerate(statements, 1):
        print(f"[{i}/{len(statements)}] Executing...")
        client.query(stmt).result()
    print(f"Done: {sql_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python migrations/run.py <sql_file>")
        sys.exit(1)
    run_migration(sys.argv[1])
