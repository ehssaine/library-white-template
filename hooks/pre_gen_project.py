"""Pre-generation hook — validates template variables."""

import re
import sys

PROJECT_SLUG = "{{ cookiecutter.project_slug }}"

if not re.match(r"^[a-z][a-z0-9_]+$", PROJECT_SLUG):
    print(
        f"ERROR: '{PROJECT_SLUG}' is not a valid Python package name. "
        "Use only lowercase letters, digits, and underscores. "
        "Must start with a letter."
    )
    sys.exit(1)
