"""File writers for common data formats."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import IO, Any


def write_json(
    data: Any,
    destination: str | Path | IO[str],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """Serialize *data* as JSON to a file path or file-like object.

    Parameters
    ----------
    data:
        JSON-serializable object.
    destination:
        A local file path (str / Path) or a text-mode writable stream.
    indent:
        Pretty-print indentation level.
    ensure_ascii:
        When *False* (default), non-ASCII characters are written as-is.
    """
    payload = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
    if isinstance(destination, (str, Path)):
        Path(destination).write_text(payload + "\n", encoding="utf-8")
    else:
        destination.write(payload + "\n")


def write_csv(
    rows: list[dict[str, Any]],
    destination: str | Path | IO[str],
    *,
    fieldnames: list[str] | None = None,
    delimiter: str = ",",
) -> None:
    """Write a list of dicts as CSV.

    Parameters
    ----------
    rows:
        Each dict represents a row.
    destination:
        A local file path or a text-mode writable stream.
    fieldnames:
        Column order.  Defaults to keys of the first row.
    delimiter:
        Column delimiter (default ``,``).
    """
    if not rows:
        return
    fields = fieldnames or list(rows[0].keys())
    if isinstance(destination, (str, Path)):
        with open(destination, "w", encoding="utf-8", newline="") as fh:
            _write(fh, rows, fields, delimiter)
    else:
        _write(destination, rows, fields, delimiter)


def _write(fh: IO[str], rows: list[dict[str, Any]], fields: list[str], delimiter: str) -> None:
    writer = csv.DictWriter(fh, fieldnames=fields, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(rows)
