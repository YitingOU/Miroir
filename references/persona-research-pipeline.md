# Deep Persona Research Pipeline

This is the extracted hard-coded research flow from the original project, abstracted as
an optional evidence mode for high-fidelity public-person OpenClaw agents.

Use it when the user asks to copy/distill a person deeply, when voice fidelity matters,
or when there is no strong existing perspective skill to convert.

## Mode Selection

| Source mode | Trigger | Strategy |
| --- | --- | --- |
| Public web | No local material | Run all six research lanes |
| Local-first | User provides PDFs, transcripts, exports, notes, or an existing archive | Classify local material into lanes, then search only the gaps |
| Local-only | User says to use only provided material or the person is private/non-public | Do not search the web; mark weak lanes as limited |

Local first usually beats web search. Complete books, long transcripts, internal notes,
and raw exports are higher signal than summaries.

## Six Research Lanes

| Lane | Search target | Extract | Output |
| --- | --- | --- | --- |
| 1. Writings | Books, essays, papers, blogs, newsletters | Repeated claims, original terms, recommended books, systematic beliefs | `01-writings.md` |
| 2. Conversations | Podcasts, long interviews, talks, AMAs, Q&A | Improvised reasoning, analogies, changed positions, refusal patterns | `02-conversations.md` |
| 3. Expression DNA | Social posts, short notes, public debates, fragments | Sentence rhythm, vocabulary, certainty, humor, taboo words | `03-expression-dna.md` |
| 4. External Views | Biographies, criticism, profiles, peer commentary | Blind spots, controversy, how others observe the person, peer comparisons | `04-external-views.md` |
| 5. Decisions | Major decisions, reversals, crises, career moves | Decision context, stated logic, behavior vs claims, postmortems | `05-decisions.md` |
| 6. Timeline | Full chronology and recent activity | Milestones, intellectual shifts, last-12-month changes for living people | `06-timeline.md` |

Write all outputs under:

```
openclaw-workspace/[agent-name]/references/research/
```

## Required Note Format

Each lane file should contain:

- Scope and date gathered
- Source list with URLs or local file paths
- Source confidence: primary, secondary, or inference
- Key findings
- Contradictions and uncertainty
- Which OpenClaw files the note informs: `IDENTITY`, `SOUL`, `AGENTS`, `TOOLS`, `MEMORY`

Hard rules:

- Distinguish what the person said, what others said, and what you infer.
- Preserve contradictions instead of smoothing them over.
- Do not fabricate quotes.
- For living people, do not claim private access or current unpublished opinions.
- If a lane is thin, say so and carry that limitation into `SOUL.md` and `AGENTS.md`.

## Local Material Classification

| Material | Primary lanes |
| --- | --- |
| Book or long essay | `01-writings`, `03-expression-dna` |
| Interview transcript | `02-conversations`, `03-expression-dna` |
| Video subtitles | `02-conversations`, `03-expression-dna` |
| Blog/newsletter export | `01-writings`, `03-expression-dna` |
| Social media export | `03-expression-dna`, `06-timeline` |
| Decision memo or internal notes | `05-decisions`, `AGENTS` workflow evidence |
| User notes | Cross-check only unless they quote primary material |

For subtitles:

```bash
bash scripts/download_subtitles.sh <YouTube_URL> openclaw-workspace/[agent-name]/references/sources/transcripts
python3 scripts/srt_to_transcript.py input.srt output.txt
```

## Source Priority

1. User-provided first-party material
2. The person's books, essays, talks, transcripts, repos, filings, or official posts
3. Long interviews and decision records
4. Reputable profiles, criticism, biographies, peer commentary
5. Search summaries and ordinary commentary

Chinese public-person source policy:

- Prefer original Bilibili videos, podcast audio, official speeches, books, and reputable media.
- Use sources like 36氪, 极客公园, 晚点 LatePost, 财新, 第一财经, 虎嗅, 少数派, 机器之心 when relevant.
- Exclude Zhihu, WeChat public-account reposts, Baidu Baike, Baidu Zhidao, and obvious content farms.

Western public-person source policy:

- Prefer official sites, books, papers, GitHub, X/Twitter originals, YouTube originals, podcast transcripts, SEC/court filings, and reputable long-form profiles.

## Lane Prompt Template

Use this shape for each lane:

```text
Task: research [person] for lane [lane name].

Focus:
- [lane-specific search targets]
- [lane-specific extraction targets]

Output:
- Write to openclaw-workspace/[agent-name]/references/research/[file-name].md
- Mark every claim as primary / secondary / inference.
- Include URLs or local source paths.
- Preserve contradictions and weak evidence.
- End with "OpenClaw file implications" listing what should inform IDENTITY, SOUL, AGENTS, TOOLS, MEMORY, or HEARTBEAT.
```

## Checkpoint

After all available lanes are complete, run:

```bash
python3 scripts/merge_research.py openclaw-workspace/[agent-name]
```

Then summarize:

- Source coverage by lane
- Strongest mental models
- Voice signals
- Behavioral evidence
- Contradictions
- Thin or missing dimensions
- OpenClaw file implications

Proceed to synthesis only after the evidence quality is clear. A limited but honest agent is
better than a polished agent that hides weak evidence.
