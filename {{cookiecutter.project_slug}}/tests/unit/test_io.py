"""Tests for data I/O readers and writers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from {{ cookiecutter.project_slug }}.io.readers import read_json, read_csv_lines
from {{ cookiecutter.project_slug }}.io.writers import write_json, write_csv


@pytest.mark.unit
class TestJsonIO:
    def test_roundtrip(self, tmp_path: Path) -> None:
        data = {"key": "value", "numbers": [1, 2, 3]}
        path = tmp_path / "test.json"
        write_json(data, path)
        assert read_json(path) == data

    def test_write_creates_file(self, tmp_path: Path) -> None:
        path = tmp_path / "new.json"
        write_json({"a": 1}, path)
        assert path.exists()


@pytest.mark.unit
class TestCsvIO:
    def test_roundtrip(self, tmp_path: Path) -> None:
        rows = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        path = tmp_path / "test.csv"
        write_csv(rows, path)
        result = read_csv_lines(path)
        assert result == rows

    def test_empty_write(self, tmp_path: Path) -> None:
        path = tmp_path / "empty.csv"
        write_csv([], path)
        assert not path.exists()
