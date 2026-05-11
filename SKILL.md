---
name: openclaw-agent-forge
description: |
  OpenClaw Agent Forge: input a person, role, operating need, existing perspective skill, or fuzzy request,
  then research, synthesize, and generate a runnable OpenClaw agent workspace.
  Produces IDENTITY.md, SOUL.md, AGENTS.md, USER.md, TOOLS.md, MEMORY.md, HEARTBEAT.md,
  with optional BOOTSTRAP.md, bundled skills, and evidence references.
  Trigger on: "generate an OpenClaw agent", "create agent", "build an agent workspace",
  "turn this skill into an OpenClaw agent", "make a Karpathy/Jobs style OpenClaw agent",
  "openclaw agent", "agent persona", "agent config", or Chinese equivalents like
  "生成openclaw agent", "造一个agent", "把这个skill改成agent", "创建智能体".
---

# OpenClaw Agent Forge

This skill turns source material into a working OpenClaw agent workspace.

The output is not a single prompt and not a Claude/Codex skill. It is a directory of OpenClaw
context files that the runtime loads at different scopes:

```
[agent-name]/
├── IDENTITY.md      # name, role, core vibe; very small
├── SOUL.md          # personality, voice, values, truth boundaries
├── AGENTS.md        # operations manual; main session + subagents
├── USER.md          # user profile and stable preferences
├── TOOLS.md         # local paths, tool conventions, integration notes
├── MEMORY.md        # seed long-term facts
├── HEARTBEAT.md     # proactive checklist; tiny unless explicitly configured
├── BOOTSTRAP.md     # optional one-time setup, deleted after first run
├── skills/          # optional installed skills copied into this agent
├── references/      # optional evidence, source maps, archived inputs
└── memory/          # daily notes created at runtime
```

Core rule: optimize for what OpenClaw actually loads. Subagents see only `AGENTS.md`
and `TOOLS.md`; personality files, user profile, memory, and heartbeat context are not
available to them unless the main agent passes that context explicitly.

## Workflow

### Phase 0: Route The Request

Classify the user's input:

| Input | Route |
| --- | --- |
| A public person or persona | Build a persona agent |
| A job function or team role | Build an operator agent |
| An existing perspective skill | Convert skill to OpenClaw agent |
| An existing OpenClaw agent | Update selected context files |
| A fuzzy need | Diagnose the desired agent type, then build |

Ask at most three clarifying questions. If the user says "just do it", default to:

- Comprehensive agent
- Final output target: `FINAL_ROOT=~/openclaw-workspace/[agent-name]`
- Staging build target: `BUILD_ROOT=~/openclaw-workspace/.staging/[agent-name]-[run-id]`
- Install the validated staged agent into the live OpenClaw workspace
- Create a new unique final agent directory unless the user explicitly asks to update an existing agent
- Public research plus any local material already provided

Minimum clarification targets:

1. **Agent identity and job:** who it is, what it is responsible for, and what success looks like.
2. **Runtime use:** conversational persona, operational assistant, coding orchestrator, monitoring agent, or hybrid.
3. **Source material:** public web, local files, existing skill, existing OpenClaw agent, or user-provided notes.

### Phase 0.5: Create The Staging Skeleton

Create a staging build root before research starts. Use two explicit path variables:

- `RUN_ID=[timestamp-or-random-suffix]`
- `BUILD_ROOT=~/openclaw-workspace/.staging/[agent-name]-[run-id]`
- `FINAL_ROOT=~/openclaw-workspace/[agent-name]`

`BUILD_ROOT` and `FINAL_ROOT` must live under `~/openclaw-workspace/` so the final install can
use a same filesystem rename. Do not reuse a staging directory; every run gets a new `RUN_ID`.
OpenClaw runtime must ignore `~/openclaw-workspace/.staging/`. If that ignore behavior is not
guaranteed, use another non-scanned staging directory on the same filesystem and stop and ask
before writing a live staging directory.

Build and research inside the staging root:

```
$BUILD_ROOT/
├── IDENTITY.md
├── SOUL.md
├── AGENTS.md
├── USER.md
├── TOOLS.md
├── MEMORY.md
├── HEARTBEAT.md
├── references/research/
└── memory/
```

Do not create or modify the final live agent directory until the staging build passes validation.
This prevents OpenClaw from seeing a half-built agent after an interrupted run.

Do not stop at a project-local export. The normal result of persona distillation is a new
OpenClaw agent directory under `~/openclaw-workspace/`, with distilled information written
directly into the agent's startup files and `references/research/` evidence notes.

If `FINAL_ROOT=~/openclaw-workspace/[agent-name]` already exists and the user did not ask to
update it, choose a new `FINAL_ROOT` such as `~/openclaw-workspace/[agent-name]-2` or a more
specific slug before creating any live directory. Never overwrite an existing agent workspace
silently.

Use project-local `./openclaw-workspace/[agent-name]/` only when the user explicitly asks for
an export-only copy, a dry run, or the live OpenClaw workspace cannot be resolved.

If converting an existing skill, also create:

