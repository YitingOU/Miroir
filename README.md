# Miroir · OpenClaw Agent Forge

Miroir is now a skill for generating OpenClaw agents.

Input a person, operating role, existing perspective skill, or fuzzy need. The skill researches
the source material, designs the agent contract, and writes it directly to `~/openclaw-workspace/[agent-name]/`
as a runnable OpenClaw agent workspace. It stages the build before installing it, using
`~/openclaw-workspace/.staging/[agent-name]-[run-id]/`, so OpenClaw does
not see a half-built agent if research or validation fails. OpenClaw must ignore the `.staging/`
directory; otherwise use another non-scanned staging directory on the same filesystem:

```
[agent-name]/
├── IDENTITY.md
├── SOUL.md
├── AGENTS.md
├── USER.md
├── TOOLS.md
├── MEMORY.md
├── HEARTBEAT.md
├── references/
└── memory/
```

The old Nuwa-style perspective examples are kept under `examples/` as source material and
conversion samples. The root skill now targets OpenClaw's seven-file agent model instead of
generating standalone perspective `SKILL.md` files.

## What It Generates

| File | Purpose |
| --- | --- |
| `IDENTITY.md` | Name, agent id, role, one-line signal |
| `SOUL.md` | Personality, voice, values, truth boundary |
| `AGENTS.md` | Operating manual, request routing, memory, safety, delegation |
| `USER.md` | User facts and preferences, only when provided |
| `TOOLS.md` | Local paths, commands, APIs, tool conventions |
| `MEMORY.md` | Seed durable facts and known limits |
| `HEARTBEAT.md` | Proactive checklist; empty by default |
| `BOOTSTRAP.md` | Optional one-time setup |

Important OpenClaw constraint: subagents only see `AGENTS.md` and `TOOLS.md`. This project is
designed around that boundary, so operational rules are not buried in persona prose.

## Example Prompts

```text
生成一个 Karpathy 风格的 OpenClaw agent
把 examples/steve-jobs-perspective 转成 OpenClaw agent
给我做一个负责 GitHub issue triage 的 OpenClaw agent
我想要一个能每天帮我看项目风险的 agent
更新现有 andrej-karpathy agent，增强它对最新 AI 模型的研究流程
```

## Workflow

1. Route the request: persona, operator, skill conversion, update, or fuzzy diagnosis.
2. Create a unique staging skeleton under `~/openclaw-workspace/.staging/[agent-name]-[run-id]/`.
3. Choose an evidence mode: fast conversion, local-first, deep persona research, or operator research.
4. Synthesize the agent contract: mission, voice, workflows, tools, memory, safety.
5. Write the OpenClaw files using the template in `references/openclaw-agent-template.md`.
6. Validate the staging workspace with `scripts/quality_check.py`.
7. Install into a new unique live path under `~/openclaw-workspace/[agent-name]/`.
8. Validate the final agent workspace and report the live path.

## Scripts

```bash
# Validate the final agent workspace
python3 scripts/quality_check.py ~/openclaw-workspace/karpathy

# Summarize research notes for the generation checkpoint
python3 scripts/merge_research.py ~/openclaw-workspace/karpathy

# Download YouTube subtitles for source collection
bash scripts/download_subtitles.sh <YouTube_URL> sources/transcripts

# Clean one SRT/VTT subtitle file into transcript text
python3 scripts/srt_to_transcript.py input.srt output.txt
```

## References

- `SKILL.md` - the actual OpenClaw Agent Forge workflow.
- `references/agent-design-framework.md` - design rules for OpenClaw's loading model.
- `references/openclaw-agent-template.md` - file-by-file output template.
- `references/persona-research-pipeline.md` - the extracted six-lane research flow from the original project.
- `examples/` - legacy perspective skills that can be converted into OpenClaw agents.

## Quality Bar

A generated agent should:

- Have a clear job, not just a vibe.
- Keep startup context compact.
- Separate personality (`SOUL.md`) from operations (`AGENTS.md`).
- Give subagents enough context through `AGENTS.md` and `TOOLS.md`.
- Avoid secrets, auth state, session logs, and stale local paths.
- Research current facts before making claims about modern companies, people, models, laws, or prices.

## License

MIT.
