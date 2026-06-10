# Release Process

End-to-end flow from a feature branch to a published artifact in Artifactory.

## High-level flow

```mermaid
flowchart TD
    A([Developer]) -->|"git checkout -b feat/xyz"| B[Feature branch created]
    B -->|"git commit + push"| C[Branch pushed to origin]
    C -->|"open PR against main"| D[Pull Request opened]

    D --> E{{CI pipeline triggered}}
    E --> E1[Lint - ruff]
    E --> E2[Type check - mypy]
    E --> E3[Unit and integration tests]
    E --> E4[Security scan - bandit / trivy]
    E --> E5[Build wheel + Docker image]

    E1 & E2 & E3 & E4 & E5 --> F{All checks green?}
    F -->|No| G[Fix and push again]
    G --> E
    F -->|Yes| H[Code review]

    H --> I{Approved?}
    I -->|Changes requested| G
    I -->|Approved| J[Squash-merge into main]

    J --> K{{Release pipeline triggered on main}}
    K --> L[Determine next version - semantic-release]
    L --> M[Generate CHANGELOG.md from conventional commits]
    M --> N["Create git tag vX.Y.Z"]
    N --> O[Publish GitHub Release with release notes]
    O --> P[Build production artifact]
    P --> Q[(Publish to Artifactory)]
    Q --> R([Artifact available for deployment])

    style A fill:#d4e7ff,stroke:#1f4e8c
    style R fill:#d4f7d4,stroke:#1f8c3a
    style Q fill:#fff4c4,stroke:#8c6b1f
    style E fill:#ffe0e0,stroke:#8c1f1f
    style K fill:#ffe0e0,stroke:#8c1f1f
```

## Actors and responsibilities

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer
    participant Git as GitHub
    participant CI as CI (GitHub Actions)
    actor Rev as Reviewer
    participant Rel as Release Job
    participant Art as Artifactory

    Dev->>Git: Push feat/xyz branch
    Dev->>Git: Open Pull Request -> main
    Git->>CI: Trigger pr.yml workflow
    CI->>CI: lint + typecheck + tests + scan + build
    CI-->>Git: Report check statuses
    Git-->>Dev: Show failing/passing checks
    Rev->>Git: Review code, request changes / approve
    Dev->>Git: Address comments, push fixups
    CI->>CI: Re-run on each push
    Rev->>Git: Approve PR
    Dev->>Git: Squash-merge into main

    Git->>Rel: Trigger release.yml workflow on main
    Rel->>Rel: Compute next semver from commit messages
    Rel->>Rel: Generate CHANGELOG.md
    Rel->>Git: Commit changelog + create tag vX.Y.Z
    Rel->>Git: Create GitHub Release (notes)
    Rel->>Rel: Build wheel + Docker image
    Rel->>Art: Upload artifact (wheel + image)
    Art-->>Rel: 201 Created
    Rel-->>Dev: Notify (Slack / email)
```

## Branch and tag conventions

| Item | Convention | Example |
|---|---|---|
| Feature branch | `feat/<slug>` | `feat/user-profile` |
| Bugfix branch | `fix/<slug>` | `fix/login-timeout` |
| Hotfix branch | `hotfix/<slug>` | `hotfix/cve-2024-1234` |
| Commit format | Conventional Commits | `feat(api): add /users/me` |
| Release tag | `vMAJOR.MINOR.PATCH` | `v1.4.2` |
| Pre-release tag | `vX.Y.Z-rc.N` | `v1.4.2-rc.1` |

## Semver bump rules (driven by commit type)

```mermaid
flowchart LR
    C[Commits since last tag] --> T{Any 'BREAKING CHANGE' footer?}
    T -->|Yes| MAJOR[Bump MAJOR]
    T -->|No| F{Any feat: commits?}
    F -->|Yes| MINOR[Bump MINOR]
    F -->|No| P{Any fix: commits?}
    P -->|Yes| PATCH[Bump PATCH]
    P -->|No| SKIP[No release]
```

## Pipeline gates

| Stage | Tool | Blocking | Notes |
|---|---|---|---|
| Lint | `ruff check` | yes | Style + common bugs |
| Format | `ruff format --check` | yes | Enforces single style |
| Types | `mypy --strict` | yes | Catches contract drift |
| Unit tests | `pytest tests/unit` | yes | Must run < 1 min |
| Integration | `pytest tests/integration` | yes | Postgres testcontainer |
| Coverage | `pytest --cov` | yes | Threshold = 80% |
| SAST | `bandit` | yes | Python security linter |
| Container scan | `trivy image` | yes | CVE gate on final image |
| Dependency audit | `pip-audit` | yes | Known vuln dependencies |
| Build | `uv build` + `docker build` | yes | Artifact must be reproducible |

## Artifactory layout

```
artifactory/
├── pypi-local/
│   └── fastapi-service/
│       ├── fastapi_service-1.4.2-py3-none-any.whl
│       └── fastapi_service-1.4.2.tar.gz
└── docker-local/
    └── fastapi-service/
        ├── 1.4.2
        ├── 1.4              # rolling minor tag
        └── latest           # only on stable main
```

## Hotfix path (compressed flow)

```mermaid
flowchart LR
    P[Production incident] --> B[Branch hotfix/* off the release tag]
    B --> F[Fix + tests]
    F --> PR[PR to main]
    PR --> CI[CI pipeline - same gates]
    CI --> M[Merge + cherry-pick to active release branch if any]
    M --> R[Patch release tag vX.Y.Z+1]
    R --> A[(Artifactory)]
    A --> D[Deploy]
```
