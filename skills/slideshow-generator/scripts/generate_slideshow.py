#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

REQUIRED_DECK_KEYS = ["title", "generatedAt", "slides"]
REQUIRED_SLIDE_KEYS = ["type", "title"]
ALLOWED_LAYOUTS = {"hero", "two-column", "timeline-focus", "chart-focus", "comparison", "dense-notes"}
ALLOWED_VISUALS = {"kpi-strip", "status-bars", "trend-line", "flow-nodes", "relationship-map", "risk-matrix"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a generic slideshow from JSON payload.")
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
    for idx, slide in enumerate(payload["slides"]):
        if not isinstance(slide, dict):
            raise ValueError(f"Slide at index {idx} must be an object")
        for key in REQUIRED_SLIDE_KEYS:
            if key not in slide:
                raise ValueError(f"Slide at index {idx} missing required field: {key}")
        render_plan = slide.get("renderPlan")
        if render_plan is not None:
            validate_render_plan(render_plan, idx)


def validate_render_plan(render_plan: dict, idx: int) -> None:
    if not isinstance(render_plan, dict):
        raise ValueError(f"Slide at index {idx} has invalid renderPlan; expected object")
    layout = render_plan.get("layout")
    if layout is not None and layout not in ALLOWED_LAYOUTS:
        raise ValueError(f"Slide at index {idx} has unknown renderPlan.layout '{layout}'")
    regions = render_plan.get("regions")
    if regions is not None and not isinstance(regions, dict):
        raise ValueError(f"Slide at index {idx} has invalid renderPlan.regions; expected object")
    visuals = render_plan.get("visuals")
    if visuals is not None:
        if not isinstance(visuals, list):
            raise ValueError(f"Slide at index {idx} has invalid renderPlan.visuals; expected array")
        for v_idx, visual in enumerate(visuals):
            if not isinstance(visual, dict):
                raise ValueError(f"Slide at index {idx} renderPlan.visuals[{v_idx}] must be an object")
            v_type = visual.get("type")
            if v_type not in ALLOWED_VISUALS:
                raise ValueError(f"Slide at index {idx} has unknown visual type '{v_type}'")
    emphasis = render_plan.get("emphasis")
    if emphasis is not None and not isinstance(emphasis, list):
        raise ValueError(f"Slide at index {idx} has invalid renderPlan.emphasis; expected array")
    constraints = render_plan.get("constraints")
    if constraints is not None and not isinstance(constraints, dict):
        raise ValueError(f"Slide at index {idx} has invalid renderPlan.constraints; expected object")


def load_asset(asset_dir: Path, name: str) -> str:
    return (asset_dir / name).read_text(encoding="utf-8")


def render_html(payload: dict, output_dir: Path, asset_dir: Path) -> None:
    css = load_asset(asset_dir, "slides.css")
    audience_js = load_asset(asset_dir, "audience.js")
    presenter_js = load_asset(asset_dir, "presenter.js")

    index_html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{payload.get("title", "Slideshow")}</title>
  <style>{css}</style>
</head>
<body>
  <main id=\"app\"></main>
  <script>window.SLIDE_DATA = {json.dumps(payload)};</script>
  <script>{audience_js}</script>
</body>
</html>
"""

    presenter_html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Presenter View - {payload.get("title", "Slideshow")}</title>
  <style>{css}</style>
</head>
<body class=\"presenter-body\">
  <main id=\"presenter-app\"></main>
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
