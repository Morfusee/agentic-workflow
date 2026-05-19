---
name: slideshow-generator
description: Render a presentation-grade fullscreen HTML slideshow from structured presentation information. Use when slide layout, pacing, presenter notes, and visual treatment need to be composed from an upstream brief such as the output of $weekly-ticket-slideshow-generator.
---

# Slideshow Generator

Render a domain-agnostic HTML slideshow from a structured brief or presentation payload. Treat upstream briefs as the interpretation source of truth: do not re-analyze raw weekly dumps when a brief exists, and preserve ticket-level depth when the brief asks for it.

## Output Contract

1. Generate final HTML directly.
2. Use one self-contained file for audience and presenter views.
3. Write to `presentations/[presentation-name]/index.html` under the canonical memory root by default. Derive `[presentation-name]` from the title using lowercase letters, digits, and hyphens. Honor explicit user paths.
4. Fit the deck inside a virtual `1920x1080` stage that scales to the viewport.
5. Keep visible slide text scannable within five to eight seconds.
6. Keep each slide focused on one primary message; slides support narration rather than replace it.
7. Vary layout, grouping, emphasis, and visual treatment when it clarifies the content. Avoid decorative noise, repeated fallback layouts, and dense detail dumps.
8. Use diagrams, flows, cards, chips, or impact chains only when they reduce explanation effort.
9. Prefer prompt-driven HTML composition over deterministic templates unless the user asks otherwise.

## Presenter View

1. Detect presenter mode with `?view=presenter` and apply `presenter-mode` to `<body>`.
2. Audience view includes a `P` keybind that opens `location.pathname + '?view=presenter'`.
3. Presenter layout is split-screen: current slide preview on the left; next title, elapsed timer, notes, controls, and status on the right.
4. Store notes in `data-notes` on each slide.
5. Support Arrow keys, Page Up/Down, Home, End in both windows; presenter prev/next buttons also navigate.
6. Sync windows with `BroadcastChannel('slideshow-sync')` and `localStorage` fallback. Use `skipBroadcast: true` on sync receivers to avoid echo loops.

## Slide And Notes Rules

1. Keep slides concise, objective, and visually clear; keep fuller explanation in presenter notes.
2. Notes must sound like a normal team member in an internal weekly review, not a keynote, performance, marketing copy, or motivational speech.
3. Notes must add context, evidence, and interpretation that the slide does not already show.
4. For ticket-specific notes, explain what the ticket addressed, what was done, how it was checked, current state, and why the audience should care.
5. Use plain verbs such as `worked on`, `checked`, `verified`, `updated`, `fixed`, `reviewed`, `moved`, `left open`, and `followed up`.
6. Follow [`references/presentation-script-guidance.md`](references/presentation-script-guidance.md) for detailed presenter-note style and delivery checks.
7. Before final HTML, run slide body text and presenter notes through `$avoid-ai-writing` in detect mode with the `blog` context profile. Fix all P0/P1 flags and unambiguous P2 issues.

## Non-Negotiables

1. Do not act as the source-analysis layer when an upstream brief exists.
2. Do not collapse in-depth ticket sections into vague theme slides unless the user requests compression.
3. Do not make routine work sound dramatic or inflated.
4. Do not duplicate slide text verbatim in notes.
5. Create missing output directories before writing.
