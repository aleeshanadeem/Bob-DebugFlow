# Bob DebugFlow  -  AI Debugging Workflow Assistant

> IBM Bob Hackathon Project  
> Demonstrating IBM Bob 2.0 as a structured, agentic debugging workflow engine.

---

## The Problem

Debugging a real codebase is not a single action  -  it is a multi-step workflow:

```
Issue reported
    -> Read and understand the codebase
    -> Run tests and linter to detect failures
    -> Trace failures to root causes
    -> Investigate across multiple files and layers
    -> Propose and apply targeted fixes
    -> Run tests again to verify
    -> Run linter to check for regressions
    -> Code review the changes
    -> Write a report
    -> Measure what was achieved
```

Every step requires context, care, and judgement. Developers working through this manually face:

- **Time cost**  -  context-switching between tools (editor, terminal, test runner, linter) adds overhead at every step.
- **Effort cost**  -  tracking findings across phases (what failed, why, what was changed) requires manual note-taking.
- **Error cost**  -  root-cause misidentification leads to incorrect fixes. Fixes applied without review introduce regressions.
- **Rework cost**  -  skipping verification or code review means bugs that appear fixed may resurface.

For a small codebase with 6 bugs, an experienced developer might spend 30-60 minutes doing this carefully. For a larger codebase with unfamiliar code, this easily scales to hours.

---

## The Solution

