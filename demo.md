# Bob DebugFlow  -  Hackathon Demo Script

> **Audience:** Hackathon judges and technical observers  
> **Duration:** ~10-15 minutes  
> **Setup:** Bob IDE open, `Bob-DebugFlow` workspace loaded, DebugFlow mode available

---

## Step 1  -  Opening Problem Statement

**Show on screen:** The `README.md` problem section.

**Say:**
> "Every developer knows this workflow: a bug is reported, you read the code, run the tests, trace the root cause, apply a fix, verify it, and write up what happened. For even a small codebase this takes 30 to 60 minutes of careful manual work  -  context-switching between tools, tracking findings in your head, and hoping you don't introduce a regression.
>
> Bob DebugFlow asks: what if an AI agent could drive that entire process for you  -  structured, transparent, and with you in control at every critical decision?"

---

## Step 2  -  Show the Intentionally Buggy Project

**Show on screen:** The project file tree in Bob IDE. Open `app/routes/users.py` briefly, then `app/utils.py`.

**Say:**
> "This is a small but realistic FastAPI REST API. It manages users and items against a SQLite database. The code looks reasonable at a glance  -  but it contains six intentional, realistic bugs seeded across the route layer, the utility layer, and the database layer.
>
> The bugs cover: wrong HTTP status codes, missing input validation, a nullable-field handling issue, an unhandled exception, a floating-point arithmetic error, and a database resource leak. Some of these you'd only find with careful testing and code inspection."

---

## Step 3  -  Show Baseline pytest and flake8 Results

**Show on screen:** Run in the Bob terminal:
```
python -m pytest tests/ -v --tb=short
```
Then:
```
python -m flake8 app/ tests/
```

**Expected output:**
```
7 failed, 10 passed

tests/test_users.py:15:1: F401 'pytest' imported but unused
```

**Say:**
> "Seven tests failing, ten passing. One lint issue. These failures are intentional  -  each one maps to a seeded bug. The test suite is written against the correct expected behaviour, so it fails on the buggy code and will pass once the bugs are fixed.
>
> This is our baseline. Everything Bob measures will be compared against these numbers."

---

## Step 4  -  Activate DebugFlow Mode

**Show on screen:** Open the Bob mode picker. Select **DebugFlow**.

**Say:**
> "This is where IBM Bob comes in. DebugFlow is a custom Bob mode  -  not a generic chat prompt, but a purpose-built orchestration persona with a 10-phase debugging workflow encoded in a skill file. It has exactly the tool permissions it needs: read, edit, execute commands, spawn subagents, and switch modes. Nothing more.
>
> I'll type the trigger phrase to start the session."

**Type in Bob:**
```
Start the DebugFlow debugging workflow.
```

---

## Step 5  -  Phase 1: Codebase Understanding

**Show on screen:** Bob executing `list_files`, `GetSymbolsOverview`, and `read_file` calls. Watch the Architecture Summary appear in the chat.

**Say:**
> "Phase 1  -  Bob reads the entire repository before touching anything. It maps every file, reads every module, traces the call relationships between route handlers, models, utilities, and the database session. It produces an architecture summary and only then moves to bug detection.
>
> This is the same thing a developer does when they first pick up an unfamiliar codebase  -  but Bob does it in seconds and retains the full context for every subsequent phase."

**Evidence:** Architecture Summary table in Bob chat output.

---

## Step 6  -  Phase 2: Bug Detection

**Show on screen:** Bob running `pytest` and `flake8` via `execute_command`. Watch the numbered Bug Detection Summary appear.

**Say:**
> "Phase 2  -  Bob runs the real test suite and the real linter. It doesn't guess at bugs. It captures every failing test, every assertion message, and every lint violation, and formats them as a structured bug list that it will trace in the next phase.
>
> Notice Bob also records the baseline metrics  -  total tests, failure count, lint issues  -  which it will use later for the productivity report."

**Evidence:** Bug Detection Summary table (7 items) in Bob chat output.

---

## Step 7  -  Phase 3: Root-Cause Analysis

**Show on screen:** Bob using `FindSymbol`, `FindReferencingSymbols`, and `read_file` to trace each failure. Watch the Root-Cause Analysis table build up.

