---
name: slideshow-generator
description: Render a presentation-grade fullscreen HTML slideshow directly from prompt-driven content. Use when slides must keep a clear narrative flow, stay concise, and visually support spoken delivery rather than mirror raw source material, and prefer LLM-authored HTML over deterministic render pipelines.
---

# Slideshow Generator

Render a domain-agnostic, audience-friendly HTML slideshow directly in the final output.

## Presentation Contract

1. Keep slides supplementary to the presenter, not a transcript.
2. Prioritize objective storytelling over technical diagnostics or raw ticket recitation.
3. Keep each slide visually clear at a glance:
- short statements
- strong hierarchy
- one primary message per panel
4. Use visuals only when they reduce explanation effort for the audience.
5. Avoid dense detail dumps, risk-heavy wording, and repeated phrasing across adjacent slides.
6. Treat the deck as a narrative artifact: each slide should answer why the audience should care, not just what happened.
7. Prefer prompt-driven HTML composition over deterministic template rendering.

## Output Contract

1. Generate final HTML directly.
2. Use Reveal-compatible slide sections when a slideshow framework is helpful.
3. Keep visible text scannable within five to eight seconds.
4. Keep the strongest message visually dominant on each slide.
5. Keep speaker notes natural and non-duplicative with visible text.
6. Vary layout, grouping, emphasis, and visual treatment when the content benefits from it.
7. Use diagrams, flows, cards, and chips only when they clarify the story.
8. If a structured payload is provided, treat it as guidance rather than a rigid rendering template unless the user explicitly asks for strict deterministic behavior.

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
