# Major Refactor Mode - Execution Plan

> **Created**: 2026-01-03
> **Status**: Ready for execution
> **Philosophy**: See `PHILOSOPHY.md` - read it first!
> **Decisions**: See `DECISIONS.md` - already settled, don't re-litigate

---

## Standard Session Format

Every session prompt follows this structure:

```
┌─────────────────────────────────────────────────────────────┐
│ SESSION HEADER                                              │
├─────────────────────────────────────────────────────────────┤
│ Worktree: YES/NO (and why)                                  │
│ Scope: What's IN and OUT of scope                           │
│ Start When: Prerequisites that must be true                 │
│ Stop When: How you know you're done                         │
├─────────────────────────────────────────────────────────────┤
│ PROMPT                                                      │
│ The actual instructions for Claude                          │
├─────────────────────────────────────────────────────────────┤
│ ASK USER IF...                                              │
│ Specific situations where you should pause and ask          │
├─────────────────────────────────────────────────────────────┤
│ EXIT CRITERIA                                               │
│ Checkboxes - all must be checked before session is done     │
├─────────────────────────────────────────────────────────────┤
│ GIT INSTRUCTIONS                                            │
│ What to commit, when, commit message format                 │
├─────────────────────────────────────────────────────────────┤
│ HANDOFF                                                     │
│ What to write for the next session                          │
└─────────────────────────────────────────────────────────────┘
```

### Worktree Rules

| Situation | Use Worktree? | Why |
|-----------|---------------|-----|
| Modifying Forge Python code | NO | Direct changes to main, commit after each session |
| Modifying Forge Swift code | NO | Same - direct to main |
| Testing a risky change | YES | Isolate until verified |
| Parallel phase work (future) | YES | Multiple features simultaneously |

**For this refactor**: NO worktrees needed. All sessions work directly on main branch.

### Git Instructions (For Non-Devs)

After completing a session, Claude should:
1. **Stage changes**: `git add <files>`
2. **Commit with message**:
   ```
   feat(refactor): Session X.Y - <brief description>

   - What was done
   - What was done
   ```
3. **Push**: `git push` (optional - ask user)

**Never**: Force push, rebase, or do anything destructive.

### Handoff Protocol

At session end, update EXECUTION_PLAN.md with:

```markdown
### Session X.Y: Title (DATE)
**Status**: DONE

**Completed**:
- [x] Thing that was done
- [x] Another thing

**Not Completed** (if any):
- [ ] Thing that wasn't done
- Reason: why

**Discoveries**:
- Anything unexpected found

**For Next Session**:
- Key context the next session needs
- Files to look at first
- Any decisions that were made

**Files Modified**:
- `path/to/file` - what changed
```

---

## Session Map

```
PHASE 0: PLANNING AGENT (MOST CRITICAL - Build first!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session 0.1
 [PENDING]    ← START HERE

PHASE 1: FOUNDATION (Sequential)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session 1.1 → Session 1.2
 [PENDING]    [PENDING]

PHASE 2: DETECTION & ANALYSIS (Sequential)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session 2.1 → Session 2.2
 [PENDING]    [PENDING]

PHASE 3: ORCHESTRATOR (Sequential)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session 3.1
 [PENDING]

PHASE 4: AGENTS (Can parallelize)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session 4.1  ∥  Session 4.2
 [PENDING]      [PENDING]

PHASE 5: UI DASHBOARD (Sequential)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session 5.1 → Session 5.2
 [PENDING]    [PENDING]

PHASE 6: INTEGRATION (Sequential)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session 6.1
 [PENDING]
```

---

## Bootstrap Strategy

- **Phase 0**: Planning Agent creates all the docs (most critical!)
- **Phase 1-2**: Build normally in regular Claude Code sessions
- **Phase 3-6**: Use the doc structure with **you as manual orchestrator**
- Once Phase 3-4 work, the orchestrator agent can take over

---

## Phase 0: Planning Agent (MOST CRITICAL)

> **This phase REPLACES brainstorm/refine for major refactors.**
> When detection triggers, instead of generating a spec, we launch a Planning Agent.
> This is what WE JUST DID in this conversation - now we formalize it.

---

### Session 0.1: Planning Agent Implementation

| | |
|---|---|
| **Worktree** | NO - Direct to main branch |
| **Scope** | IN: Planning Agent that runs interactive planning conversation. OUT: Execution agents |
| **Start When** | This is the FIRST thing to build |
| **Stop When** | Planning Agent can explore codebase, ask questions, and output complete docs |

---

**PROMPT** (copy this into Claude Code):

```
Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md - this is what you'll be helping users create.

The Planning Agent is the MOST CRITICAL component. It replaces brainstorm/refine
for major refactors. When Claude detects a major refactor, instead of generating
a spec, we launch a Planning Agent session.

Implement the Planning Agent:

1. Create forge/refactor/planning_agent.py with PlanningAgent class:
   - launch(project_path, goal) - Opens Warp with planning session
   - generate_claude_md() - Creates session-specific CLAUDE.md with PLANNING_PROMPT
   - write_docs(refactor_id) - Writes all generated docs

2. Create PLANNING_PROMPT in forge/refactor/prompts.py (see below)

3. Add CLI: forge refactor plan {project} --goal "description"
   - Launches Planning Agent in Warp
   - Agent has the PLANNING_PROMPT as its system context
   - Agent explores codebase, asks user questions, debates, documents

4. The Planning Agent conversation should:
   a. Explore codebase first (understand what exists)
   b. Ask clarifying questions (2-4 key questions)
   c. Propose approach, debate alternatives
   d. Build PHILOSOPHY.md together (show user, get feedback)
   e. Build DECISIONS.md (what we decided, what we rejected)
   f. Create EXECUTION.md with phased sessions
   g. Write all docs when user approves

5. Output all docs to: .forge/refactors/{id}/
```

---

**PLANNING_PROMPT** (add to forge/refactor/prompts.py):

