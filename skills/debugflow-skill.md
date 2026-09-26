---
name: debugflow
description: >-
  Use when the developer activates the DebugFlow mode and wants Bob to run
  the full structured 10-phase debugging workflow on the Bob DebugFlow
  FastAPI project. Guides Bob through codebase understanding, bug detection,
  root-cause analysis, parallel investigation, fix implementation, testing,
  verification, code review, report generation, and productivity measurement.
metadata:
  disable-model-invocation: true
---

# DebugFlow Skill  -  10-Phase Debugging Workflow

This skill drives the complete DebugFlow debugging session. Follow every
phase in the order given. Never skip a phase. Never reorder phases. Never
apply fixes outside Phase 5. Always pause at the four approval gates and
wait for explicit developer confirmation before continuing.

---

## Workflow Rules (read before starting)

- **Evidence first.** Never assert a root cause without citing a specific
  file, line, and failing test or lint message.
- **Minimal changes only.** Every fix must be traceable to a specific bug ID.
  Do not reformat, refactor, or clean up surrounding code.
- **Approval gates are hard stops.** At each gate, present findings using
  `ask_followup_question` with exactly two options: one to proceed and one
  to abort. Do not continue if the developer chooses abort.
- **No silent fixes.** Never apply a change without first presenting it to
  the developer for approval.
- **Track state across phases.** Carry findings, metrics, and file change
  lists forward from each phase into the next.

---

## Phase 1  -  Codebase Understanding

**Goal:** Build a complete mental model of the repository before touching
anything.

**Steps:**

1. Use `list_files` on the workspace root to enumerate all top-level files
   and directories.

2. Use `GetSymbolsOverview` on each of the following files to identify all
   top-level symbols (classes, functions, routes):
   - `app/main.py`
   - `app/database.py`
   - `app/models.py`
   - `app/utils.py`
   - `app/routes/users.py`
   - `app/routes/items.py`

3. Use `read_file` to read `app/database.py` and `app/models.py` in full.
   Understand the ORM schema, the session lifecycle, and the Pydantic
   request/response contracts.

4. Use `read_file` to read `app/utils.py` in full. Identify any
   computation helpers and how they are used.

5. Use `grep` to find all imports of `get_db` and `round_price` across the
   codebase to understand their call sites:
   - Pattern: `get_db`
   - Pattern: `round_price`

6. Use `read_file` to read `tests/conftest.py`, `tests/test_users.py`, and
   `tests/test_items.py` in full. Note which tests exist and what behaviour
   each one asserts.

7. Produce a concise Architecture Summary in your response:
   - Repository layout (one line per file, with its responsibility)
   - Request lifecycle (HTTP request -> router -> ORM -> DB)
   - Dependencies between modules
   - Test coverage overview (which routes/helpers have tests)

**No approval gate. Continue automatically to Phase 2.**

---

## Phase 2  -  Bug Detection

**Goal:** Collect all observable failures without interpreting causes yet.

**Steps:**

1. Run the full test suite with verbose output and short tracebacks:
   ```
   python -m pytest tests/ -v --tb=short
   ```
   Capture the complete output.

2. Run the linter across the application and test code:
   ```
   python -m flake8 app/ tests/
   ```
   Capture the complete output.

3. From the pytest output, extract every FAILED test. For each one record:
   - Test ID (e.g. `tests/test_users.py::TestCreateUser::test_create_user_returns_201`)
   - Failure assertion message (the `AssertionError` line or exception type)
   - File and line number of the assertion

4. From the flake8 output, extract every reported issue. For each one record:
   - File and line number
   - Error code (e.g. F401)
   - Message

5. Present a numbered **Bug Detection Summary** table:

   | # | Source | Test/Rule | File | Symptom |
   |---|--------|-----------|------|---------|
   | 1 | pytest | test name | file:line | assertion message |
   | 2 | flake8 | F401 | file:line | message |

6. Record the following baseline metrics for later use in Phase 10:
   - `tests_before`: total test count
   - `test_failures_before`: count of FAILED tests
   - `lint_issues_before`: count of flake8 issues