**Say:**
> "Phase 3  -  for each symptom, Bob traces it to the exact root cause. It distinguishes between what the test observed  -  the symptom  -  and why the code is wrong  -  the root cause.
>
> For example: a test expecting status 201 but receiving 200 is the symptom. The missing `status_code=201` argument on the route decorator is the root cause. Bob reads the actual source, cites the exact file and line, and records the evidence before proposing anything."

**Evidence:** Root-Cause Analysis table with Bug ID, file, line, root cause, and correct behaviour for each of the 6 bugs.

---

## Step 8  -  Phase 4: Parallel Subagent Investigation

**Show on screen:** Bob invoking `spawn_subagent` twice. Show both subagent results returning and being merged.

**Say:**
> "Phase 4  -  this is where Bob's multi-agent capability comes in. It groups the bugs into two clusters: route-layer bugs in `users.py` and `items.py`, and utility and database bugs in `utils.py` and `database.py`. It then spawns two independent subagents simultaneously  -  one per cluster  -  each reading its assigned files and verifying the root causes independently.
>
> The findings come back in parallel. Bob merges them into a single consolidated table, flags any discrepancies between its Phase 3 analysis and the subagent findings, and prepares to present them to you."

**Evidence:** Two subagent calls in the Bob tool log. Consolidated Investigation Findings table in chat.

---

## Step 9  -  Approval Gate 4

**Show on screen:** Bob's `ask_followup_question` dialog with two options.

**Say:**
> "This is Approval Gate 4  -  the first of four hard stops in the workflow. Bob will not proceed to fix anything without your explicit sign-off. It presents the consolidated investigation findings and asks: proceed to fix implementation, or abort?
>
> You are reviewing what Bob found, not rubber-stamping an action it already took. The fixes have not been applied yet."

**Action:** Select **"Proceed to fix implementation"**.

---

## Step 10  -  Phase 5: Proposed Fixes

**Show on screen:** Bob presenting the Proposed Fix Summary  -  one block per bug showing the before/after lines and a one-sentence rationale.

**Say:**
> "Phase 5  -  Bob plans every fix in detail before applying a single character. For each bug it shows you: the exact current line, the exact replacement line, and why the change is correct. No speculation, no rewrites, no cleanup of unrelated code.
>
> You are looking at six precise, minimal changes  -  nothing more."

**Evidence:** Proposed Fix Summary in Bob chat, showing exactly 6 fix blocks.

---

## Step 11  -  Approval Gate 5

**Show on screen:** Bob's approval gate dialog for fixes.

**Say:**
> "Approval Gate 5. Bob is asking permission to apply the fixes it just described. If you chose Abort here, no files would be touched. The workflow stops cleanly.
>
> This is controlled AI-assisted development  -  every consequential action requires your consent."

**Action:** Select **"Approve and apply all fixes"**.

**Show on screen:** Bob applying fixes one by one using `apply_diff` and `search_and_replace`. Watch the Fix Application Log appear.

---

## Step 12  -  Phase 6 and 7: Testing and Verification

**Show on screen:** Bob running `pytest --cov` and then `flake8` again. Watch the Test Results Summary and Quality Gate Summary appear.

**Say:**
> "Phase 6  -  Bob runs the full test suite with coverage. Phase 7  -  it runs both pytest and flake8 again, and compares the results to the Phase 2 baseline. It verifies each of the six bugs individually by mapping each test to its corresponding bug ID.
>
> The quality gate is not just 'did the tests pass'  -  it also checks that the fixes did not introduce any new lint issues."

**Expected output:**
```
17 passed, 0 failed
```

**Evidence:** Test Results Summary table (before: 7 failed / after: 0 failed). Quality Gate Summary table (all checks PASS).

---

## Step 13  -  Approval Gate 7

**Show on screen:** Bob's approval gate dialog presenting the quality gate summary.

**Say:**
> "Gate 7  -  Bob presents the full quality gate result. Zero test failures, no new lint issues, all six bugs verified. Your call to proceed to code review."

**Action:** Select **"Proceed to code review"**.

---

## Step 14  -  Phase 8: CodeReview Mode

**Show on screen:** Bob using `switch_mode` to transition to **CodeReview** mode. Show CodeReview reading the changed files and writing `reports/code_review_findings.md`. Then show Bob switching back to DebugFlow.