```python
PLANNING_PROMPT = '''
# You are a Planning Agent for Major Refactors

Project: {project_name}
Goal: {goal_description}

## Your Mission

Through conversation with the user, create a complete refactor plan:
1. PHILOSOPHY.md - Guiding principles, anti-patterns, what NOT to do
2. VISION.md - Target state, success criteria
3. DECISIONS.md - Architectural choices with rationale + rejected alternatives
4. PRE_REFACTOR.md - Codebase analysis relevant to the goal
5. EXECUTION.md - Phased sessions with standardized format

## How to Work

### 1. EXPLORE FIRST (before proposing anything)
- Read the codebase extensively
- Understand current architecture
- Find existing patterns
- Identify what we're changing

### 2. ASK QUESTIONS (clarify intent)
- What problem are we solving?
- What are the constraints?
- What's explicitly out of scope?
- What approaches have been considered?

### 3. DEBATE ALTERNATIVES (don't just accept first idea)
- Present 2-3 options for key decisions
- Discuss tradeoffs
- Document what was REJECTED and why

### 4. BUILD PHILOSOPHY (establish principles)
- What should we NEVER do?
- What anti-patterns to avoid?
- What makes this refactor "done"?

### 5. PLAN PHASES (break into sessions)
- Each session = ~1 Claude Code context window of work
- Clear scope, start/stop conditions
- Identify parallel vs sequential
- Use the standardized session format from EXECUTION_PLAN.md

### 6. WRITE DOCS (when ready)
- Show each doc to user before writing
- Get explicit approval
- Write to .forge/refactors/{id}/

## Conversation Flow

START: "I'll help you plan this refactor. Let me first explore the codebase
to understand what we're working with..."

1. Explore codebase (search, read key files)
2. Summarize what you found
3. Ask 2-4 clarifying questions
4. Propose high-level approach
5. Debate and refine together
6. Draft PHILOSOPHY.md → show → get feedback
7. Draft DECISIONS.md → show → get feedback
8. Plan phases in EXECUTION.md
9. Write all docs when approved

END: "Planning complete! Docs are in .forge/refactors/{id}/.
Ready to start execution when you are."

## Key Principles

- EXPLORE before proposing (understand what exists)
- ASK before assuming (clarify intent)
- DEBATE alternatives (document rejections)
- SCOPE clearly (in/out)
- BE CONVERSATIONAL (this is collaborative planning)
'''
```

---

**ASK USER IF...**

- The conversation flow feels right
- Too many or too few questions
- Missing any doc types

---

**EXIT CRITERIA**

- [ ] `forge refactor plan {project} --goal "..."` launches Warp session
- [ ] Planning Agent explores codebase before proposing
- [ ] Agent asks clarifying questions
- [ ] Agent shows drafts for approval before writing
- [ ] All 5 docs generated (PHILOSOPHY, VISION, DECISIONS, PRE_REFACTOR, EXECUTION)
- [ ] EXECUTION.md uses the standardized session format

---

**GIT INSTRUCTIONS**

```bash
git add forge/refactor/planning_agent.py forge/refactor/prompts.py forge/cli.py
git commit -m "feat(refactor): Session 0.1 - Planning Agent

- Add PlanningAgent for interactive refactor planning
- Replaces brainstorm/refine for major refactors
- Explores codebase, asks questions, debates, documents
- Generates all planning docs via conversation
- MOST CRITICAL component of Major Refactor Mode"
```

---

**HANDOFF**

Phase 0 creates the docs that ALL other phases read.
Without Planning Agent, there are no docs.
Build this FIRST.

---

**Files to create:**
- `forge/refactor/planning_agent.py`

**Files to modify:**
- `forge/refactor/prompts.py` - Add PLANNING_PROMPT
- `forge/cli.py` - Add `forge refactor plan` command

---

## Phase 1: Foundation (Python Backend)

---

### Session 1.1: Core State & Signals