**No approval gate. Continue automatically to Phase 3.**

---

## Phase 3  -  Root-Cause Analysis

**Goal:** Trace each symptom from Phase 2 to the exact defective line of
code and explain why it is wrong.

**Steps:**

For each item in the Phase 2 Bug Detection Summary, do the following:

1. Use `FindSymbol` with `include_body: true` to read the implementation
   of the function or class implicated by the test failure or lint message.

2. Use `FindReferencingSymbols` where the bug may involve a caller/callee
   relationship (e.g. a helper called by a route handler).

3. Use `read_file` with a precise line range to inspect the exact buggy
   section in context.

4. Identify and record the root cause using this template:

   ```
   Bug ID:        B<N>
   File:          app/...
   Line:          <N>
   Symptom:       What the test or linter observed
   Root Cause:    Why the code is wrong (specific mechanism)
   Correct Behaviour: What the code should do instead
   Evidence:      Test name + assertion / lint rule + line
   ```

5. Distinguish symptoms from root causes. For example:
   - A test expecting status 201 but receiving 200 is a *symptom*.
   - The missing `status_code=201` argument on the route decorator is the
     *root cause*.

6. Group the root causes by module:
   - Route layer: `app/routes/users.py`, `app/routes/items.py`
   - Utility layer: `app/utils.py`
   - Database layer: `app/database.py`
   - Schema layer: `app/models.py`

7. Produce a Root-Cause Analysis table:

   | Bug ID | File | Line | Root Cause | Correct Behaviour |
   |--------|------|------|------------|-------------------|

**No approval gate. Continue automatically to Phase 4.**

---

## Phase 4  -  Parallel Investigation

**Goal:** Use parallel subagents to independently verify the root causes,
then consolidate findings before presenting them for developer approval.

**Steps:**

1. Identify two investigation clusters based on the Phase 3 grouping:
   - **Cluster A  -  Route Layer:** bugs in `app/routes/users.py` and
     `app/routes/items.py` (typically B1, B2, B3, B4).
   - **Cluster B  -  Utility/DB Layer:** bugs in `app/utils.py` and
     `app/database.py` (typically B5, B6).

2. Use `spawn_subagent` to launch **two subagents in parallel**:

   **Subagent A prompt (route layer):**
   > Read `app/routes/users.py` and `app/routes/items.py` in full using
   > `read_file`. For each bug assigned to the route layer, verify the root
   > cause identified in Phase 3. Confirm the exact file, line, and
   > mechanism. Propose a plain-English fix description (one sentence per
   > bug). Return findings as a structured list: Bug ID | File | Line |
   > Confirmed Root Cause | Proposed Fix Description.

   **Subagent B prompt (utility/DB layer):**
   > Read `app/utils.py` and `app/database.py` in full using `read_file`.
   > For each bug assigned to the utility and database layers, verify the
   > root cause identified in Phase 3. Confirm the exact file, line, and
   > mechanism. Propose a plain-English fix description (one sentence per
   > bug). Return findings as a structured list: Bug ID | File | Line |
   > Confirmed Root Cause | Proposed Fix Description.

3. Wait for both subagents to return their results.

4. Merge the two result sets into a single **Consolidated Investigation
   Findings** table:

   | Bug ID | File | Line | Confirmed Root Cause | Proposed Fix |
   |--------|------|------|----------------------|--------------|

5. Note any discrepancies between Phase 3 analysis and subagent findings.
   If a subagent contradicts the Phase 3 root cause, report it explicitly
   and recommend which analysis to trust (with evidence).

6. **APPROVAL GATE 4:**
   Present the Consolidated Investigation Findings table to the developer.
   Use `ask_followup_question` with:
   - Question: "Phase 4 complete. Investigation findings are ready for
     review. All six root causes have been confirmed. Proceed to fix
     implementation?"
   - Option A: "Proceed to fix implementation"
   - Option B: "Abort workflow"

   **Do not continue to Phase 5 until the developer selects Option A.**

---

## Phase 5  -  Fix Implementation

