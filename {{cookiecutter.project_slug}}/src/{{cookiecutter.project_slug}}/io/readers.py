"""File readers for common data formats.

All readers work with both local paths and file-like objects so they can be
composed with :class:`~{{ cookiecutter.project_slug }}.services.s3_service.S3Service`.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import IO, Any


def read_json(source: str | Path | IO[bytes]) -> Any:
    """Read JSON from a file path or file-like object.

    Parameters
    ----------
    source:
        A local file path (str / Path) or an already-opened binary stream.
    """
    if isinstance(source, (str, Path)):
        with open(source, encoding="utf-8") as fh:
            return json.load(fh)
    return json.loads(source.read())


def read_csv_lines(
    source: str | Path | IO[str],
    *,
    delimiter: str = ",",
    has_header: bool = True,
) -> list[dict[str, str]]:
    """Read a CSV file and return a list of row dicts.

    Parameters
    ----------
    source:
        A local file path or a text-mode file-like object.
    delimiter:
        Column delimiter (default ``,``).
    has_header:
        Whether the first row contains column names.
    """
    if isinstance(source, (str, Path)):
        with open(source, encoding="utf-8", newline="") as fh:
            return _parse_csv(fh, delimiter=delimiter, has_header=has_header)
    return _parse_csv(source, delimiter=delimiter, has_header=has_header)


def _parse_csv(fh: IO[str], *, delimiter: str, has_header: bool) -> list[dict[str, str]]:
    if has_header:
        reader = csv.DictReader(fh, delimiter=delimiter)
        return list(reader)
    reader_raw = csv.reader(fh, delimiter=delimiter)
    rows = list(reader_raw)
    return [{str(i): v for i, v in enumerate(row)} for row in rows]