**Bob DebugFlow** demonstrates how [IBM Bob 2.0](https://www.ibm.com/bob) can act as the core orchestrator of this entire debugging workflow  -  not as a chatbot that answers questions, but as an autonomous agent that:

- **Understands** the codebase structure before doing anything.
- **Detects** all failures using real tool execution (pytest, flake8).
- **Analyses** root causes by reading and tracing code symbols.
- **Investigates** in parallel using spawned subagents.
- **Implements** only the approved minimal fixes.
- **Verifies** the fixes with automated tests and linting.
- **Reviews** the changes through a dedicated CodeReview mode.
- **Reports** findings in structured, human-readable and machine-readable formats.
- **Measures** the productivity impact of the session.

**This is not a code generator.** Bob does not rewrite code speculatively. Every change is minimal, evidence-backed, and developer-approved before being applied.

---

## IBM Bob Capabilities Demonstrated

| Capability | How It Is Used in DebugFlow |
|---|---|
| **Agent Mode** | Default mode for executing multi-step autonomous workflows |
| **Plan Mode** | Used to design the project architecture and workflow before implementation |
| **Custom Modes** | `DebugFlow` mode orchestrates the 10-phase workflow; `CodeReview` mode performs independent review |
| **Skills** | `skills/debugflow-skill.md` encodes the full 10-phase workflow as a reusable, self-activating skill |
| **Subagents** | Phase 4 spawns two parallel subagents  -  one per bug cluster  -  for independent investigation |
| **Parallel Investigation** | Route-layer bugs and utility/DB-layer bugs are investigated simultaneously |
| **Approval Gates** | Four hard stops where Bob presents findings and waits for explicit developer sign-off |
| **Code Review** | A dedicated `CodeReview` mode reviews every changed file and produces structured findings |
| **Automated Testing** | `pytest --cov` is run before and after fixes; results are captured and compared |
| **Reporting** | `debug_report.md` assembles all findings; `code_review_findings.md` holds review output |
| **Productivity Measurement** | `metrics.json` records before/after metrics and estimated time saved |

---

## The 10-Phase DebugFlow Workflow

```
Phase 1  Codebase Understanding     Map the repository. Read every relevant file.
Phase 2  Bug Detection              Run pytest + flake8. Record all failures.
Phase 3  Root-Cause Analysis        Trace each failure to its exact defective line.
Phase 4  Parallel Investigation     Two subagents investigate route vs. utility/DB bugs.
          [APPROVAL GATE 4]         Developer reviews consolidated findings.
Phase 5  Fix Implementation         Propose and apply minimal, targeted fixes.
          [APPROVAL GATE 5]         Developer approves the proposed diff before it is applied.
Phase 6  Automated Testing          Run pytest --cov. Capture before/after results.
Phase 7  Verification               Run pytest + flake8. Confirm zero failures, zero new issues.
          [APPROVAL GATE 7]         Developer reviews the quality gate summary.
Phase 8  Code Review                CodeReview mode reviews changed files. Writes findings.
          [APPROVAL GATE 8]         Developer reviews and approves code review findings.
Phase 9  Debugging Report           Write reports/debug_report.md with all findings.
Phase 10 Productivity Measurement   Write reports/metrics.json with before/after metrics.
```

The developer is in control at every gate. Bob does not apply fixes, proceed past verification, or generate the final report without explicit approval.

---

## The Six Seeded Bugs

This project contains six intentional, realistic bugs seeded across different layers of the API. They are subtle enough to require careful investigation but deterministically reproducible by the test suite.

| ID | File | Bug Type | Symptom |
|----|------|----------|---------|
| **B1** | `app/routes/users.py` | Wrong HTTP status code | `POST /users/` returns `200 OK` instead of `201 Created` |
| **B2** | `app/models.py` | Missing input validation | Email field accepts any string  -  no format validation applied |
| **B3** | `app/routes/items.py` | Nullable-field handling issue | `GET /items/?description=` (empty string) returns empty list instead of all items |
| **B4** | `app/routes/items.py` | Unhandled exception | `GET /items/{id}` raises `KeyError` (500) instead of returning `404 Not Found` |
| **B5** | `app/utils.py` | Floating-point price arithmetic | `round_price()` truncates to 1 decimal place  -  `19.99` is stored as `19.9` |
| **B6** | `app/database.py` | Database session resource leak | `get_db()` does not close the session in the error path  -  connections are leaked |

> **Note:** The fixes for these bugs are not documented here. Bob identifies and proposes each fix during the workflow. The developer reviews and approves the proposed changes before they are applied.

---

## Project Structure

```
Bob-DebugFlow/
+-- app/                        # FastAPI sample application (contains seeded bugs)
|   +-- __init__.py
|   +-- main.py                 # App factory and router registration
|   +-- database.py             # SQLAlchemy engine and session management [B6]
|   +-- models.py               # ORM models and Pydantic schemas [B2]
|   +-- utils.py                # Price rounding helper [B5]
|   +-- routes/
|       +-- __init__.py
|       +-- users.py            # User CRUD endpoints [B1, B2]
|       +-- items.py            # Item CRUD endpoints [B3, B4]
+-- tests/
|   +-- __init__.py
|   +-- conftest.py             # In-memory SQLite fixture and TestClient setup
|   +-- test_users.py           # Tests that expose B1 and B2
|   +-- test_items.py           # Tests that expose B3, B4, and B5
+-- .bob/
|   +-- custom_modes.yaml       # DebugFlow and CodeReview mode definitions
+-- skills/
|   +-- debugflow-skill.md      # 10-phase workflow skill loaded by DebugFlow mode
+-- reports/                    # Generated by Bob during the workflow run
|   +-- debug_report.md         # Human-readable debugging session summary
|   +-- metrics.json            # Before/after productivity metrics
|   +-- code_review_findings.md # Structured code review output from CodeReview mode
+-- bob_sessions/               # Bob task session screenshots (demo evidence)
+-- requirements.txt            # Python dependencies
+-- .flake8                     # Linter configuration
+-- README.md                   # This file
```

---

## Installation

### Prerequisites

- Python 3.11 or later
- IBM Bob IDE (with custom modes support)

### Setup

```powershell
# Create and activate a virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
python -m pip install -r requirements.txt
```

### Run the test suite (intentional failures expected)

```powershell
python -m pytest tests/ -v --tb=short
```

### Run the linter

```powershell
python -m flake8 app/ tests/
```

---

## Expected Initial Baseline

Running the test suite against the unmodified (buggy) codebase produces the following intentional results:

```
7 failed, 10 passed
```

Running flake8 produces:

```
tests/test_users.py:15:1: F401 'pytest' imported but unused
```

**These failures are intentional.** They represent the six seeded bugs. The test suite is written against the correct expected behaviour  -  it will pass once all bugs are fixed.

| Failure | Bug |
|---------|-----|
| `test_create_user_returns_201` | B1 |
| `test_create_user_rejects_invalid_email` | B2 |
| `test_create_user_rejects_missing_at_symbol` | B2 |
| `test_list_items_empty_description_param_returns_all` | B3 |
| `test_get_nonexistent_item_returns_404` | B4 (raises 500 KeyError) |
| `test_price_rounded_to_two_decimal_places` | B5 |
| `test_price_rounding_preserves_cents` | B5 |

> B6 (database session resource leak) is a structural bug visible in `app/database.py`. It does not produce a direct pytest failure but is identified by Bob during the root-cause analysis and code review phases.

---

## Running DebugFlow

1. Open this repository in IBM Bob IDE.
2. Open the mode picker and select **DebugFlow**.
3. Type or say: `Start the DebugFlow debugging workflow.`
4. Bob will begin Phase 1 automatically and proceed through each phase.
5. At each of the four approval gates, read Bob's findings and choose to **Proceed** or **Abort**.

Bob will not apply any changes or generate reports without your explicit approval.

---

## Approval Gates

The workflow has four mandatory checkpoints where Bob stops and waits for developer sign-off:

| Gate | After Phase | What Bob Presents | Developer Decision |
|------|-------------|-------------------|--------------------|
| **Gate 4** | Parallel Investigation | Consolidated findings table from both subagents | Approve findings / Abort |
| **Gate 5** | Fix Implementation | Exact proposed diff for every bug fix | Approve and apply / Abort |
| **Gate 7** | Verification | Full quality gate summary (test counts, lint delta) | Proceed to review / Abort |
| **Gate 8** | Code Review | Structured review findings from CodeReview mode | Approve and generate report / Abort |

If the developer chooses **Abort** at any gate, Bob stops immediately without making further changes.

---

## Reports

The following files are generated by Bob during the workflow run. They do not exist until the workflow completes.

| File | Generated By | Contents |
|------|-------------|----------|
| `reports/code_review_findings.md` | CodeReview mode (Phase 8) | Per-file findings table: severity, line, dimension, finding. Overall verdict. |
| `reports/debug_report.md` | DebugFlow mode (Phase 9) | Full session report: problem statement, bug inventory, root causes, fixes, test results, review findings. |
| `reports/metrics.json` | DebugFlow mode (Phase 10) | Structured before/after metrics: bugs, tests, coverage, lint, timing, approval gates. |

---

## Bob Session Evidence

During and after the demo, screenshots of the Bob task session are stored under:

```
bob_sessions/
```

These screenshots serve as evidence of the workflow execution, approval gate interactions, and generated outputs for the hackathon submission.

---

## Measured Impact

At the end of a DebugFlow session, `reports/metrics.json` records the following productivity metrics:

| Metric | Description |
|--------|-------------|
| `bugs_identified` | Number of bugs Bob found and documented |
| `bugs_fixed` | Number of bugs verified as fixed by the test suite |
| `test_failures_before` | Number of failing tests before fixes |
| `test_failures_after` | Number of failing tests after fixes (target: 0) |
| `lint_issues_before` | Number of flake8 issues before fixes |
| `lint_issues_after` | Number of flake8 issues after fixes |
| `coverage_before_pct` | Test coverage percentage before fixes |
| `coverage_after_pct` | Test coverage percentage after fixes |
| `estimated_manual_debug_time_minutes` | Estimate of how long a developer would spend doing this manually |
| `debugflow_time_minutes` | Actual elapsed time for the Bob-assisted session |
| `estimated_time_saved_minutes` | The difference  -  the productivity gain |
| `approval_gates_approved` | Number of gates where the developer chose Proceed |

---

## Hackathon Relevance

Bob DebugFlow directly addresses the IBM Bob Hackathon theme of **developer workflow improvement**:

| Dimension | What This Project Demonstrates |
|-----------|-------------------------------|
| **Reduced manual effort** | Bob replaces 10 sequential manual steps with a single orchestrated session |
| **Controlled AI assistance** | The developer approves every significant action  -  Bob does not operate autonomously without consent |
| **Measurable productivity** | Before/after metrics are captured programmatically and presented as a structured report |
| **Multi-agent coordination** | Parallel subagent investigation demonstrates Bob's ability to coordinate independent workers |
| **Mode specialisation** | DebugFlow and CodeReview are purpose-built modes, not generic prompts  -  each has constrained permissions and a focused role |
| **Real developer workflow** | Every phase maps to something a developer actually does today; Bob accelerates and structures the process rather than replacing judgement |

---

## License

MIT