**Goal:** Apply only the approved minimal fixes. Present a precise diff
summary before touching any file.

**Steps:**

1. For each bug in the approved Consolidated Investigation Findings, plan
   the exact change needed. For every planned change record:
   - Bug ID
   - File to modify
   - Current line content (exact)
   - Replacement line content (exact)
   - One-sentence rationale

2. Present the complete **Proposed Fix Summary** to the developer:

   ```
   Fix for B1  -  app/routes/users.py line <N>
     Before: @router.post("/", response_model=UserResponse)
     After:  @router.post("/", response_model=UserResponse, status_code=201)
     Why:    POST endpoints must return 201 Created per HTTP semantics.

   Fix for B2  -  app/models.py line <N>
     Before: email: str
     After:  email: EmailStr
     Why:    EmailStr triggers Pydantic email format validation.

   ... (one block per bug)
   ```

3. **APPROVAL GATE 5:**
   Use `ask_followup_question` with:
   - Question: "Phase 5 ready. The proposed fixes are listed above. Approve
     all fixes and apply them?"
   - Option A: "Approve and apply all fixes"
   - Option B: "Abort workflow  -  do not apply any changes"

   **Do not apply any changes until the developer selects Option A.**

4. After approval, apply each fix using `apply_diff` or
   `search_and_replace`. Apply fixes one at a time, in Bug ID order (B1
   through B6). For each fix:
   - Apply the change.
   - Confirm the exact line was changed as intended.
   - Do not touch any other lines in the file.

5. Produce a **Fix Application Log** listing every file modified, the line
   changed, and the bug ID it addresses.

**Do not run tests in this phase. Testing is Phase 6.**

---

## Phase 6  -  Automated Testing

**Goal:** Verify that all seeded bugs have been resolved by the test suite.

**Steps:**

1. Run the full pytest suite with coverage reporting:
   ```
   python -m pytest tests/ -v --cov=app --cov-report=term-missing
   ```
   Capture the complete output.

2. From the output extract and record:
   - Total tests run
   - Passed count
   - Failed count (must be 0  -  if not, stop and report which tests still
     fail before continuing)
   - Per-module coverage percentages (from the coverage report)

3. If any tests still fail, **stop here**. Do not proceed to Phase 7.
   Report the remaining failures clearly and ask the developer how to
   proceed using `ask_followup_question`.

4. Present a **Test Results Summary**:

   | Metric | Before (Phase 2) | After (Phase 6) |
   |--------|-----------------|----------------|
   | Total tests | N | N |
   | Passed | N | N |
   | Failed | N | 0 |
   | Coverage (app/) | N% | N% |

**No approval gate. Continue automatically to Phase 7 if all tests pass.**

---

## Phase 7  -  Verification

**Goal:** Confirm the full quality gate  -  zero test failures and zero new
lint issues  -  before declaring the bugs fixed.

**Steps:**

1. Run pytest one more time to confirm the Phase 6 result is stable:
   ```
   python -m pytest tests/ -v --tb=short
   ```

2. Run flake8 across the full codebase:
   ```
   python -m flake8 app/ tests/
   ```
   Capture the complete output.

3. Compare the flake8 output to the Phase 2 baseline:
   - Were any of the original lint issues resolved?
   - Were any new lint issues introduced by the fixes?
   - Net change in lint issue count.

4. Verify each of the six seeded bugs individually:

   | Bug ID | Test(s) That Verify It | Status |
   |--------|------------------------|--------|
   | B1 | test_create_user_returns_201 | PASS / FAIL |
   | B2 | test_create_user_rejects_invalid_email, test_create_user_rejects_missing_at_symbol | PASS / FAIL |
   | B3 | test_list_items_empty_description_param_returns_all | PASS / FAIL |
   | B4 | test_get_nonexistent_item_returns_404 | PASS / FAIL |
   | B5 | test_price_rounded_to_two_decimal_places, test_price_rounding_preserves_cents | PASS / FAIL |
   | B6 | (static analysis  -  no direct pytest coverage) | VERIFIED / UNVERIFIED |

