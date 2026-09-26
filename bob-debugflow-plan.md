# Bob DebugFlow — Implementation Plan

> **Status:** Approved — all decisions locked. Ready for implementation.

## Top-Level Overview

**Goal:** Build a self-contained hackathon prototype that demonstrates IBM Bob IDE as the core engine of a structured, agentic debugging workflow applied to a realistic Python REST API project.

**Scope:**
- A small Python REST API (FastAPI) with **6 intentionally seeded, realistic bugs** covering wrong HTTP status, missing validation, ORM null guard, unhandled exception, float arithmetic, and DB resource leak.
- A Bob custom mode called **DebugFlow** that walks a developer through every phase of debugging automatically using Bob's agentic tools.
- A second Bob custom mode called **CodeReview** used exclusively during Phase 8; it produces its own structured review findings which DebugFlow incorporates into the final `debug_report.md`.
- A JSON metrics file (`reports/metrics.json`) and a Markdown report (`reports/debug_report.md`) generated at the end to measure before-vs-after productivity.

**Approach:**
Each phase of the workflow maps to a dedicated sub-task below. The demo story is: a developer opens the repository, activates DebugFlow mode in Bob, and Bob autonomously investigates, fixes, tests, reviews, and reports — with the developer acting as approver at **four fixed gates only** (after phases 4, 5, 7, and 8). Bob does not pause at any other phase.

**Non-Goals:**
- No CI/CD pipeline integration.
- No containerization or cloud deployment.
- No database beyond SQLite (in-memory for tests).
- No frontend UI.
- No external APIs, cloud services, or unnecessary infrastructure.

---

## Repository Structure (Target)

```
Bob-DebugFlow/
├── app/                        # FastAPI sample application
│   ├── __init__.py
│   ├── main.py                 # App entry point, route registration
│   ├── models.py               # Pydantic models / SQLAlchemy ORM models
│   ├── database.py             # DB session management (SQLite)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── users.py            # User CRUD routes (bugs seeded here)
│   │   └── items.py            # Item CRUD routes (bugs seeded here)
│   └── utils.py                # Helper utilities (bugs seeded here)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures, test DB setup
│   ├── test_users.py           # Tests that expose user-route bugs
│   └── test_items.py           # Tests that expose item-route bugs
├── .bob/
│   └── custom_modes.yaml       # DebugFlow + CodeReview mode definitions
├── skills/
│   └── debugflow-skill.md      # Bob skill: DebugFlow phase instructions
├── reports/
│   ├── debug_report.md         # Generated: human-readable summary
│   └── metrics.json            # Generated: before/after productivity data
├── requirements.txt
├── .flake8                     # Linter configuration
└── README.md                   # Project overview and demo instructions
```

---

## Sub-Tasks

---

### Sub-Task 1 — Python Sample Application (FastAPI with Seeded Bugs)

**Status:** `[x] done`

**Intent:**
Create the FastAPI application that serves as the subject of the debugging workflow. The app must be realistic enough that bugs are non-trivial to spot without tooling, but small enough to fully understand in minutes. Bugs must cover multiple categories to demonstrate the full investigation workflow.

**Bug Inventory (to be seeded):**

| ID  | Location             | Bug Type                       | Description |
|-----|----------------------|-------------------------------|-------------|
| B1  | `routes/users.py`    | Off-by-one / wrong HTTP status | POST /users returns 200 instead of 201 |
| B2  | `routes/users.py`    | Missing input validation       | Email field not validated — any string accepted |
| B3  | `routes/items.py`    | SQL/ORM logic error            | Filter uses `==` on a nullable field without null guard |
| B4  | `routes/items.py`    | Unhandled exception path       | GET /items/{id} raises unhandled KeyError instead of 404 |
| B5  | `utils.py`           | Silent data corruption         | Price rounding uses incorrect float arithmetic |
| B6  | `database.py`        | Resource leak                  | DB session never closed in error path |

**Expected Outcomes:**
- `app/` is a runnable FastAPI application.
- All six bugs are present and reproducible.
- Running `pytest` against the initial codebase produces a predictable set of failures that map 1:1 to the seeded bugs.
- `flake8` reports at least one style issue related to a bug.