**Say:**
> "Phase 8  -  Bob switches to a completely separate CodeReview mode. This mode has constrained permissions: it can only read files and write to `reports/code_review_findings.md`. It cannot run commands, cannot modify source code, cannot touch tests.
>
> It reviews every changed file across six dimensions: correctness, maintainability, security, error handling, test coverage, and regression risk. It classifies every finding as CRITICAL, WARNING, or POSITIVE, and writes a structured report. Then it switches back to DebugFlow."

**Evidence:** `reports/code_review_findings.md` created. Bob displays a summary of CRITICAL / WARNING / POSITIVE counts and the Overall Verdict.

---

## Step 15  -  Approval Gate 8

**Show on screen:** Bob's approval gate dialog with the code review summary.

**Say:**
> "Gate 8  -  final checkpoint. Bob summarises the code review findings and asks for your approval to generate the final report. If CodeReview flagged any CRITICAL issues, you'd want to investigate before signing off."

**Action:** Select **"Approve and generate final report"**.

---

## Step 16  -  Phase 9: Debugging Report

**Show on screen:** Open `reports/debug_report.md` in the editor. Scroll through the sections.

**Say:**
> "Phase 9  -  Bob assembles the complete debugging report. It pulls together everything from all prior phases: the architecture summary, the bug inventory, the root-cause analysis, the investigation evidence from both subagents, every fix applied, the test results before and after, the verification results, and the full code review findings.
>
> This is a document you could hand to a team lead, a reviewer, or store in your incident log. Bob wrote it. You approved the content at every gate."

**Evidence:** `reports/debug_report.md` with 11 fully populated sections.

---

## Step 17  -  Phase 10: Metrics JSON

**Show on screen:** Open `reports/metrics.json` in the editor.

**Say:**
> "Phase 10  -  Bob writes the structured metrics file. Every number came from a real tool execution during this session  -  not estimated, not fabricated."

**Highlight key fields:**
```json
"test_failures_before": 7,
"test_failures_after": 0,
"bugs_identified": 6,
"bugs_fixed": 6,
"estimated_time_saved_minutes": ...
```

---

## Step 18  -  Measurable Productivity Impact

**Show on screen:** The metrics.json productivity section side by side with the demo.md impact table.

**Say:**
> "Here is what this session measured:
>
> - 6 bugs identified, 6 bugs fixed
> - 7 test failures reduced to 0
> - Test coverage increased
> - Lint issues reduced
> - Code reviewed across 5 files, across 6 quality dimensions
> - 4 approval gates  -  developer in control at every critical decision
>
> The estimated manual debugging time for this task is 30 to 60 minutes. Bob completed the structured workflow  -  including parallel investigation, automated testing, code review, and full reporting  -  in a fraction of that time.
>
> The key point is not just speed. It is that the result is reproducible, documented, and auditable. Every finding is traceable to a test or a code line. Every fix was approved. Every step is in the report."

---

## Step 19  -  Closing Statement

**Show on screen:** Return to the `README.md` hackathon relevance section.

**Say:**
> "Bob DebugFlow is not a chatbot that helps you debug. It is an orchestrated, agentic debugging workflow  -  driven by a custom mode, guided by a structured skill, powered by real tool execution, and kept under developer control through approval gates.
>
> It demonstrates that IBM Bob 2.0 is not just a coding assistant. It is a workflow engine. And when you combine custom modes, parallel subagents, controlled permissions, and structured reporting, you get something that genuinely changes how developers work.
>
> Thank you."

---

## Demo Checklist

Use this before the presentation to confirm the environment is ready:

- [ ] Workspace `Bob-DebugFlow` is open in Bob IDE
- [ ] DebugFlow mode appears in the mode picker
- [ ] CodeReview mode appears in the mode picker
- [ ] `python -m pytest tests/ -v --tb=short` shows `7 failed, 10 passed`
- [ ] `python -m flake8 app/ tests/` shows `1 issue`
- [ ] `reports/` directory exists but all three report files are empty stubs
- [ ] `bob_sessions/` directory exists for screenshot storage
- [ ] Screen recording or screenshot tool is ready