5. Record the following metrics for Phase 10:
   - `tests_after`: total test count
   - `test_failures_after`: count of FAILED tests (target: 0)
   - `lint_issues_after`: count of flake8 issues

6. Produce a **Quality Gate Summary**:

   | Check | Before | After | Result |
   |-------|--------|-------|--------|
   | Test failures | N | 0 | PASS |
   | Lint issues | N | N | PASS/FAIL |
   | New issues introduced | - | 0 | PASS |

7. **APPROVAL GATE 7:**
   Use `ask_followup_question` with:
   - Question: "Phase 7 complete. Quality gate results are shown above.
     Proceed to code review?"
   - Option A: "Proceed to code review"
   - Option B: "Abort and investigate remaining issues"

   **Do not continue to Phase 8 until the developer selects Option A.**

---

## Phase 8  -  Code Review

**Goal:** Switch to the CodeReview mode, which independently reviews the
changes and writes structured findings to `reports/code_review_findings.md`.
Then return to DebugFlow mode and present the findings for approval.

**Steps:**

1. Use `switch_mode` to switch to the `code-review` mode.

2. In CodeReview mode, the agent will:
   - Read every file modified during Phase 5.
   - Assess correctness, maintainability, security, error handling, test
     coverage, and regression risk.
   - Classify every finding as CRITICAL, WARNING, or POSITIVE.
   - Write the full structured findings to `reports/code_review_findings.md`
     following the template defined in Sub-Task 5.

3. After CodeReview mode has written `reports/code_review_findings.md`,
   use `switch_mode` to return to the `debug-flow` mode.

4. Use `read_file` to read `reports/code_review_findings.md` in full.

5. Summarise the key findings for the developer:
   - Count of CRITICAL findings (must be 0 to proceed safely)
   - Count of WARNING findings
   - Count of POSITIVE findings
   - Overall Verdict from the report

6. **APPROVAL GATE 8:**
   Use `ask_followup_question` with:
   - Question: "Phase 8 complete. Code review findings are summarised above.
     Approve and generate the final report?"
   - Option A: "Approve and generate final report"
   - Option B: "Abort workflow"

   **Do not continue to Phase 9 until the developer selects Option A.**

---

## Phase 9  -  Debugging Report

**Goal:** Write a complete, human-readable debugging report to
`reports/debug_report.md` by assembling all findings gathered across every
prior phase.

**Steps:**

1. Use `read_file` to re-read `reports/code_review_findings.md` to ensure
   the code review section is accurate.

2. Use `write_file` to write `reports/debug_report.md`. The file must
   follow this exact section structure:

   ```
   # Bob DebugFlow  -  Debugging Report

   ## 1. Problem Statement
   Brief description of the repository and purpose of this debugging session.

   ## 2. Initial Baseline (Phase 2)
   - Test suite results before fixes: N passed, N failed
   - Lint issues before fixes: N
   - Coverage before fixes: N%

   ## 3. Bug Inventory
   Table: Bug ID | File | Line | Bug Type | Symptom

   ## 4. Root-Cause Analysis (Phase 3)
   For each bug: Bug ID, root cause explanation, evidence (test name + line).

   ## 5. Investigation Evidence (Phase 4)
   Consolidated findings table from both subagents.
   Note any discrepancies between Phase 3 and Phase 4.

   ## 6. Fixes Applied (Phase 5)
   Fix Application Log: Bug ID | File | Line Changed | Description.

   ## 7. Test Results Before and After (Phases 2 and 6)
   Side-by-side comparison table.

   ## 8. Verification Results (Phase 7)
   Quality Gate Summary table from Phase 7.
   Per-bug verification status table from Phase 7.

   ## 9. Code Review Findings (Phase 8)
   Full content of reports/code_review_findings.md incorporated here.

   ## 10. Remaining Limitations
   Any bugs not fully addressed, edge cases not covered by tests,
   or WARNING/CRITICAL findings from code review that were not resolved.

   ## 11. Developer Approvals
   Record of each approval gate:
   Gate 4: [Approved / Aborted] by developer
   Gate 5: [Approved / Aborted] by developer
   Gate 7: [Approved / Aborted] by developer
   Gate 8: [Approved / Aborted] by developer
   ```

