---
name: weekly-ticket-slideshow-generator
description: Build a weekly ticket-flow payload from dump files and render it through $slideshow-generator. Use when you need a weekly ticket presentation that preserves each ticket's full activity chain, adds interpretation-oriented visuals/diagrams, and provides presenter-ready speaking scripts in notes.
---

# Weekly Ticket Slideshow Generator (Wrapper)

Create a weekly ticket slideshow by preparing a normalized payload and delegating rendering to `$slideshow-generator`.

This skill is domain-aware for ticket dumps. It acts as a harness that interprets ticket-flow signals and emits deterministic rendering directives for `$slideshow-generator`.

## Execution Steps

1. Resolve target week under `memory/tickets/YYYY-W##/`.
2. Parse `# All Scraped Tickets` from each daily dump.
3. Merge same ticket IDs across the week and build chronological flows.
4. Infer start, transitions, and current state per ticket.
5. Emit normalized payload JSON (`weekly-ticket-slides.json`) that matches `$slideshow-generator` input contract, including `renderDefaults` and slide-level `renderPlan`.
6. For each ticket slide, include interpretation blocks at minimum:
- What happened
- Issue
- Impact
- Next step
7. Generate presenter notes as speaking script (line-by-line cues), not a generic summary paragraph.
8. Invoke `$slideshow-generator` script to render:
- `index.html`
- `presenter.html`
- `slides.json`
9. Save outputs in the same week folder convention used by ticket dumps:
- Root path: `memory/tickets/`
- Week folder format: `YYYY-W##`
- Week slideshow files:
  - `YYYY-W##-weekly-ticket-slideshow.html`
  - `YYYY-W##-weekly-ticket-slideshow-presenter.html`
  - `YYYY-W##-weekly-ticket-slideshow.json`

## Rules

1. Keep wrapper focused on ticket parsing, deterministic flow inference, and deterministic render-plan hints only.
2. For `--renderer reveal-single`, render a single bundled Reveal HTML file directly in this wrapper.
3. For `--renderer legacy`, keep delegating to `$slideshow-generator`.
4. Preserve full chronological ticket flow when middle events exist.
5. Keep empty-week behavior explicit and informative.
6. Encode layout and visual intent as `renderPlan` rather than hard-coding slide HTML.
7. Avoid status-only graph slides by default; prefer explanatory visuals and flow diagrams that help humans interpret ticket movement and blockers.

## Command

```powershell
python skills/weekly-ticket-slideshow-generator/scripts/generate_weekly_slideshow.py --week 2026-W20
```
