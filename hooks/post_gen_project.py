"""Post-generation hook — clean up conditional files and initialise the project."""

import os
import shutil

USE_S3 = "{{ cookiecutter.use_s3 }}"
USE_DOCKER = "{{ cookiecutter.use_docker }}"
USE_GITHUB_ACTIONS = "{{ cookiecutter.use_github_actions }}"
INCLUDE_API_CONNECTOR = "{{ cookiecutter.include_api_connector }}"
INCLUDE_DATABASE_CONNECTOR = "{{ cookiecutter.include_database_connector }}"


def remove_file(filepath: str) -> None:
    if os.path.isfile(filepath):
        os.remove(filepath)


def remove_dir(dirpath: str) -> None:
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)


# Remove S3-related files when not needed
if USE_S3 == "no":
    remove_file(os.path.join("src", "{{ cookiecutter.project_slug }}", "services", "s3_service.py"))
    remove_file(os.path.join("tests", "unit", "test_s3_service.py"))

# Remove Docker file when not needed
if USE_DOCKER == "no":
    remove_file("Dockerfile")

# Remove GitHub Actions when not needed
if USE_GITHUB_ACTIONS == "no":
    remove_dir(".github")

# Remove database connector when not needed
if INCLUDE_DATABASE_CONNECTOR == "no":
    remove_file(os.path.join("src", "{{ cookiecutter.project_slug }}", "connectors", "database_connector.py"))

print("")
print("=" * 60)
print("  Project '{{ cookiecutter.project_slug }}' generated successfully!")
print("=" * 60)
print("")
print("  Next steps:")
print("")
print("    cd {{ cookiecutter.project_slug }}")
print("    git init")
print("    uv sync --all-extras")
print("    uv run pre-commit install")
print("    cp .env.example .env")
print("    make test")
print("")
print("=" * 60)