3. Do not truncate any section. Every section header must be present even
   if its content is brief.

**No approval gate. Continue automatically to Phase 10.**

---

## Phase 10  -  Productivity Measurement

**Goal:** Write a structured JSON metrics file capturing the measurable
before/after impact of the DebugFlow session.

**Steps:**

1. Assemble all numeric metrics collected across phases 2, 6, 7, and 9.

2. Use `write_file` to write `reports/metrics.json` following this exact
   schema (populate every field with real values from this session):

   ```json
   {
     "session": {
       "timestamp": "<ISO-8601 datetime>",
       "repository": "Bob-DebugFlow",
       "workflow_version": "1.0.0"
     },
     "bugs": {
       "bugs_seeded": 6,
       "bugs_identified": <count of bugs found in Phase 2/3>,
       "bugs_fixed": <count of bugs resolved in Phase 5 and verified in Phase 7>
     },
     "tests": {
       "tests_before": <total test count from Phase 2>,
       "tests_after": <total test count from Phase 6>,
       "test_failures_before": <failed count from Phase 2>,
       "test_failures_after": <failed count from Phase 7>
     },
     "coverage": {
       "coverage_before_pct": <coverage % from Phase 2 baseline, or null if not captured>,
       "coverage_after_pct": <coverage % from Phase 6>
     },
     "lint": {
       "lint_issues_before": <flake8 issue count from Phase 2>,
       "lint_issues_after": <flake8 issue count from Phase 7>
     },
     "workflow": {
       "phases_completed": <number of phases completed, e.g. 10>,
       "approval_gates_triggered": 4,
       "approval_gates_approved": <count of gates where developer chose Proceed>,
       "approval_gates_aborted": <count of gates where developer chose Abort>
     },
     "productivity": {
       "debugging_steps": <total number of distinct investigation + fix actions taken>,
       "estimated_manual_debug_time_minutes": <reasonable estimate for a developer doing this manually>,
       "debugflow_time_minutes": <approximate elapsed time for this session>,
       "estimated_time_saved_minutes": <estimated_manual - debugflow>
     },
     "code_review": {
       "critical_findings": <count from Phase 8>,
       "warning_findings": <count from Phase 8>,
       "positive_findings": <count from Phase 8>,
       "overall_verdict": "<APPROVED | APPROVED WITH WARNINGS | REQUIRES CHANGES>"
     }
   }
   ```

3. Do not use placeholder values. Every field must be populated with real
   data from this session. If a metric was not measurable (e.g. coverage
   before fixes was not captured), set it to `null`.

4. After writing `reports/metrics.json`, present a final **Session Summary**
   to the developer in chat:
   - Bugs identified and fixed
   - Test pass rate before vs after
   - Coverage delta
   - Lint issues delta
   - Estimated time saved
   - Code review verdict

**No approval gate. The DebugFlow session is now complete.**

---

## Quick Reference  -  Bob Tool Usage by Phase

| Phase | Bob Capabilities Used |
|-------|-----------------------|
| 1  -  Codebase Understanding | `list_files`, `GetSymbolsOverview`, `read_file`, `grep` |
| 2  -  Bug Detection | `execute_command` (pytest, flake8) |
| 3  -  Root-Cause Analysis | `FindSymbol`, `FindReferencingSymbols`, `read_file` |
| 4  -  Parallel Investigation | `spawn_subagent` (x2 parallel), `ask_followup_question` |
| 5  -  Fix Implementation | `apply_diff`, `search_and_replace`, `ask_followup_question` |
| 6  -  Automated Testing | `execute_command` (pytest --cov) |
| 7  -  Verification | `execute_command` (pytest, flake8), `ask_followup_question` |
| 8  -  Code Review | `switch_mode` (CodeReview), `read_file`, `ask_followup_question` |
| 9  -  Debugging Report | `read_file`, `write_file` |
| 10  -  Productivity Measurement | `write_file` |
