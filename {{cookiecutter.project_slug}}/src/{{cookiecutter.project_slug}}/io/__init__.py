"""Data I/O layer — readers and writers for common formats."""

from {{ cookiecutter.project_slug }}.io.readers import read_json, read_csv_lines
from {{ cookiecutter.project_slug }}.io.writers import write_json, write_csv

__all__ = ["read_json", "read_csv_lines", "write_json", "write_csv"]