```
skills/[source-skill-name]/
references/[source-skill-name]/
```

Copy or archive source material only when it is needed for self-contained future maintenance.
Do not copy secrets, auth states, session logs, private chat exports, or credential files into
the generated agent.

### Phase 1: Collect Evidence

Choose an evidence collection mode before searching:

| Mode | Use when | Method |
| --- | --- | --- |
| **Fast conversion** | Existing perspective skill or strong local source already exists | Read only the source sections needed for OpenClaw files |
| **Local-first** | User provided books, transcripts, notes, exports, or an existing agent | Classify local material, identify gaps, then search only for missing/current facts |
| **Deep persona research** | Public-person agent needs high fidelity or user asks for deep cloning/distillation | Load `references/persona-research-pipeline.md` and run the six-lane research plan |
| **Operator research** | The agent is a role/workflow, not a person | Gather mission, tools, workflows, memory, heartbeat, and safety requirements |

Default to **local-first**. Use web research when the agent depends on current public facts
or when local sources are insufficient. Use **deep persona research** for high-fidelity
public-person agents where voice, mental models, and behavioral record all matter.

For persona agents, gather:

1. **Identity and origin:** role, domain, recurring self-description, public trajectory.
2. **Mental models:** repeated reasoning frames, decision heuristics, anti-patterns.
3. **Voice:** sentence rhythm, certainty level, humor, vocabulary, taboo phrases.
4. **Behavioral record:** decisions, conflicts, reversals, public constraints.
5. **Truth boundary:** what is public evidence, what is inference, what must never be claimed.

For operator agents, gather:

1. **Mission:** outcomes, users served, non-goals, escalation thresholds.
2. **Workflows:** request routing, checklists, decision trees, completion criteria.
3. **Tools:** APIs, CLIs, local paths, credentials policy, failure modes.
4. **Memory:** what should be remembered, where, and what must remain ephemeral.
5. **Heartbeat:** proactive checks, cadence, quiet hours, archive/report behavior.
6. **Safety:** external side effects, approval gates, destructive actions, privacy boundaries.

Each research note should say which target file it informs: `IDENTITY`, `SOUL`, `AGENTS`,
`USER`, `TOOLS`, `MEMORY`, or `HEARTBEAT`.

If using deep persona research, preserve the old six-file evidence shape under
`references/research/`:

```
01-writings.md
02-conversations.md
03-expression-dna.md
04-external-views.md
05-decisions.md
06-timeline.md
```

This structure is optional for simple agents but recommended for copied-person agents.

### Phase 1.5: Evidence Checkpoint

Before synthesis, summarize research quality:

```
Agent target: [agent-name]
Source mode: local / web / existing skill / mixed
Evidence summary:
- Identity: ...
- Voice or operating style: ...
- Workflows: ...
- Tools and integrations: ...
- Memory and heartbeat: ...
- Safety and truth boundaries: ...

Gaps:
- ...
```

If a core dimension is thin, either ask for more source material or explicitly mark the
result as a limited v1 agent.

### Phase 2: Synthesize The Agent Contract

Read `references/agent-design-framework.md` before writing files.

Produce a compact contract:

- **Identity:** name, agent id, role, one-line signal.
- **Operating thesis:** what the agent is here to do better than a generic assistant.
- **Default request routing:** how it classifies incoming work.
- **Response protocol:** default answer shape, when to research, when to act, when to ask.
- **Tool protocol:** tool order, required checks, local paths, credential handling.
- **Memory protocol:** what to save, what not to save, and where.
- **Safety protocol:** approval gates, truth boundaries, escalation language.
- **Heartbeat protocol:** no proactive work by default unless the user requested it.

Then map each part to exactly one OpenClaw file:

| Content | File |
| --- | --- |
| Name, emoji, role, core vibe | `IDENTITY.md` |
| Personality, tone, values, persona truth boundary | `SOUL.md` |
| Workflows, routing, delegation, memory rules, safety operations | `AGENTS.md` |
| User facts and preferences | `USER.md` |
| Tool commands, local paths, APIs, integration conventions | `TOOLS.md` |
| Seed durable facts | `MEMORY.md` |
| Proactive recurring checklist | `HEARTBEAT.md` |
| One-time setup or migration | `BOOTSTRAP.md` |

Hard rule: if subagents must follow it, it belongs in `AGENTS.md` or `TOOLS.md`, not `SOUL.md`.

### Phase 3: Build The Files

Read `references/openclaw-agent-template.md` and fill the sections. Keep files compact:

| File | Target size |
| --- | --- |
| `IDENTITY.md` | under 500 chars |
| `HEARTBEAT.md` | under 2K chars |
| `USER.md` | under 5K chars |
| `SOUL.md` | under 10K chars |
| `TOOLS.md` | under 15K chars |
| `AGENTS.md` | under 18K chars |

Default file behavior:

- `IDENTITY.md`: punchy, not a biography.
- `SOUL.md`: first-person is acceptable; include forbidden phrases and truth boundary.
- `AGENTS.md`: imperative operating manual with routing tables and clear workflows.
- `USER.md`: factual, sparse, and safe; leave intentionally blank if no user facts exist.
- `TOOLS.md`: concrete command/path/API notes; no secrets.
- `MEMORY.md`: seed facts only; do not fabricate history.
- `HEARTBEAT.md`: "No proactive heartbeat work is configured" unless the user requested monitoring.
- `BOOTSTRAP.md`: only for one-time setup that should run once and then disappear.

### Phase 4: Validate

Run:

```bash
python3 scripts/quality_check.py "$BUILD_ROOT"
```

Validation must check:

- Required files exist.
- File sizes are within OpenClaw limits.
- Operational rules are in `AGENTS.md`, not buried in `SOUL.md`.
- `AGENTS.md` and `TOOLS.md` contain enough context for subagents.
- `HEARTBEAT.md` is tiny and has no unsolicited proactive work.
- No placeholders, fake private access, secrets, or stale local author paths.
- Persona agents do not claim to be the biological person when challenged.
- Current-fact questions require research before judgment.

If validation fails, patch the files and rerun. If a failure is due to legitimately missing
source material, document that limitation in `SOUL.md` and `AGENTS.md`.

### Phase 5: Finalize The Agent Workspace

Default: leave the finished agent in the live OpenClaw workspace at
`FINAL_ROOT=~/openclaw-workspace/[agent-name]` and report that path.

Before finishing, choose the correct path:

1. Resolve `FINAL_ROOT`, normally `~/openclaw-workspace/[agent-name]`.
2. Check whether that final agent folder already existed before this run.
3. Never copy secrets, auth files, sessions, or runtime state.

#### New Agent Install

Use this path when `FINAL_ROOT` does not exist, or when you selected a new unique final path.

1. Validate `BUILD_ROOT`.
2. Ensure `FINAL_ROOT` still does not exist.
3. Install a new agent with an atomic same-filesystem rename from `BUILD_ROOT` to `FINAL_ROOT`.
4. Run validation against `FINAL_ROOT`.

#### Existing Agent Update

Use this path only when the user explicitly asked to update an existing OpenClaw agent.

1. Read the current target files from `FINAL_ROOT` before changing them.
2. Compare the staged files in `BUILD_ROOT` against the current agent.
3. Do not move or copy the whole staging directory over an existing agent.
4. Patch only the selected files in FINAL_ROOT, preserving unrelated user edits and runtime state.
5. Run validation against `FINAL_ROOT`.

Final validation command:

```bash
python3 scripts/quality_check.py "$FINAL_ROOT"
```

#### Staging Cleanup

- After a successful new-agent rename, remove the empty `.staging` parent only if it is empty.
- If validation or install fails, keep BUILD_ROOT for inspection and report its path.
- Never retry into the same BUILD_ROOT; start a new run with a new `RUN_ID`.

Optional export: if the user also wants a portable copy, mirror the final workspace into a
project-local `openclaw-workspace/[agent-name]/` directory after validation. The export is
secondary; the live OpenClaw agent workspace is the source of truth.

## Conversion Modes

### Existing Perspective Skill To OpenClaw Agent

When converting a perspective skill:

1. Read the source `SKILL.md`.
2. Read only the references needed for identity, voice, mental models, decisions, and current facts.
3. Convert:
   - Role rules and voice -> `SOUL.md`
   - Answer workflow -> `AGENTS.md`
   - Research/source map -> `TOOLS.md`
   - Latest dynamics and limits -> `MEMORY.md` or `SOUL.md`
4. Archive the source skill under `skills/` or `references/` if useful for future updates.
5. Add a note in `TOOLS.md` describing when to read the archived source.

Do not simply paste the full skill into `AGENTS.md`. OpenClaw agents need concise startup
context, not a giant monolith.

### Updating An Existing Agent

Use the existing OpenClaw file map:

- Personality/tone changes -> `SOUL.md`
- Operational workflows -> `AGENTS.md`
- Tool paths and commands -> `TOOLS.md`
- User preferences -> `USER.md`
- Stable facts -> `MEMORY.md`
- Proactive checks -> `HEARTBEAT.md`
- Name/vibe -> `IDENTITY.md`

Read the target file first, patch the smallest section, and preserve unrelated user changes.

### Fuzzy Need To Agent Recommendation

If the user only describes a need, recommend 2-3 agent shapes:

```
### Candidate: [agent type]
Mission: ...
Core workflows: ...
Files that matter most: ...
Limitations: ...
```

After selection, continue with Phase 0.5.

## Quality Bar

A good OpenClaw agent:

- Has a clear job, not just a vibe.
- Separates personality from operations.
- Gives subagents enough operational context.
- Has explicit truth and safety boundaries.
- Knows when to research, when to act, and when to ask.
- Uses memory deliberately.
- Starts with small context and loads references only when needed.

Avoid:

- Long biographies in startup files.
- Persona theater without workflow competence.
- Copying private source material into distributable agents.
- Putting operations in `SOUL.md`.
- Making `HEARTBEAT.md` proactive without user consent.
- Claiming private access to living people, companies, or accounts.
