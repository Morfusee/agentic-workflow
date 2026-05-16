---
name: slideshow-generator
description: Render a presentation-grade fullscreen HTML slideshow from structured presentation information. Use when slide layout, pacing, presenter notes, and visual treatment need to be composed from an upstream brief such as the output of $weekly-ticket-slideshow-generator.
---

# Slideshow Generator

Render a domain-agnostic, audience-friendly HTML slideshow directly in the final output from a structured brief or presentation payload.

Treat this skill as the presentation layer only:
- accept structured information from upstream skills
- compose audience-facing slides from that information
- generate presenter notes and presenter-view behavior
- output audience and presenter HTML
- do not act as the source-analysis layer when an upstream brief already exists

## Presentation Contract

1. Keep slides supplementary to the presenter, not a transcript.
2. Prioritize clear explanation over style, hype, or stage voice.
3. Keep each slide visually clear at a glance:
- short statements
- strong hierarchy
- one primary message per panel
4. Use visuals only when they reduce explanation effort for the audience.
5. Avoid dense detail dumps, risk-heavy wording, and repeated phrasing across adjacent slides.
6. Keep wording plain and useful for an internal weekly review.
7. Prefer prompt-driven HTML composition over deterministic template rendering.
8. Do not re-analyze raw weekly dump files when an upstream interpretation brief is already available.
9. If the upstream brief preserves ticket-level sections for in-depth coverage, do not collapse them back into high-level theme slides.

## Output Contract

1. Generate final HTML directly.
2. Use Reveal-compatible slide sections when a slideshow framework is helpful.
3. Keep visible text scannable within five to eight seconds.
4. Keep the strongest message visually dominant on each slide.
5. Keep speaker notes natural and non-duplicative with visible text.
6. Vary layout, grouping, emphasis, and visual treatment when the content benefits from it.
7. Use diagrams, flows, cards, and chips only when they clarify the story.
8. If a structured payload or weekly brief is provided, treat it as the interpretation source-of-truth and focus on slide composition, pacing, and notes.
9. Preserve the depth requested by the upstream brief: if the brief is ticket-specific, keep the deck ticket-specific unless the user asks for compression.
10. Generate a presenter view together with the audience deck by default.
11. Put the presenter view behind a keybind on the main deck so it can be opened from the same presentation file.
12. Follow the script guidance in [`references/presentation-script-guidance.md`](references/presentation-script-guidance.md).
13. Treat presenter notes as normal spoken delivery for an internal team update, not as a polished performance script.

## Rendering Rules

1. Build slides as narrative support, not as a transcript or exported data view.
2. Keep slide content supplementary to narration:
- prefer concise, objective summaries over technical detail
- avoid overcrowding text on any single slide
- use visuals only when they clarify flow or relationships
3. Keep presenter notes naturally spoken and not visibly duplicated on slide body text.
4. Prefer strong, purposeful slide variation:
- cards for theme grouping
- flow visuals for movement or momentum
- impact chains for problem-to-outcome stories
- action ladders for commitments and handoffs
5. Avoid decorative visual noise, repeated slide patterns, and text-heavy fallback layouts when a simpler card is clearer.
6. Do not default to repository `scripts/`, `assets/`, or `output/` folders as the primary workflow.
7. Use deterministic renderer code only when the user explicitly asks for that tradeoff.
8. Respect role boundaries:
- upstream skills gather and normalize source evidence
- `$slideshow-generator` turns that normalized information into audience and presenter experiences
9. Fit the deck inside a virtual `1920x1080` stage and scale it to the viewport.
10. Let text use the space available inside its parent container; do not set narrow width caps that force early wrapping unless the layout clearly requires it.
11. Keep the language on slides and in presenter notes simple and direct; do not use flowery or inflated wording.
12. Write presenter notes as full paragraph script that can be read aloud without the presenter having to invent transitions between bullet points.
13. Write presenter notes in normal spoken language for an internal weekly review:
- use simple transitions
- sound like a normal team member giving a status update
- do not sound like a keynote speaker
- do not sound edgy, dramatic, clever, or performative
- do not sound like marketing copy, an influencer, or a motivational speaker
- do not overstate routine work
14. Use plain verbs in notes, such as `worked on`, `checked`, `verified`, `updated`, `fixed`, `reviewed`, `moved`, `left open`, and `followed up`.
15. Use plain transitions in notes, such as `On this slide`, `Here`, `Next`, `After that`, `The next step is`, and `By the end of the week`.
16. Use slides as cues and notes as explanation; do not write notes that simply read the slide aloud.
17. Keep notes fuller than slides, but still natural enough to read out loud without sounding written for a stage talk.
18. When the brief includes one section per ticket, keep each ticket legible on its own slide or panel and show the concrete problem, action, validation, and state without flattening it into a theme-only summary.
