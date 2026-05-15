#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

REQUIRED_DECK_KEYS = ["title", "generatedAt", "presentationPolicy", "slides"]
REQUIRED_POLICY_KEYS = ["textPolicy", "diagramPolicy", "styleProfile"]
REQUIRED_SLIDE_KEYS = ["type", "title"]
REQUIRED_CONTENT_KEYS = ["insight", "context", "decision", "actions", "signals", "visualSpec", "speakerScript"]
REQUIRED_SIGNAL_KEYS = ["hasBlocker", "hasDependency", "statusTransitions", "riskLevel", "eventDepth"]
REQUIRED_VISUAL_SPEC_KEYS = ["primaryVisual"]
ALLOWED_VISUALS = {
    "state-lane-flow",
    "dependency-map",
    "issue-impact-chain",
    "context-chips",
    "action-ladder",
    "none",
}
ALLOWED_RISK_LEVELS = {"low", "medium", "high"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an insight-first slideshow from JSON payload.")
    parser.add_argument("--input", required=True, help="Path to normalized payload JSON file.")
    parser.add_argument("--output", required=True, help="Output directory for rendered files.")
    parser.add_argument("--theme", default="default", help="Theme name. Currently supports only 'default'.")
    return parser.parse_args()


def validate_payload(payload: dict) -> None:
    for key in REQUIRED_DECK_KEYS:
        if key not in payload:
            raise ValueError(f"Payload missing required deck field: {key}")
    if not isinstance(payload["slides"], list):
        raise ValueError("Payload field 'slides' must be a list")
    validate_presentation_policy(payload["presentationPolicy"])
    for idx, slide in enumerate(payload["slides"]):
        validate_slide(slide, idx)


def validate_presentation_policy(policy: dict) -> None:
    if not isinstance(policy, dict):
        raise ValueError("presentationPolicy must be an object")
    for key in REQUIRED_POLICY_KEYS:
        if key not in policy:
            raise ValueError(f"presentationPolicy missing required key: {key}")


def validate_slide(slide: dict, idx: int) -> None:
    if not isinstance(slide, dict):
        raise ValueError(f"Slide at index {idx} must be an object")
    for key in REQUIRED_SLIDE_KEYS:
        if key not in slide:
            raise ValueError(f"Slide at index {idx} missing required field: {key}")
    if slide.get("type") == "content":
        validate_content_slide(slide, idx)


def validate_content_slide(slide: dict, idx: int) -> None:
    for key in REQUIRED_CONTENT_KEYS:
        if key not in slide:
            raise ValueError(f"Content slide at index {idx} missing required field: {key}")

    actions = slide.get("actions")
    if not isinstance(actions, list) or not all(isinstance(item, str) for item in actions):
        raise ValueError(f"Content slide at index {idx} has invalid actions; expected string array")

    signals = slide.get("signals")
    if not isinstance(signals, dict):
        raise ValueError(f"Content slide at index {idx} has invalid signals; expected object")
    for key in REQUIRED_SIGNAL_KEYS:
        if key not in signals:
            raise ValueError(f"Content slide at index {idx} signals missing required key: {key}")
    if not isinstance(signals["hasBlocker"], bool):
        raise ValueError(f"Content slide at index {idx} signals.hasBlocker must be boolean")
    if not isinstance(signals["hasDependency"], bool):
        raise ValueError(f"Content slide at index {idx} signals.hasDependency must be boolean")
    if not isinstance(signals["statusTransitions"], int) or signals["statusTransitions"] < 0:
        raise ValueError(f"Content slide at index {idx} signals.statusTransitions must be non-negative integer")
    if not isinstance(signals["eventDepth"], int) or signals["eventDepth"] < 0:
        raise ValueError(f"Content slide at index {idx} signals.eventDepth must be non-negative integer")
    if signals["riskLevel"] not in ALLOWED_RISK_LEVELS:
        raise ValueError(f"Content slide at index {idx} signals.riskLevel must be one of: {sorted(ALLOWED_RISK_LEVELS)}")

    visual_spec = slide.get("visualSpec")
    if not isinstance(visual_spec, dict):
        raise ValueError(f"Content slide at index {idx} has invalid visualSpec; expected object")
    for key in REQUIRED_VISUAL_SPEC_KEYS:
        if key not in visual_spec:
            raise ValueError(f"Content slide at index {idx} visualSpec missing required key: {key}")
    primary = visual_spec["primaryVisual"]
    secondary = visual_spec.get("secondaryVisual")
    if primary not in ALLOWED_VISUALS:
        raise ValueError(f"Content slide at index {idx} has unknown primaryVisual '{primary}'")
    if secondary is not None and secondary not in ALLOWED_VISUALS:
        raise ValueError(f"Content slide at index {idx} has unknown secondaryVisual '{secondary}'")

    script = slide.get("speakerScript")
    if not isinstance(script, str) or not script.strip():
        raise ValueError(f"Content slide at index {idx} speakerScript must be a non-empty string")


def load_asset(asset_dir: Path, name: str) -> str:
    return (asset_dir / name).read_text(encoding="utf-8")


def render_html(payload: dict, output_dir: Path, asset_dir: Path) -> None:
    css = load_asset(asset_dir, "slides.css")
    audience_js = load_asset(asset_dir, "audience.js")
    presenter_js = load_asset(asset_dir, "presenter.js")

    index_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{payload.get("title", "Slideshow")}</title>
  <style>{css}</style>
</head>
<body>
  <main id="app"></main>
  <script>window.SLIDE_DATA = {json.dumps(payload)};</script>
  <script>{audience_js}</script>
</body>
</html>
"""

    presenter_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Presenter View - {payload.get("title", "Slideshow")}</title>
  <style>{css}</style>
</head>
<body class="presenter-body">
  <main id="presenter-app"></main>
  <script>window.SLIDE_DATA = {json.dumps(payload)};</script>
  <script>{presenter_js}</script>
</body>
</html>
"""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "slides.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")
    (output_dir / "presenter.html").write_text(presenter_html, encoding="utf-8")


def main() -> None:
    args = parse_args()
    if args.theme != "default":
        raise ValueError("Only theme 'default' is currently supported")

    payload_path = Path(args.input)
    output_dir = Path(args.output)
    asset_dir = Path(__file__).resolve().parent.parent / "assets"

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    validate_payload(payload)
    render_html(payload, output_dir, asset_dir)

    print(f"Rendered slideshow: {output_dir / 'index.html'}")
    print(f"Rendered presenter view: {output_dir / 'presenter.html'}")
    print(f"Copied payload: {output_dir / 'slides.json'}")


if __name__ == "__main__":
    main()