**Todo List:**
1. Create `requirements.txt` with: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic[email]`, `pytest`, `pytest-cov`, `httpx`, `flake8`.
2. Create `app/database.py` — SQLite engine, SessionLocal, Base (with seeded resource-leak bug B6).
3. Create `app/models.py` — `User` and `Item` ORM + Pydantic schemas.
4. Create `app/utils.py` — price rounding helper (with seeded float bug B5).
5. Create `app/routes/users.py` — POST/GET/DELETE user routes (with B1, B2).
6. Create `app/routes/items.py` — POST/GET/DELETE item routes (with B3, B4).
7. Create `app/main.py` — app factory, router registration.
8. Create `tests/conftest.py` — in-memory SQLite fixture, TestClient setup.
9. Create `tests/test_users.py` — tests that fail against B1, B2.
10. Create `tests/test_items.py` — tests that fail against B3, B4.
11. Create `.flake8` config file.
12. Verify: `pytest` run shows exactly the expected failures; `flake8` flags expected issues.

**Relevant Context:**
- All bugs must be subtle enough that they are not immediately obvious on first read.
- Tests must be written to the *correct* behaviour so they fail against the buggy code and pass after fixes.

---

### Sub-Task 2 — Bob DebugFlow Custom Mode

**Status:** `[x] done`

**Intent:**
Define the `DebugFlow` and `CodeReview` Bob custom modes in `.bob/custom_modes.yaml`. DebugFlow is the primary orchestrator mode. CodeReview is a focused review agent activated during Phase 8 — it **produces its own structured review findings** (a `code_review_findings` block), which DebugFlow then reads and incorporates into `reports/debug_report.md` during Phase 9.

**Expected Outcomes:**
- `.bob/custom_modes.yaml` contains valid entries for both `DebugFlow` and `CodeReview`.
- Activating DebugFlow in Bob changes Bob's persona and available instructions to the full debugging workflow.
- Activating CodeReview in Bob produces a structured findings block covering correctness, style, and regression risk for each changed file.
- The mode references the `debugflow-skill.md` skill for phase-by-phase instructions.

**Todo List:**
1. Create `.bob/custom_modes.yaml`.
2. Define `DebugFlow` mode with:
   - `roleDefinition`: structured debugging agent persona; orchestrates all 10 phases; pauses only at gates after phases 4, 5, 7, and 8.
   - Permission groups: `read`, `edit`, `command`, `mcp`.
   - Reference to the `debugflow-skill.md` skill.
3. Define `CodeReview` mode with:
   - `roleDefinition`: focused code review agent; reads diff of changed files; produces a structured `code_review_findings` block with sections: Summary, Per-File Findings (correctness, style, regression risk), and Overall Verdict.
   - Permission groups: `read`, `edit`.
4. Validate YAML schema against Bob's `custom_modes.yaml` spec.

**Relevant Context:**
- Bob's `custom_modes.yaml` lives at `.bob/custom_modes.yaml`.
- Permission group names: `read`, `edit`, `command`, `mcp`, `browser`.
- The `roleDefinition` field is a plain string describing the agent persona.
- CodeReview mode writes its findings to `reports/code_review_findings.md`; DebugFlow reads this file during Phase 9 report assembly.

---

### Sub-Task 3 — Bob DebugFlow Skill

**Status:** `[x] done`

**Intent:**
Create `skills/debugflow-skill.md` — the Bob skill that encodes the full 10-phase DebugFlow workflow. When the DebugFlow mode activates this skill, Bob receives structured instructions for every phase. This is the core intellectual artifact of the project.

**Phases encoded in the skill:**

| Phase | Name                        | Key Bob Capability Used |
|-------|-----------------------------|------------------------|
| 1     | Codebase Understanding      | `GetSymbolsOverview`, `read_file`, `grep` |
| 2     | Bug Detection               | `execute_command` (pytest + flake8), `grep` |
| 3     | Root-Cause Analysis         | `FindSymbol`, `FindReferencingSymbols`, `read_file` |
| 4     | Parallel Investigation      | `spawn_subagent` (one per bug cluster) |
| 5     | Fix Implementation          | `apply_diff`, `search_and_replace` |
| 6     | Automated Testing           | `execute_command` (pytest --cov) |
| 7     | Verification                | `execute_command` (flake8 + pytest re-run) |
| 8     | Code Review                 | Switch to `CodeReview` mode |
| 9     | Debugging Report            | `write_file` (debug_report.md) |
| 10    | Productivity Measurement    | `write_file` (metrics.json) |

**Expected Outcomes:**
- `skills/debugflow-skill.md` is a valid Bob skill file with correct frontmatter.
- Each phase has a clear prompt instruction block telling Bob what tools to call, in what order, and what to record.
- The skill specifies exactly **four** developer approval gates: after Phase 4 (investigation findings), Phase 5 (proposed fixes), Phase 7 (verification), and Phase 8 (code review). Bob proceeds automatically through all other phases without pausing.
- Phase 8 instructs Bob to switch to `CodeReview` mode, which writes `reports/code_review_findings.md` independently.
- Phase 9 instructs Bob (back in DebugFlow mode) to read `reports/code_review_findings.md` and merge it into `reports/debug_report.md`.

**Todo List:**
1. Create `skills/debugflow-skill.md` with valid Bob skill frontmatter (`name`, `description`, `version`).
2. Write Phase 1 instructions: map file tree, identify modules, summarise architecture. **No approval gate.**
3. Write Phase 2 instructions: run `pytest` and `flake8`, collect failure list, format as structured bug list. **No approval gate.**
4. Write Phase 3 instructions: for each bug, trace call graph, identify root cause, document findings. **No approval gate.**
5. Write Phase 4 instructions: spawn one subagent per bug cluster (routes bugs vs. utils/db bugs), merge findings. **Approval gate — present findings; wait for developer approval before continuing.**
6. Write Phase 5 instructions: apply minimal targeted fixes using `apply_diff`/`search_and_replace`; no unrelated changes. **Approval gate — present diff summary; wait for developer approval before continuing.**
7. Write Phase 6 instructions: run `pytest --cov=app --cov-report=term-missing`; assert all tests pass. **No approval gate.**
8. Write Phase 7 instructions: run `flake8`; confirm zero new lint issues introduced by fixes. **Approval gate — present full quality gate results; wait for developer approval before continuing.**
9. Write Phase 8 instructions: switch to `CodeReview` mode; CodeReview agent reviews each changed file and writes structured findings to `reports/code_review_findings.md`. **Approval gate — present code review findings; wait for developer approval before continuing.**
10. Write Phase 9 instructions: switch back to DebugFlow mode; read `reports/code_review_findings.md`; write `reports/debug_report.md` incorporating all findings. **No approval gate.**
11. Write Phase 10 instructions: write `reports/metrics.json` with structured before/after data (bugs found, tests passing, coverage %, lint issues). **No approval gate.**

**Relevant Context:**
- Bob skill files live in `skills/` (relative to the workspace root, not `.bob/`).
- The frontmatter must include at minimum: `name` (kebab-case), `description`, `version`.
- Approval gates must use `ask_followup_question` to pause and explicitly wait for developer confirmation with "Proceed" / "Abort" options.
- CodeReview mode writes to `reports/code_review_findings.md`; this file must exist as a stub before Phase 8 runs.

---

### Sub-Task 4 — README and Demo Script

**Status:** `[x] done`

**Intent:**
Write a `README.md` that serves as both project documentation and a live demo script for the hackathon presentation. It must clearly explain what Bob DebugFlow is, how to set it up, and how to run the demo end-to-end.

**Expected Outcomes:**
- `README.md` explains the project goal, architecture, and each workflow phase.
- Step-by-step setup instructions allow a judge to reproduce the demo from scratch.
- A "What to watch" section narrates the expected Bob behaviour at each phase for judges.
- The README includes a workflow diagram (ASCII or Mermaid fenced block).

**Todo List:**
1. Write project overview section: what is Bob DebugFlow, why it matters.
2. Write prerequisites section: Python 3.11+, Bob IDE, how to install dependencies.
3. Write "Activate DebugFlow" section: how to switch to DebugFlow mode in Bob.
4. Write per-phase walkthrough: what Bob does, what the developer sees, what to approve.
5. Write "Seeded Bugs" reference table: maps bug ID to file, type, and symptom.
6. Write "Reports" section: explains `debug_report.md` and `metrics.json` outputs.
7. Add a workflow diagram showing the 10-phase pipeline.

**Relevant Context:**
- The README is the primary artefact judges will read; it must be polished.
- The demo story must be coherent: developer opens repo → activates DebugFlow → Bob runs → developer approves phases → reports appear.

---

### Sub-Task 5 — Metrics and Report Templates

**Status:** `[x] done`

**Intent:**
Pre-define the schema for all three report files so that the skill produces consistent, well-formatted output at runtime. These stubs also serve as reference artefacts for judges evaluating the demo output.

**Expected Outcomes:**
- `reports/metrics.json` stub has all keys present with empty/zero values; Bob fills it in during Phase 10.
- `reports/debug_report.md` stub has all section headers and placeholder text; Bob fills it in during Phase 9.
- `reports/code_review_findings.md` stub exists so CodeReview mode has a target file to write to during Phase 8.
- The skill instructions in Sub-Task 3 explicitly reference these file paths and schemas.

**Todo List:**
1. Create `reports/metrics.json` as a template stub with all keys present but empty/zero values.
2. Create `reports/debug_report.md` as a template stub with all section headers and placeholder text.
3. Create `reports/code_review_findings.md` as a template stub for CodeReview mode output.
4. Confirm that the skill (Sub-Task 3) Phase 8 and Phase 9 instructions reference the exact paths `reports/code_review_findings.md` and `reports/debug_report.md`.

**Relevant Context:**
- `metrics.json` must include: `timestamp`, `bugs_seeded`, `bugs_detected`, `tests_before` (pass/fail counts), `tests_after` (pass/fail counts), `coverage_before_pct`, `coverage_after_pct`, `lint_issues_before`, `lint_issues_after`, `phases_completed`.
- `debug_report.md` must include sections: Executive Summary, Bug Inventory, Root-Cause Analysis, Fixes Applied, Test Results, Code Review Notes, Productivity Delta.
- `code_review_findings.md` must include sections: Summary, Per-File Findings (correctness, style, regression risk), Overall Verdict.

---

## Milestones

| Milestone | Sub-Tasks Covered | Deliverable |
|-----------|-------------------|-------------|
| M1 — Runnable App with Bugs | Sub-Task 1 | FastAPI app that fails tests predictably |
| M2 — Bob Modes Configured | Sub-Task 2 | DebugFlow + CodeReview modes active in Bob; CodeReview writes its own findings |
| M3 — Skill Encoded | Sub-Task 3 | Full 10-phase skill with 4 approval gates; CodeReview findings merged into final report |
| M4 — Demo-Ready | Sub-Task 4 + 5 | README, all three report stubs; full demo runnable end-to-end |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | FastAPI | Modern, type-annotated, realistic in industry |
| Database | SQLite in-memory | Zero infra, reproducible, fast for tests |
| Test runner | pytest + pytest-cov | Standard; coverage output feeds metrics |
| Linter | flake8 | Lightweight, widely understood |
| Bug seeding strategy | 6 bugs, subtle but deterministic | Covers status, validation, ORM, exceptions, arithmetic, resource management |
| Parallel investigation | spawn_subagent per bug cluster | Demonstrates Bob's multi-agent capability explicitly |
| Developer approval gates | **Only** after phases 4, 5, 7, 8 | Realistic cadence — not every phase; keeps demo moving |
| CodeReview mode | Produces own `code_review_findings.md` | Demonstrates multi-mode collaboration; DebugFlow assembles final report |
| Report formats | JSON + Markdown (3 files total) | JSON for metrics; Markdown for human-readable outputs; clear judge artefacts |
| Scope constraint | No external APIs, cloud, or frontend | Hackathon-focused; demo must run fully offline |
