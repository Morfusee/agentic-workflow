---
name: weekly-ticket-slideshow-generator
description: Build a weekly insight-first ticket deck payload from dump files and render it through $slideshow-generator. Use when you need strict anti-restatement slides, signal-based diagrams, and polished presenter scripts.
---

# Weekly Ticket Slideshow Generator

Create a weekly ticket deck by synthesizing non-obvious insights and emitting the strict payload consumed by `$slideshow-generator`.

## Execution Steps

1. Resolve target week under `memory/tickets/YYYY-W##/`.
2. Parse `# All Scraped Tickets` from each daily dump.
3. Merge same ticket IDs across the week and preserve chronological events.
4. Synthesize content-slide fields:
- `insight`
- `context`
- `decision`
- `actions`
- `signals`
- `visualSpec`
- `speakerScript`
5. Apply strict suppression of obvious text repetition.
6. Detect diagram-required signals from blockers, dependencies, status churn, and event depth.
7. Emit the hard-break payload JSON (`YYYY-W##-weekly-ticket-slides.json`).
8. Render output:
- `--renderer reveal-single`: bundled one-file reveal deck (`YYYY-W##-weekly-ticket-slideshow-reveal.html`)
- `--renderer legacy`: invoke `$slideshow-generator` and emit audience/presenter HTML pair

## Rules

1. Do not emit legacy text-first fields as primary story content.
2. Keep default `presentationPolicy` values:
- `textPolicy=strict-summary`
- `diagramPolicy=signal-required`
- `styleProfile=narrative-cards`
3. Use visual types that add interpretive context:
- `state-lane-flow`
- `dependency-map`
- `issue-impact-chain`
- `context-chips`
- `action-ladder`
4. Keep presenter scripts in freeform polished prose with natural pacing.
5. Keep unresolved-risk closure actions explicit in the closing slide.

## Command

```powershell
python skills/weekly-ticket-slideshow-generator/scripts/generate_weekly_slideshow.py --week 2026-W20 --renderer reveal-single
```
