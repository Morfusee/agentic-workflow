---
name: slideshow-generator
description: Render an insight-first fullscreen HTML slideshow with synced presenter view from a strict JSON payload. Use when decks must avoid obvious restatement, emphasize narrative-card visuals, apply signal-based diagram gating, and provide polished speaker scripts.
---

# Slideshow Generator

Render a domain-agnostic, insight-first HTML slideshow from a strict payload contract.

## Input Contract (Hard Break)

Provide a JSON file with this shape:

```json
{
  "title": "Deck title",
  "subtitle": "Optional subtitle",
  "generatedAt": "ISO timestamp",
  "presentationPolicy": {
    "textPolicy": "strict-summary",
    "diagramPolicy": "signal-required",
    "styleProfile": "narrative-cards"
  },
  "context": {"week": "2026-W20"},
  "slides": [
    {
      "type": "content",
      "title": "Slide title",
      "status": "In Progress",
      "insight": "Non-obvious takeaway",
      "context": "Why this matters",
      "decision": "Decision required now",
      "actions": ["Action 1", "Action 2"],
      "signals": {
        "hasBlocker": true,
        "hasDependency": false,
        "statusTransitions": 2,
        "riskLevel": "high",
        "eventDepth": 4
      },
      "visualSpec": {
        "primaryVisual": "issue-impact-chain",
        "secondaryVisual": "action-ladder",
        "entities": {}
      },
      "speakerScript": "Presenter-ready prose script"
    }
  ]
}
```

Required per `content` slide:
- `insight`
- `context`
- `decision`
- `actions`
- `signals`
- `visualSpec`
- `speakerScript`

`visualSpec.primaryVisual` must be one of:
- `state-lane-flow`
- `dependency-map`
- `issue-impact-chain`
- `context-chips`
- `action-ladder`
- `none`

## Rendering Rules

1. Enforce strict payload validation. Reject missing required content fields.
2. Enforce strict anti-restatement when `presentationPolicy.textPolicy=strict-summary`.
3. Build content slides with narrative cards:
- Insight
- Why This Matters
- Decision Needed
- Next Actions
4. Gate heavy diagrams by signal policy:
- render diagrams when blocker/dependency/churn/depth thresholds are met
- otherwise render lightweight context visuals
5. Keep presenter script readable and paragraph-preserving in presenter view.
6. Keep audience/presenter synchronized through `BroadcastChannel` and `localStorage` fallback.

## Command

```powershell
python skills/slideshow-generator/scripts/generate_slideshow.py --input payload.json --output skills/slideshow-generator/output/sample --theme default
```
