# OpenClaw Agent Design Framework

Use this framework to turn source material into a compact OpenClaw agent workspace.

## 1. Design The Agent Around A Job

An OpenClaw agent is not just a persona. It is an operating system for a recurring job.

Before writing files, define:

- **Mission:** what outcome this agent owns.
- **Users:** who it serves and what they expect.
- **Default work:** what it should do without needing extra setup.
- **Non-goals:** what it should refuse, defer, or route elsewhere.
- **Escalation:** when to ask the user before acting.
- **Evidence:** what source material justifies the agent's behavior.

If the job is unclear, the generated files will become a pile of style notes. Clarify the
job before adding personality.

## 2. Respect OpenClaw Loading Boundaries

OpenClaw loads different files into different contexts:

| Runtime context | Files visible |
| --- | --- |
| Main session | `IDENTITY.md`, `SOUL.md`, `AGENTS.md`, `USER.md`, `TOOLS.md`, `MEMORY.md`, daily memory |
| Subagents | `AGENTS.md`, `TOOLS.md`, task prompt |
| Heartbeats | `HEARTBEAT.md` plus minimal operational context |
| First run | `BOOTSTRAP.md`, then it should be deleted |

Design implication:

- Put operational rules in `AGENTS.md`.
- Put tool facts and local commands in `TOOLS.md`.
- Put personality in `SOUL.md`.
- Put user facts in `USER.md`.
- Put stable durable facts in `MEMORY.md`.
- Put proactive recurring checks in `HEARTBEAT.md`.

Subagents do not see `SOUL.md`, `USER.md`, or `MEMORY.md`. Any rule they must follow must
appear in `AGENTS.md` or `TOOLS.md`.

## 3. File Responsibilities

### IDENTITY.md

Purpose: first-glance identity.

Include:

- Name
- Agent id
- Role
- Core vibe
- One-line signal

Avoid:

- Biography
- Long values lists
- Tool instructions

Target: under 500 characters.

### SOUL.md

Purpose: personality, voice, values, truth boundaries.

Include:

- Core stance in first person
- Temperament
- Voice rules
- Signature phrases, used sparingly
- Values and anti-patterns
- Truth boundary, especially for public-person persona agents

Avoid:

- Step-by-step operating procedures
- Tool command reference
- Memory file formats
- Long source dumps

Target: under 10K characters.

### AGENTS.md

Purpose: operating manual.

Include:

- Startup behavior
- Request classification
- Response protocol
- Research rules
- Delegation/subagent rules
- Memory workflow
- Safety and approval gates
- Installed skills and when to read references

Style:

- Imperative
- Tables for routing
- Numbered workflows for fragile sequences
- Motivation where it prevents misuse

Target: under 18K characters.

### USER.md

Purpose: user facts and preferences.

Include only facts the user provided or explicitly approved:

- Name, timezone, working hours
- Communication preferences
- Project context
- Privacy preferences

If no user facts exist, write a small placeholder that says no durable user profile has
been configured. Do not invent a user profile.

Target: under 5K characters.

### TOOLS.md

Purpose: local tool and integration reference.

Include:

- Local paths
- CLI commands
- API/env var names without secret values
- Installed skills and source maps
- Tool fallback order
- Known failure modes

Avoid:

- Secrets
- Auth state
- Session logs
- Full API docs when a short link/path is enough

Target: under 15K characters.

### MEMORY.md

Purpose: seed durable facts.

Include:

- Stable agent facts
- Stable user preferences if approved
- Known source limitations
- Maintenance notes

Avoid:

- Conversation transcripts
- Sensitive data
- Speculative facts

### HEARTBEAT.md

Purpose: proactive checklist for heartbeat runs.

Default:

```
# HEARTBEAT.md

No proactive heartbeat work is configured.

Reply `HEARTBEAT_OK` unless the user has explicitly added a monitoring/checklist task.
```

Do not add proactive monitoring unless the user asked for it.

### BOOTSTRAP.md

Purpose: one-time setup.

Use only when the first run must:

- Install bundled skills
- Create directories
- Run a migration
- Ask for missing configuration

Make it idempotent. Tell the agent to delete `BOOTSTRAP.md` after completion.

## 4. Persona Agents

Persona agents should preserve a public reasoning style without pretending to possess private
access to the person.

Extract:

- Mental models
- Decision heuristics
- Voice and cadence
- Publicly documented constraints
- Blind spots and controversy
- Topics that require current research

Write:

- `SOUL.md`: first-person persona stance, voice, values, truth boundary.
- `AGENTS.md`: answer protocol, research rules, safety rules.
- `TOOLS.md`: source map and when to read archived references.

Never claim:

- Private thoughts
- Current unpublished opinions
- Direct authorship by the biological person
- Access to accounts or confidential material

If asked directly whether the agent is the real person, answer truthfully in one sentence
and return to the work.

## 5. Operator Agents

Operator agents should be judged by reliable execution, not style.

Extract:

- Request classes
- Required inputs
- Tool order
- State changes
- Confirmation gates
- Failure handling
- Reporting format

Write:

- `AGENTS.md`: the actual playbook.
- `TOOLS.md`: commands, paths, credentials policy.
- `HEARTBEAT.md`: only explicit recurring checks.
- `MEMORY.md`: durable operational facts.

Default to asking before external side effects such as sending messages, spending money,
deleting data, pushing code, changing schedules, or modifying production systems.

## 6. Evidence Handling

Rank sources:

1. User-provided first-party source material
2. Official docs, public writings, source repos, transcripts
3. Long-form interviews and decision records
4. Reputable analysis and criticism
5. Search summaries and commentary

Keep source notes under `references/research/` when they are needed for future maintenance.
Each note should state:

- What it informs
- Source type
- Confidence level
- Contradictions or uncertainty
- Date gathered

## 7. Validation Questions

Before final delivery, answer these:

- Can a new OpenClaw runtime start this agent without reading anything else?
- Can a subagent follow the needed workflow with only `AGENTS.md` and `TOOLS.md`?
- Does the agent have a job, or only a personality?
- Are file sizes below targets?
- Are there secrets, private paths, copied session logs, or auth state?
- Does `HEARTBEAT.md` avoid unsolicited proactive work?
- Does the agent know when to research current facts?
- Are limitations explicit instead of hidden?

If any answer is weak, patch the relevant file before delivery.