| | |
|---|---|
| **Worktree** | NO - Direct to main branch |
| **Scope** | IN: RefactorState dataclass, SessionState, signal file I/O. OUT: Session launcher (that's 1.2) |
| **Start When** | Fresh session, no prerequisites |
| **Stop When** | All exit criteria checked, code committed |

---

**PROMPT** (copy this into Claude Code):

```
Read these docs first:
- docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md (principles)
- docs/MAJOR_REFACTOR_MODE/DECISIONS.md (architecture decisions)

Note: forge/refactor/ already exists with planning_agent.py and prompts.py.
You're ADDING to this module, not creating it from scratch.

Implement the execution state infrastructure:

1. Create forge/refactor/state.py with these dataclasses:

   @dataclass
   class SessionState:
       """State for a single execution session."""
       session_id: str  # e.g., "1.1", "2.1"
       status: str  # "pending" | "in_progress" | "completed" | "needs_revision"
       started_at: Optional[str] = None
       completed_at: Optional[str] = None
       commit_hash: Optional[str] = None
       audit_result: Optional[str] = None  # "pending" | "passed" | "failed"
       notes: str = ""  # Handoff notes for next session

   @dataclass
   class RefactorState:
       """Runtime state for a refactor execution."""
       refactor_id: str
       status: str  # "planning" | "executing" | "paused" | "completed"
       current_session: Optional[str] = None  # e.g., "1.1"
       sessions: dict = field(default_factory=dict)  # session_id -> SessionState
       started_at: Optional[str] = None
       updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
       completed_at: Optional[str] = None

   Include:
   - to_dict() and from_dict() methods (follow registry.py patterns)
   - save(path) and load(path) class methods
   - Location: .forge/refactors/{id}/state.json

2. Create forge/refactor/signals.py with:

   Signal types (use an Enum):
   - SESSION_STARTED: Agent began work on a session
   - SESSION_DONE: Agent finished work (includes commit_hash, summary)
   - AUDIT_PASSED: Audit agent approved the session
   - REVISION_NEEDED: Audit found issues (includes issues list)
   - QUESTION: Agent needs user input (includes question, options)
   - PAUSED: User paused the refactor

   Functions:
   - write_signal(signals_dir, signal_type, payload) -> Path
     - Atomic write (write to temp file, then rename)
     - Filename: {timestamp}_{signal_type}.json
   - read_signals(signals_dir) -> list[Signal]
     - Returns all signals, sorted by timestamp
   - clear_signals(signals_dir)
     - Archives old signals to signals/archive/

   Signal file format:
   {
     "type": "SESSION_DONE",
     "session_id": "1.1",
     "timestamp": "2026-01-03T14:30:00",
     "payload": {...}
   }

3. Update forge/refactor/__init__.py to export the new classes.

After implementing, show a quick demo:
- Create a RefactorState with two sessions
- Save to JSON, load it back
- Write a SESSION_DONE signal
- Read signals back
```

---

**ASK USER IF...**

- The state structure looks right (show the dataclass first)
- Signal archiving behavior is correct
- You find patterns in registry.py that conflict

---

**EXIT CRITERIA**

- [ ] `forge/refactor/state.py` exists with RefactorState and SessionState
- [ ] `forge/refactor/signals.py` exists with SignalType enum and read/write functions
- [ ] State can be saved to JSON and loaded back
- [ ] Signals can be written atomically and read back
- [ ] Signal files use timestamp prefix for ordering
- [ ] Code follows existing Forge patterns (see registry.py)

---

**GIT INSTRUCTIONS**

When done, commit:
```bash
git add forge/refactor/state.py forge/refactor/signals.py forge/refactor/__init__.py
git commit -m "feat(refactor): Session 1.1 - Core state and signal infrastructure

- Add RefactorState and SessionState dataclasses
- Add atomic signal file read/write with SignalType enum
- Foundation for multi-session refactor execution"
```

Ask user: "Ready to push to remote?" (only push if they say yes)

---

**HANDOFF**

Session 1.2 will use this infrastructure to:
- Load RefactorState to know current position
- Update state when launching a session
- Write SESSION_STARTED signal

Key files: state.py (RefactorState, SessionState), signals.py (SignalType, write_signal, read_signals)

---

**Files to create:**
- `forge/refactor/state.py`
- `forge/refactor/signals.py`

**Files to modify:**
- `forge/refactor/__init__.py`

---

### Session 1.2: Execution Session Launcher

| | |
|---|---|
| **Worktree** | NO - Direct to main branch |
| **Scope** | IN: Session launcher that starts execution sessions. OUT: Orchestrator logic (that's Phase 3) |
| **Start When** | Session 1.1 is DONE (state.py and signals.py exist) |
| **Stop When** | Can run `forge refactor start {id} {session}` and see Claude session launch |

---

**PROMPT** (copy this into Claude Code):

```
Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md first.

Check that Session 1.1 is complete:
- forge/refactor/state.py should exist with RefactorState, SessionState
- forge/refactor/signals.py should exist with write_signal, read_signals

Note: CLI commands already exist (forge refactor plan/list/status/resume).
You're adding the execution launcher, not recreating existing commands.

Implement the execution session launcher:

1. Create forge/refactor/session.py with ExecutionSession class:

   class ExecutionSession:
       def __init__(self, refactor_id: str, session_id: str, project_root: Path):
           ...

       def load_session_spec(self) -> dict:
           """Load session spec from EXECUTION.md or phases/{session_id}/spec.md"""
           - Parse the session's PROMPT, EXIT CRITERIA, etc.
           - Return structured dict

       def generate_execution_claude_md(self) -> str:
           """Generate CLAUDE.md for this execution session."""
           Include:
           - "Read PHILOSOPHY.md and DECISIONS.md first"
           - The session PROMPT from spec
           - EXIT CRITERIA as checklist
           - GIT INSTRUCTIONS
           - "When done, run: forge refactor done {session_id}"

       def launch(self) -> tuple[bool, str]:
           """Launch the session in Warp."""
           - Load RefactorState
           - Validate session can start (check prerequisites)
           - Update state: current_session, status = executing
           - Write SESSION_STARTED signal
           - Generate CLAUDE.md to .forge/refactors/{id}/sessions/{session_id}/CLAUDE.md
           - Open Warp with claude command
           - Return (success, message)

2. Add CLI commands to forge/cli.py:

   forge refactor start {refactor-id} {session-id}
     - Creates ExecutionSession and calls launch()
     - Prints status and instructions

   forge refactor done {session-id}
     - Marks session complete in RefactorState
     - Writes SESSION_DONE signal with commit hash
     - Updates EXECUTION.md session log
     - Prints "Ready for audit" or next session info

3. Test flow:
   - Create a test refactor with `forge refactor plan "Test" --goal "test"`
   - Add a simple session spec to EXECUTION.md
   - Run `forge refactor start test 1.1`
   - Verify Warp opens with proper CLAUDE.md
   - Run `forge refactor done 1.1`
   - Verify state updated and signal written
```

---

**ASK USER IF...**

- The session CLAUDE.md content looks right (show a preview)
- Session spec parsing from EXECUTION.md is unclear
- You need to create phases/{session_id}/ directory structure

---

**EXIT CRITERIA**

- [ ] `forge/refactor/session.py` exists with ExecutionSession class
- [ ] `forge refactor start {id} {session}` launches Warp with Claude
- [ ] Generated CLAUDE.md includes PHILOSOPHY.md reference and session prompt
- [ ] RefactorState is updated when session starts
- [ ] SESSION_STARTED signal is written
- [ ] `forge refactor done {session}` updates state and writes SESSION_DONE signal

---

**GIT INSTRUCTIONS**

When done, commit:
```bash
git add forge/refactor/session.py forge/cli.py
git commit -m "feat(refactor): Session 1.2 - Execution session launcher

- Add ExecutionSession class for launching execution sessions
- Add forge refactor start/done CLI commands
- Generates session-specific CLAUDE.md with prompts
- Updates RefactorState and writes signals on start/done"
```

Ask user: "Ready to push?"

---

**HANDOFF**

Phase 1 Foundation is complete! The orchestrator (Phase 3) will use:
- ExecutionSession.launch() to start sessions
- RefactorState to track progress
- Signals to know when sessions complete

Key insight: The orchestrator doesn't run the sessions - it coordinates them.
Sessions are independent Claude Code instances that communicate via signals.

---

**Files to create:**
- `forge/refactor/session.py`

**Files to modify:**
- `forge/cli.py` - Add start/done commands

---

## Phase 2: Detection & Codebase Analysis

---

### Session 2.1: Complexity Detection

| | |
|---|---|
| **Worktree** | NO - Direct to main branch |
| **Scope** | IN: Detection logic in Python, prompt updates. OUT: Swift UI (that's 5.2) |
| **Start When** | Phase 1 complete (can run `forge refactor init`) |
| **Stop When** | BrainstormAgent can detect and recommend Major Refactor Mode |

---

**PROMPT** (copy this into Claude Code):

```
Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md - especially the AGI-pilled vision.
Key principle: Let Claude decide when something is too big. No hardcoded thresholds.

Add complexity detection to BrainstormAgent:

1. Modify forge/agents/prompts.py - Add to REFINE_SYSTEM_PROMPT:

   "If the user's request is a major architectural change that would take
   multiple implementation sessions (not just one focused task), you should
   recommend Major Refactor Mode. Output:

   MAJOR_REFACTOR_RECOMMENDED

   This looks like a major architectural change. I'd recommend breaking it
   into multiple phases for safer implementation.

   **Affected Areas:**
   - [area 1]
   - [area 2]

   **Estimated Phases:** [number]

   Would you like to switch to Major Refactor Mode?"

2. The detection should be based on Claude's judgment, not rules like
   "if more than 5 files" - that's against our philosophy.

3. Test by starting a brainstorm and describing something big like
   "I want to completely restructure the data layer"

Don't modify Swift code yet - that's Session 5.2.
```

---

**ASK USER IF...**

- The prompt wording feels right (show it first)
- You're unsure what constitutes "major" (but err on the side of trusting Claude)
- The marker format should be different

---

**EXIT CRITERIA**

- [ ] REFINE_SYSTEM_PROMPT updated with detection guidance
- [ ] Tested: describe a major refactor, Claude outputs MAJOR_REFACTOR_RECOMMENDED
- [ ] Tested: describe a small feature, Claude does NOT trigger detection
- [ ] Detection is judgment-based, not rule-based

---

**GIT INSTRUCTIONS**

```bash
git add forge/agents/prompts.py forge/agents/brainstorm.py
git commit -m "feat(refactor): Session 2.1 - Major refactor detection

- Add complexity detection to BrainstormAgent
- Claude decides when to recommend Major Refactor Mode
- AGI-pilled: model judgment, not hardcoded rules"
```

---

**HANDOFF**

Note for Session 2.2:
- What the marker looks like
- How to parse it (if needed)
- Any edge cases discovered

---

**Files to modify:**
- `forge/agents/brainstorm.py`
- `forge/agents/prompts.py`

---

### Session 2.2: Codebase Analyzer

| | |
|---|---|
| **Worktree** | NO - Direct to main branch |
| **Scope** | IN: Analyzer that generates PRE_REFACTOR.md. OUT: Using it in UI flow |
| **Start When** | Session 2.1 complete (detection works) |
| **Stop When** | `forge refactor analyze` produces useful PRE_REFACTOR.md |

---

**PROMPT** (copy this into Claude Code):

```
Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md and DECISIONS.md.

Reference: Look at /Users/Brian/Projects/Active/AirFit/docs/MEMORY_PERSONA_PRE-REFACTOR_STATE.md
for an example of what good codebase analysis looks like.

Implement codebase analyzer:

1. Create forge/refactor/analyzer.py with CodebaseAnalyzer class

2. Analyzer should:
   - Take a project path and refactor goal as input
   - Scan file structure (respect .gitignore)
   - Identify key modules/components relevant to the goal
   - Note patterns used (architecture style, frameworks)
   - Summarize what exists before we change it

3. Output PRE_REFACTOR.md with sections:
   - Executive Summary
   - Current Architecture (relevant to goal)
   - Key Files (with purposes)
   - Patterns in Use
   - Known Gaps/Issues

4. Add CLI command:
   forge refactor analyze {id} --goal "description"

   This updates the refactor's PRE_REFACTOR.md

5. The analysis should be FOCUSED on the refactor goal, not a dump of
   the entire codebase. Quality over quantity.

Test on the Forge codebase itself with a sample goal.
```

---

**ASK USER IF...**

- The output format looks right (show a sample first)
- Analysis is too shallow or too deep
- Certain file types should be included/excluded

---

**EXIT CRITERIA**

- [ ] `forge/refactor/analyzer.py` exists with CodebaseAnalyzer class
- [ ] `forge refactor analyze test --goal "..."` produces PRE_REFACTOR.md
- [ ] Output is focused on the goal, not a codebase dump
- [ ] Output format matches AirFit example structure

---

**GIT INSTRUCTIONS**

```bash
git add forge/refactor/analyzer.py forge/cli.py
git commit -m "feat(refactor): Session 2.2 - Codebase analyzer

- Add CodebaseAnalyzer for PRE_REFACTOR.md generation
- Goal-focused analysis, not full codebase dump
- CLI: forge refactor analyze {id} --goal '...'"
```

---

**HANDOFF**

Note for Phase 3:
- How to invoke the analyzer
- What the output looks like
- Any improvements needed for quality

---

**Files to create:**
- `forge/refactor/analyzer.py`

**Files to modify:**
- `forge/cli.py` - Add analyze command

---

## Phase 3: Orchestrator Agent

---

### Session 3.1: Interactive Supervisor

| | |
|---|---|
| **Worktree** | NO - Direct to main branch |
| **Scope** | IN: Orchestrator that runs in Warp, handles signals. OUT: Phase/audit agents (Phase 4) |
| **Start When** | Phase 2 complete (detection + analyzer work) |
| **Stop When** | Can launch orchestrator in Warp and interact with it |

---

**PROMPT** (copy this into Claude Code):

```
Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md - especially the orchestrator section.
Key: Orchestrator is your INTERACTIVE TEAM LEAD, not a daemon.

Implement the Orchestrator Agent:

1. Create forge/refactor/orchestrator.py with:
   - OrchestratorSession class
   - read_state() - Load refactor state from files
   - check_signals() - Look for new signal files
   - handle_signal(signal) - Decide what to do
   - advance_phase() - Move to next phase

2. Create forge/refactor/prompts.py with ORCHESTRATOR_PROMPT:
   - Explain the orchestrator role (you are the team lead)
   - Reference PHILOSOPHY.md and DECISIONS.md from the refactor
   - Instructions for:
     - Checking signals when user asks "check status"
     - Advancing phases when audit passes
     - Asking user about parallelization
     - Modifying plan when user requests
   - Make it conversational and helpful

3. Add CLI: forge refactor orchestrate {id}
   - Generates a CLAUDE.md for the orchestrator session
   - Opens Warp with claude command pointing to refactor directory
   - The session should start with "I'm your orchestrator for [refactor].
     Current status: [phase]. What would you like to do?"

4. Test flow:
   - Run forge refactor orchestrate test
   - Warp opens with orchestrator session
   - Type "check status" - it reads state and reports
   - Type "I want to modify the plan" - it engages conversationally
```

---

**ASK USER IF...**

- The orchestrator personality feels right
- The Warp launch mechanism works (may need osascript on Mac)
- You're unsure how to generate the session-specific CLAUDE.md

---

**EXIT CRITERIA**

- [ ] `forge refactor orchestrate {id}` opens Warp with Claude session
- [ ] Orchestrator introduces itself and shows current status
- [ ] "check status" shows refactor state from files
- [ ] Can have a conversation about modifying the plan
- [ ] check_signals() can read signal files

---

**GIT INSTRUCTIONS**

```bash
git add forge/refactor/orchestrator.py forge/refactor/prompts.py forge/cli.py
git commit -m "feat(refactor): Session 3.1 - Interactive orchestrator agent

- Add OrchestratorSession for managing refactor state
- Add ORCHESTRATOR_PROMPT for Claude personality
- CLI: forge refactor orchestrate {id}
- Launches interactive supervisor in Warp"
```

---

**HANDOFF**

Note for Phase 4:
- How to launch orchestrator
- How signals are checked
- How the conversation model works

This is the "team lead" - Phase 4 agents will signal back to it.

---

**Files to create:**
- `forge/refactor/orchestrator.py`
- `forge/refactor/prompts.py`

**Files to modify:**
- `forge/cli.py` - Add orchestrate command

---

## Phase 4: Phase & Audit Agents

> **Note**: Sessions 4.1 and 4.2 can run in PARALLEL if you have bandwidth.
> They're independent - phase agents and audit agents don't depend on each other during development.

---

### Session 4.1: Phase Agent

| | |
|---|---|
| **Worktree** | NO for development. Phase agents CREATE worktrees when they run. |
| **Scope** | IN: Phase agent that runs in worktree, signals completion. OUT: Audit agent (4.2) |
| **Start When** | Phase 3 complete (orchestrator works) |
| **Stop When** | Can start a phase, have it run, and see the signal file created |

---

**PROMPT** (copy this into Claude Code):

```
Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md and DECISIONS.md.
Look at existing patterns in forge/worktree.py and forge/agents/executor.py.

Implement Phase Agent:

1. Create forge/refactor/phase_agent.py with PhaseAgent class:
   - __init__(refactor_id, phase_id)
   - prepare() - Create worktree for this phase
   - generate_prompt() - Build Claude prompt from phase spec
   - run() - Launch Claude Code session in worktree
   - complete() - Write output.md and signal phase_complete

2. Phase workflow:
   a. Read .forge/refactors/{id}/phases/{phase-id}/spec.md
   b. Create worktree at .forge-worktrees/refactor-{id}-phase-{phase-id}/
   c. Generate CLAUDE.md for the phase session
   d. Launch Warp with Claude Code in that worktree
   e. When Claude is done (user confirms), write output.md
   f. Write signal file: signals/phase-{id}.signal

3. Add CLI: forge refactor start-phase {refactor-id} {phase-id}
   - Creates worktree
   - Opens Warp with Claude session
   - Claude reads the phase spec and works

4. Use existing WorktreeManager from forge/worktree.py

Test: Create a dummy phase spec, run start-phase, verify worktree created.
```

---

**ASK USER IF...**

- The worktree naming convention is right
- You need help understanding existing worktree patterns
- The phase completion flow is unclear

---

**EXIT CRITERIA**

- [ ] `forge refactor start-phase {id} {phase}` creates worktree
- [ ] Warp opens with Claude session for the phase
- [ ] Phase spec is read and included in prompt
- [ ] After work, output.md can be written
- [ ] Signal file is created on completion

---

**GIT INSTRUCTIONS**

```bash
git add forge/refactor/phase_agent.py forge/cli.py
git commit -m "feat(refactor): Session 4.1 - Phase agent

- Add PhaseAgent for worktree-based phase execution
- Integrates with WorktreeManager
- CLI: forge refactor start-phase {id} {phase}
- Signals completion to orchestrator"
```

---

**HANDOFF**

Note for integration:
- How worktrees are named
- How signals are written
- How orchestrator should read these signals

---

**Files to create:**
- `forge/refactor/phase_agent.py`

**Files to modify:**
- `forge/cli.py` - Add start-phase command

---

### Session 4.2: Audit Agent

| | |
|---|---|
| **Worktree** | NO - Audit runs against phase worktrees, doesn't need its own |
| **Scope** | IN: Audit agent that validates against philosophy. OUT: Full iteration loop (comes with integration) |
| **Start When** | Phase 3 complete (can run in parallel with 4.1) |
| **Stop When** | Audit agent can read phase output and validate against philosophy |

---

**PROMPT** (copy this into Claude Code):

```
Read docs/MAJOR_REFACTOR_MODE/PHILOSOPHY.md - this is what audit validates against!
The audit agent is the GUARDIAN of idea fidelity. It prevents drift.

Implement Audit Agent:

1. Create forge/refactor/audit_agent.py with AuditAgent class:
   - __init__(refactor_id, group_id)
   - load_philosophy() - Read PHILOSOPHY.md from refactor
   - load_phase_outputs() - Read output.md from each phase in group
   - validate() - Check outputs against philosophy
   - report() - Write audit report and signal

2. Validation checks:
   - Does the work align with stated principles?
   - Are any anti-patterns present?
   - Does the implementation match the vision?
   - Are there concerning deviations?

3. Output:
   - If issues found:
     - Write audit-groups/{group}/iterations/{n}/issues.md
     - Signal audit_complete with passed=false and issues list
   - If passes:
     - Signal audit_complete with passed=true

4. Add CLI: forge refactor audit {refactor-id} {group-id}
   - Opens Warp with audit Claude session
   - Claude reads philosophy + phase outputs
   - Claude writes validation report

5. The audit prompt should make Claude:
   - Read PHILOSOPHY.md carefully
   - Compare each phase output against principles
   - Be specific about what doesn't align
   - Suggest how to fix issues

Test: Create dummy phase output, run audit, see if it catches misalignment.
```

---

**ASK USER IF...**

- The validation criteria are too strict or too loose
- You're unsure what "alignment with philosophy" means concretely
- The audit feedback format needs adjustment

---

**EXIT CRITERIA**

- [ ] `forge refactor audit {id} {group}` launches audit session
- [ ] Audit reads PHILOSOPHY.md and phase outputs
- [ ] Can detect when work doesn't align with principles
- [ ] Writes issues.md with specific feedback
- [ ] Signals audit_complete with pass/fail status

---

**GIT INSTRUCTIONS**

```bash
git add forge/refactor/audit_agent.py forge/cli.py
git commit -m "feat(refactor): Session 4.2 - Audit agent

- Add AuditAgent for philosophy validation
- Reads phase outputs, checks against principles
- CLI: forge refactor audit {id} {group}
- Guardian of idea fidelity"
```

---

**HANDOFF**

Note for integration:
- How audit reads philosophy
- What the issues format looks like
- How orchestrator should handle audit results

---

**Files to create:**
- `forge/refactor/audit_agent.py`

**Files to modify:**
- `forge/cli.py` - Add audit command
- `forge/refactor/prompts.py` - Add AUDIT_PROMPT

---

## Phase 5: UI Dashboard (Swift)

---

### Session 5.1: Models & Basic View

| | |
|---|---|
| **Worktree** | NO - Direct to main branch |
| **Scope** | IN: Swift models, basic dashboard view. OUT: Notifications, mode switch (5.2) |
| **Start When** | Phase 4 complete (phase + audit agents work) |
| **Stop When** | Can see refactor status in Forge app |

---

**PROMPT** (copy this into Claude Code):

```
Read docs/MAJOR_REFACTOR_MODE/VISION.md for the target UX.
Look at existing patterns in ForgeApp/Models/Feature.swift and
ForgeApp/Design/Components/WorkspaceCard.swift.

Add Major Refactor Mode to Forge macOS app:

1. Create ForgeApp/Models/RefactorPlan.swift:
   - RefactorPlan struct (mirrors Python RefactorState)
   - RefactorPhase struct
   - PhaseStatus enum
   - Codable for JSON parsing

2. Create ForgeApp/Views/Refactor/RefactorDashboardView.swift:
   - List of phases with status indicators
   - Current phase highlighted
   - Simple list view (railroad track is stretch goal for later)
   - Use existing DesignTokens for styling

3. Create ForgeApp/Services/RefactorClient.swift:
   - fetchRefactors() -> [RefactorPlan]
   - fetchRefactor(id) -> RefactorPlan
   - Use existing APIClient patterns

4. Add navigation to refactor dashboard from main app
   - Maybe a "Refactors" section in sidebar
   - Or accessible from project view

5. Run xcodegen generate before building

Test: Create a test refactor via CLI, see it appear in the app.
```

---

**ASK USER IF...**

- The phase list UI looks right (show a screenshot/mockup)
- Navigation placement is correct
- You need to add API endpoints to Python server first

---

**EXIT CRITERIA**

- [ ] RefactorPlan.swift model exists and parses correctly
- [ ] RefactorDashboardView shows list of phases
- [ ] Can navigate to dashboard from main app
- [ ] Styling matches existing Forge design

---

**GIT INSTRUCTIONS**

```bash
cd ForgeApp && xcodegen generate
git add ForgeApp/
git commit -m "feat(refactor): Session 5.1 - Swift models and basic dashboard

- Add RefactorPlan model
- Add RefactorDashboardView with phase list
- Add RefactorClient for API integration
- Navigate from main app to refactor view"
```

---

**HANDOFF**

Note for Session 5.2:
- What models exist
- How navigation works
- What styling was used

---

**Files to create:**
- `ForgeApp/Models/RefactorPlan.swift`
- `ForgeApp/Views/Refactor/RefactorDashboardView.swift`
- `ForgeApp/Services/RefactorClient.swift`

---

### Session 5.2: Phase Cards & Notifications

| | |
|---|---|
| **Worktree** | NO - Direct to main branch |
| **Scope** | IN: Phase cards, notifications, mode switch in brainstorm. OUT: Pause/resume (Phase 6) |
| **Start When** | Session 5.1 complete (basic dashboard exists) |
| **Stop When** | Notifications work, can trigger mode switch from brainstorm |

---

**PROMPT** (copy this into Claude Code):

```
Read docs/MAJOR_REFACTOR_MODE/VISION.md for notification design.
Look at ForgeApp/Design/DesignTokens.swift for styling.
Look at ForgeApp/Design/Components/WorkspaceCard.swift for card pattern.

Enhance Major Refactor Mode UI:

1. Create ForgeApp/Views/Refactor/PhaseCardView.swift:
   - Extend WorkspaceCard pattern
   - Show: phase name, status, active worktrees count
   - Click to expand details
   - "Open Terminal" button to launch worktree

2. Add notifications system:
   - In-app toasts: ForgeApp/Views/Components/ToastView.swift
   - macOS system notifications using UNUserNotificationCenter
   - Notification triggers:
     - Phase started
     - Phase complete
     - Audit passed/failed
     - Needs attention

3. Add mode switch to BrainstormChatView:
   - Detect MAJOR_REFACTOR_RECOMMENDED in Claude's response
   - Show: "Claude recommends Major Refactor Mode" banner
   - Button: "Switch to Major Refactor Mode"
   - On click: navigate to refactor creation flow

4. Run xcodegen generate before building

Test: Trigger a notification, see it appear. Start brainstorm with
large idea, see mode switch button.
```

---

**ASK USER IF...**

- Phase card design looks right
- Notification wording is good
- Mode switch placement in brainstorm is correct

---

**EXIT CRITERIA**

- [ ] PhaseCardView shows rich phase information
- [ ] In-app toast notifications work
- [ ] macOS system notifications work
- [ ] BrainstormChatView detects MAJOR_REFACTOR_RECOMMENDED
- [ ] Mode switch button appears and navigates correctly

---

**GIT INSTRUCTIONS**

```bash
cd ForgeApp && xcodegen generate
git add ForgeApp/
git commit -m "feat(refactor): Session 5.2 - Phase cards and notifications

- Add PhaseCardView with rich phase info
- Add notification system (in-app + macOS)
- Add mode switch trigger in BrainstormChatView
- Detect MAJOR_REFACTOR_RECOMMENDED marker"
```

---

**HANDOFF**

Note for Phase 6:
- How notifications are triggered
- How mode switch works
- What's left for full integration

---

**Files to create:**
- `ForgeApp/Views/Refactor/PhaseCardView.swift`
- `ForgeApp/Views/Components/ToastView.swift` (if doesn't exist)

**Files to modify:**
- `ForgeApp/Views/Brainstorm/BrainstormChatView.swift`
- `ForgeApp/Views/Refactor/RefactorDashboardView.swift`

---

## Phase 6: Integration

---

### Session 6.1: Full Integration & Polish

| | |
|---|---|
| **Worktree** | NO - Direct to main branch |
| **Scope** | IN: Pause/resume, Ship All, error handling, docs. OUT: Nothing - this completes the feature! |
| **Start When** | Phase 5 complete (UI works) |
| **Stop When** | End-to-end flow works, feature is production-ready |

---

**PROMPT** (copy this into Claude Code):

```
Read ALL docs in docs/MAJOR_REFACTOR_MODE/ - this is the final integration.
The goal: Make Major Refactor Mode production-ready.

Complete the integration:

1. Pause/Resume flow:
   - forge refactor pause {id}
     - Save current state to metadata.json
     - Mark status as "paused"
     - Notify user of paused worktrees
   - forge refactor resume {id}
     - Restore state
     - Resume orchestrator
   - Add pause/resume buttons in Swift UI

2. Ship All (the big merge):
   - forge refactor ship {id}
     - Check for conflicts BEFORE starting
     - Merge each phase worktree to main, IN ORDER
     - If any merge fails: stop and report
     - Clean up worktrees after successful merge
     - Celebrate!
   - Follow patterns from forge/merge.py

3. Error handling:
   - If phase agent fails: notify user, pause refactor
   - If audit fails after max iterations: escalate to user
   - If merge conflicts: show which files, offer help
   - All errors should be clear and actionable

4. Wire up the full flow:
   - Detection → Analysis → Planning → Phases → Audit → Ship
   - Test end-to-end with a small refactor

5. Update documentation:
   - Add Major Refactor Mode section to CLAUDE.md
   - Add to docs/WORKFLOW.md
   - Include examples of usage

Test: Run through entire flow from brainstorm to ship.
```

---

**ASK USER IF...**

- The merge order is correct
- Error messages are clear enough
- Any edge cases you've encountered

---

**EXIT CRITERIA**

- [ ] `forge refactor pause` saves state correctly
- [ ] `forge refactor resume` restores and continues
- [ ] `forge refactor ship` merges all worktrees in order
- [ ] Conflict detection works before shipping
- [ ] Error handling is clear and actionable
- [ ] CLAUDE.md updated with Major Refactor Mode
- [ ] docs/WORKFLOW.md updated
- [ ] End-to-end flow works

---

**GIT INSTRUCTIONS**

```bash
git add forge/ ForgeApp/ CLAUDE.md docs/
git commit -m "feat(refactor): Session 6.1 - Full integration

- Add pause/resume flow
- Add Ship All with conflict detection
- Add comprehensive error handling
- Update documentation
- Major Refactor Mode is complete!"
```

Then push and celebrate!

---

**HANDOFF**

This is the final session. Update Session Log with:
- Everything that was completed
- Any known limitations
- Future improvements to consider

The feature is now ready for use!

---

**Files to modify:**
- `forge/cli.py` - Add pause, resume, ship commands
- `forge/refactor/orchestrator.py` - Handle pause/resume
- `forge/refactor/state.py` - Add pause state
- `ForgeApp/Views/Refactor/RefactorDashboardView.swift` - Add buttons
- `CLAUDE.md` - Add usage docs
- `docs/WORKFLOW.md` - Add Major Refactor Mode section

---

## Session Log

> Update this section as sessions complete. Copy the template below for each session.

---

### Session 0.1: Planning Agent Implementation
**Date**: 2026-01-03
**Status**: DONE

**Completed**:
- [x] `forge refactor plan {project} --goal "..."` launches Warp session
- [x] Planning Agent CLAUDE.md instructs exploration before proposing
- [x] CLAUDE.md includes 2-3 questions at a time guidance
- [x] CLAUDE.md requires showing drafts for approval before writing
- [x] Template for all 5 docs included (PHILOSOPHY, VISION, DECISIONS, PRE_REFACTOR, EXECUTION)
- [x] Uses PLANNING_PROCESS_CLAUDE.md as the "soul" of the agent

**Discoveries**:
- Launching Claude in the refactor directory is elegant - it reads both the planning CLAUDE.md AND inherits the project's root CLAUDE.md
- No clipboard needed - CLAUDE.md tells Claude to start immediately
- Added `forge refactor resume` command for continuing sessions

**Files Created**:
- `forge/refactor/__init__.py` - Module init
- `forge/refactor/planning_agent.py` - PlanningAgent class with launch(), generate_planning_claude_md()
- `forge/refactor/prompts.py` - Template strings for planning docs

**Files Modified**:
- `forge/cli.py` - Added `forge refactor plan|list|status|resume` commands
- `.forge/config.json` - Removed obsolete fields (test_command, default_persona)

**For Next Session (1.1)**:
- The Planning Agent creates docs in `.forge/refactors/{id}/`
- Session 1.1 builds the RefactorState dataclass that tracks phase progress
- Look at how metadata.json is currently structured in planning_agent.py

---

### Session 1.1: Core State & Signals
**Date**: 2026-01-03
**Status**: DONE

**Completed**:
- [x] `forge/refactor/state.py` exists with RefactorState and SessionState
- [x] `forge/refactor/signals.py` exists with SignalType enum and read/write functions
- [x] State can be saved to JSON and loaded back
- [x] Signals can be written atomically and read back
- [x] Signal files use timestamp prefix for ordering
- [x] Code follows existing Forge patterns (see registry.py)

**Discoveries**:
- Used Enums for all status types (RefactorStatus, SessionStatus, AuditResult, SignalType) for type safety
- Added convenience functions like `signal_session_done()` for common signal patterns
- Signal filenames include microsecond precision for proper ordering

**Files Created**:
- `forge/refactor/state.py` - RefactorState, SessionState dataclasses with to_dict/from_dict, save/load
- `forge/refactor/signals.py` - SignalType enum, atomic write_signal, read_signals, convenience helpers

**Files Modified**:
- `forge/refactor/__init__.py` - Exports all new classes and functions

**For Next Session (1.2)**:
- Use RefactorState.load() to read current state
- Use state.start_session() when launching a session
- Use signal_session_started() to write signal when session begins
- Signals go in .forge/refactors/{id}/signals/

---

### Session 1.2: Execution Session Launcher
**Date**: 2026-01-03
**Status**: DONE

**Completed**:
- [x] `forge/refactor/session.py` exists with ExecutionSession class
- [x] `forge refactor start {id} {session}` launches terminal with Claude
- [x] Generated CLAUDE.md includes PHILOSOPHY.md reference and session prompt
- [x] RefactorState is updated when session starts
- [x] SESSION_STARTED signal is written
- [x] `forge refactor done {session}` updates state and writes SESSION_DONE signal

**Discoveries**:
- SessionSpec parses session info from EXECUTION_PLAN.md using regex patterns
- CLAUDE.md generation creates a complete instruction set for execution agents
- Auto-detection of refactor_id in `done` command by checking current_session in state
- Can fall back to per-session spec files at sessions/{id}/spec.md

**Files Created**:
- `forge/refactor/session.py` - ExecutionSession class, SessionSpec dataclass, complete_session function

**Files Modified**:
- `forge/cli.py` - Added `forge refactor start` and `forge refactor done` commands
- `forge/refactor/__init__.py` - Exports ExecutionSession, SessionSpec, complete_session

**For Next Session (2.1)**:
- Phase 1 Foundation is complete!
- Use `forge refactor start <id> <session>` to launch execution sessions
- Execution agents read generated CLAUDE.md with session prompt
- State and signals now track session lifecycle

---

### Session 2.1: Complexity Detection
**Date**: 2026-01-03
**Status**: DONE

**Completed**:
- [x] Added major refactor detection to BRAINSTORM_SYSTEM_PROMPT
- [x] Added major refactor detection to REFINE_SYSTEM_PROMPT
- [x] Output marker: `MAJOR_REFACTOR_RECOMMENDED`
- [x] Helper methods: `is_major_refactor_detected()`, `get_major_refactor()`

**Discoveries**:
- Added detection to BOTH prompts (not just REFINE) - user might start with brainstorm that turns out massive
- "Signs" list provides guidance without hobbling model (AGI-pilled balance)

**Commit**: c7eae0b

---

### Session 2.2: Codebase Analyzer
**Date**: 2026-01-03
**Status**: DONE

**Completed**:
- [x] Created `forge/refactor/analyzer.py` with CodebaseAnalyzer class
- [x] Scans file structure (respects .gitignore)
- [x] Two-stage Claude analysis: identify relevant files → deep analysis
- [x] Generates PRE_REFACTOR.md with all required sections
- [x] CLI command: `forge refactor analyze {id} --goal "..."`

**Discoveries**:
- Two-stage analysis is efficient: first identifies 5-15 relevant files, then deep-dives
- File sampling: max 80 lines per file prevents context overflow
- JSON parsing with fallback ensures graceful degradation

**Future Improvements**:
- Claude CLI calls can be slow (~30-60s) - could cache results
- Consider async processing for large codebases
- Could add --depth flag for analysis thoroughness

**Commit**: 288d207

---

### Session 3.1: Interactive Supervisor
**Date**: (not started)
**Status**: PENDING

---

### Session 4.1: Phase Agent
**Date**: (not started)
**Status**: PENDING

---

### Session 4.2: Audit Agent
**Date**: (not started)
**Status**: PENDING

---

### Session 5.1: Models & Basic View
**Date**: (not started)
**Status**: PENDING

---

### Session 5.2: Phase Cards & Notifications
**Date**: (not started)
**Status**: PENDING

---

### Session 6.1: Full Integration & Polish
**Date**: (not started)
**Status**: PENDING

---

## Session Log Entry Template

When completing a session, replace the PENDING entry with:

```markdown
### Session X.Y: Title
**Date**: 2026-01-XX
**Status**: DONE

**Completed**:
- [x] Thing that was done
- [x] Another thing done

**Not Completed** (if any):
- [ ] Thing that wasn't done
- Reason: explanation

**Discoveries**:
- Anything unexpected found
- Decisions made during implementation

**For Next Session**:
- Key context needed
- Files to look at first

**Files Modified**:
- `path/to/file` - what changed
```
