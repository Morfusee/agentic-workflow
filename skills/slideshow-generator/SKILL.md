---
name: slideshow-generator
description: Render a generic fullscreen HTML slideshow plus synced presenter view from a normalized JSON payload. Use when you need an agnostic deck renderer with meaningful visual composition (not text restatement), keyboard navigation, and presenter notes that contain a clear speaking script.
---

# Slideshow Generator

Render a domain-agnostic HTML slideshow from a JSON payload.
Prioritize interpretive slides: summarize what happened, why it matters, and what to do next, instead of repeating raw input text.

## Input Contract

Provide a JSON file with this shape:

```json
{
  "title": "Deck title",
  "subtitle": "Optional subtitle",
  "generatedAt": "ISO timestamp",
  "context": {"key": "value"},
  "slides": [
    {
      "type": "title|content|closing|empty",
      "title": "Slide title",
      "body": "Main text",
      "meta": ["line 1", "line 2"],
      "timeline": [{"timestamp": "...", "event": "..."}],
      "presenterNotes": "Spoken script",
      "status": "Optional status",
      "items": ["Optional bullet item"],
      "renderPlan": {
        "layout": "hero|two-column|timeline-focus|chart-focus|comparison|dense-notes",
        "regions": {"headline": "title", "timeline": "timeline"},
        "visuals": [{"type": "kpi-strip|status-bars|trend-line|flow-nodes|relationship-map|risk-matrix"}],
        "emphasis": ["risk", "momentum", "blockers"],
        "constraints": {"maxMetaItems": 4, "maxTimelineItems": 5, "maxBulletItems": 6}
      }
    }
  ],
  "renderDefaults": {
    "defaultLayout": "two-column",
    "constraints": {"maxMetaItems": 4, "maxTimelineItems": 5, "maxBulletItems": 6}
  }
}
```

`renderPlan` is optional. When missing, `$slideshow-generator` falls back to legacy rendering behavior.

`presenterNotes` should be written as a line-by-line script the presenter can read naturally. Prefer sections such as:
- `Slide goal:`
- `Say:`
- `What happened:`
- `Issue:`
- `Impact:`
- `Next step:`
- `Transition:`

## Execution Steps

1. Read and validate payload file.
2. Ensure required deck and slide fields exist, and validate optional `renderPlan` shape.
3. Render:
- `index.html` (audience)
- `presenter.html` (presenter)
- `slides.json` (copied payload)
4. Resolve layout and visual composition deterministically from `renderPlan` with stable fallback order.
5. Ensure each content slide includes interpretation-oriented structure (event flow, issue framing, impact, and next action), not only title/description restatement.
6. Ensure presenter notes are usable as spoken script during reporting.
7. Enable keys:
- `ArrowLeft`, `ArrowRight`, `Home`, `End`, `F`, `P`
8. Sync audience/presenter via `BroadcastChannel` with `localStorage` fallback.

## Command

```powershell
python skills/slideshow-generator/scripts/generate_slideshow.py --input payload.json --output skills/slideshow-generator/output/sample --theme default
```
