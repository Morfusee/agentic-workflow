#!/usr/bin/env python3
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

WEEK_RE = re.compile(r"^\d{4}-W\d{2}$")
DUMP_FILE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-ticket-dump(?:-\d+)?\.md$")
TICKET_HEADER_RE = re.compile(r"^##\s+(?:\[)?([A-Z0-9-]+)(?:\])?:\s+(.+?)\s*$")
TIMELINE_EVENT_RE = re.compile(r"^-\s+([^\s]+)\s+(.+)$")
DAY_MAP_RE = re.compile(r"^-\s+(\d{4}-\d{2}-\d{2}):\s+(.+)$")
UNRESOLVED_STATUSES = {"done", "completed", "cancelled", "canceled"}
RISK_KEYWORDS = ("block", "blocked", "risk", "incident", "urgent", "delay", "dependency", "failure", "error")
DEPENDENCY_KEYWORDS = ("dependency", "depends on", "waiting on", "blocked by")
MOMENTUM_KEYWORDS = ("merged", "shipped", "released", "completed", "resolved", "closed")


@dataclass
class TicketRecord:
    ticket_id: str
    title: str
    status: str = "Unknown"
    url: str = "Not available"
    activity_date: str = "Unknown"
    role: str = "Unknown"
    notes: list[str] = field(default_factory=list)
    timeline_events: list[dict[str, str]] = field(default_factory=list)
    day_events: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class UnifiedTicket:
    ticket_id: str
    title: str
    statuses: list[str]
    url: str
    role: str
    timeline_events: list[dict[str, str]]
    notes: list[str]
    day_events: dict[str, list[str]]
    first_event_ts: str
    last_event_ts: str
    current_status: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate weekly insight-first ticket deck.")
    parser.add_argument("--week", help="ISO week folder name (e.g. 2026-W20).")
    parser.add_argument("--input-root", default="memory/tickets", help="Ticket dump root directory.")
    parser.add_argument("--output-root", default="memory/tickets", help="Output root directory.")
    parser.add_argument(
        "--renderer-script",
        default="skills/slideshow-generator/scripts/generate_slideshow.py",
        help="Path to generic slideshow renderer script.",
    )
    parser.add_argument("--python-bin", default=sys.executable, help="Python executable for invoking generic renderer.")
    parser.add_argument("--renderer", choices=["reveal-single", "legacy"], default="reveal-single")
    parser.add_argument("--reveal-assets-root", default="skills/weekly-ticket-slideshow-generator/assets/vendor/reveal")
    parser.add_argument("--reveal-theme", default="black")
    return parser.parse_args()


def resolve_week(input_root: Path, week: str | None) -> str:
    if week:
        if not WEEK_RE.match(week):
            raise ValueError(f"Invalid week format: {week}. Expected YYYY-W##.")
        target = input_root / week
        if not target.exists():
            raise FileNotFoundError(f"Week folder not found: {target}")
        return week
    week_dirs = sorted(p.name for p in input_root.iterdir() if p.is_dir() and WEEK_RE.match(p.name))
    if not week_dirs:
        raise FileNotFoundError(f"No week folders found under {input_root}")
    return week_dirs[-1]


def list_dump_files(week_dir: Path) -> list[Path]:
    return sorted(p for p in week_dir.iterdir() if p.is_file() and DUMP_FILE_RE.match(p.name))


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_tickets_section(text: str) -> list[TicketRecord]:
    marker = "# All Scraped Tickets"
    idx = text.find(marker)
    if idx == -1:
        return []
    lines = text[idx + len(marker) :].splitlines()
    tickets: list[TicketRecord] = []
    current: TicketRecord | None = None
    section = ""

    for raw in lines:
        line = raw.rstrip("\n")
        header_match = TICKET_HEADER_RE.match(line.strip())
        if header_match:
            if current:
                tickets.append(current)
            current = TicketRecord(ticket_id=header_match.group(1), title=normalize_space(header_match.group(2)))
            section = ""
            continue

        if current is None:
            continue

        stripped = line.strip()
        if stripped.startswith("Status:"):
            current.status = normalize_space(stripped.split(":", 1)[1])
        elif stripped.startswith("URL:"):
            current.url = normalize_space(stripped.split(":", 1)[1])
        elif stripped.startswith("Activity date:"):
            current.activity_date = normalize_space(stripped.split(":", 1)[1])
        elif stripped.startswith("My role for this ticket:"):
            current.role = normalize_space(stripped.split(":", 1)[1])
        elif stripped == "### Activity Timeline":
            section = "timeline"
        elif stripped == "### In-Range Day Mapping":
            section = "day-map"
        elif stripped == "### Activity Notes":
            section = "notes"
        elif stripped.startswith("### "):
            section = ""
        elif section == "timeline" and stripped.startswith("-"):
            m = TIMELINE_EVENT_RE.match(stripped)
            if m:
                current.timeline_events.append({"timestamp": m.group(1), "event": normalize_space(m.group(2))})
        elif section == "day-map" and stripped.startswith("-"):
            m = DAY_MAP_RE.match(stripped)
            if m:
                day = m.group(1)
                acts = [normalize_space(part) for part in m.group(2).split(";") if normalize_space(part)]
                current.day_events.setdefault(day, []).extend(acts)
        elif section == "notes" and stripped:
            current.notes.append(stripped)

    if current:
        tickets.append(current)
    return tickets


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def fallback_ts(day: str) -> str:
    return f"{day}T00:00:00+00:00"


def merge_records(records: list[TicketRecord]) -> list[UnifiedTicket]:
    grouped: dict[str, list[TicketRecord]] = {}
    for record in records:
        grouped.setdefault(record.ticket_id, []).append(record)

    unified: list[UnifiedTicket] = []
    for ticket_id, items in grouped.items():
        title = items[-1].title
        url = next((x.url for x in items if x.url and x.url != "Not available"), "Not available")
        role = next((x.role for x in items if x.role and x.role != "Unknown"), "Unknown")

        statuses: list[str] = []
        notes: list[str] = []
        day_events: dict[str, list[str]] = {}
        timeline_events: list[dict[str, str]] = []

        for item in items:
            if item.status and item.status not in statuses:
                statuses.append(item.status)
            notes.extend(item.notes)
            for day, events in item.day_events.items():
                day_events.setdefault(day, []).extend(events)
            timeline_events.extend(item.timeline_events)

        if not timeline_events:
            for item in items:
                if re.match(r"^\d{4}-\d{2}-\d{2}$", item.activity_date):
                    timeline_events.append(
                        {
                            "timestamp": fallback_ts(item.activity_date),
                            "event": f"activity snapshot (status {item.status})",
                        }
                    )

        seen: set[tuple[str, str]] = set()
        deduped_timeline: list[dict[str, str]] = []
        for event in timeline_events:
            key = (event["timestamp"], event["event"])
            if key in seen:
                continue
            seen.add(key)
            deduped_timeline.append(event)

        deduped_timeline.sort(key=lambda x: parse_ts(x["timestamp"]))
        current_status = statuses[-1] if statuses else "Unknown"
        first_event_ts = deduped_timeline[0]["timestamp"] if deduped_timeline else "Unknown"
        last_event_ts = deduped_timeline[-1]["timestamp"] if deduped_timeline else "Unknown"

        unified.append(
            UnifiedTicket(
                ticket_id=ticket_id,
                title=title,
                statuses=statuses,
                url=url,
                role=role,
                timeline_events=deduped_timeline,
                notes=notes,
                day_events=day_events,
                first_event_ts=first_event_ts,
                last_event_ts=last_event_ts,
                current_status=current_status,
            )
        )

    unified.sort(key=lambda t: parse_ts(t.first_event_ts) if t.first_event_ts != "Unknown" else datetime.max)
    return unified


def _is_resolved(status: str) -> bool:
    return status.lower() in UNRESOLVED_STATUSES


def _status_transition_count(statuses: list[str]) -> int:
    if not statuses:
        return 0
    return max(len(statuses) - 1, 0)


def _extract_issue(ticket: UnifiedTicket) -> str:
    corpus = [ticket.title] + ticket.notes + [e.get("event", "") for e in ticket.timeline_events]
    for text in corpus:
        low = text.lower()
        if any(word in low for word in RISK_KEYWORDS):
            return normalize_space(text)
    if _is_resolved(ticket.current_status):
        return "No active issue remains; ticket appears resolved."
    return "Issue is implied by unresolved status, but details are sparse in source notes."


def _extract_dependencies(ticket: UnifiedTicket) -> list[dict[str, str]]:
    deps: list[dict[str, str]] = []
    corpus = ticket.notes + [e.get("event", "") for e in ticket.timeline_events]
    for line in corpus:
        low = line.lower()
        if "depends on" in low:
            part = line.split("depends on", 1)[1].strip(" .:;")
            deps.append({"from": ticket.ticket_id, "to": part or "upstream task"})
        elif "blocked by" in low:
            part = line.split("blocked by", 1)[1].strip(" .:;")
            deps.append({"from": ticket.ticket_id, "to": part or "blocking issue"})
        elif "dependency" in low:
            deps.append({"from": ticket.ticket_id, "to": normalize_space(line)})
    return deps[:5]


def _risk_level(ticket: UnifiedTicket, issue: str) -> str:
    text = " ".join([ticket.title, issue] + ticket.notes).lower()
    score = sum(text.count(word) for word in RISK_KEYWORDS)
    if not _is_resolved(ticket.current_status):
        score += 2
    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def _has_dependency(ticket: UnifiedTicket) -> bool:
    text = " ".join(ticket.notes + [e.get("event", "") for e in ticket.timeline_events]).lower()
    return any(keyword in text for keyword in DEPENDENCY_KEYWORDS)


def _has_blocker(ticket: UnifiedTicket) -> bool:
    text = " ".join(ticket.notes + [e.get("event", "") for e in ticket.timeline_events]).lower()
    return "block" in text or "blocked" in text


def _suppress_obvious_text(text: str, title: str, status: str) -> str:
    visible = normalize_space(f"{title} {status}").lower()
    raw = normalize_space(text)
    if not raw:
        return raw
    words = [w for w in re.sub(r"[^a-z0-9\s]", " ", raw.lower()).split() if len(w) > 2]
    if not words:
        return raw
    visible_set = set(re.sub(r"[^a-z0-9\s]", " ", visible).split())
    overlap = sum(1 for w in words if w in visible_set) / len(words)
    has_value = any(
        cue in raw.lower()
        for cue in ("because", "impact", "risk", "decision", "next", "therefore", "dependency", "blocker", "if")
    )
    if overlap >= 0.65 and not has_value:
        return ""
    return raw


def _pick_visual_spec(signals: dict[str, Any], ticket: UnifiedTicket, issue: str, impact: str, actions: list[str]) -> dict[str, Any]:
    flow_steps = [normalize_space(e.get("event", "")) for e in ticket.timeline_events[:5] if normalize_space(e.get("event", ""))]
    dependencies = _extract_dependencies(ticket)
    chips = [f"Role: {ticket.role}", f"Status: {ticket.current_status}", f"Risk: {signals['riskLevel']}"]

    if signals["hasDependency"]:
        primary = "dependency-map"
        secondary = "action-ladder"
    elif signals["hasBlocker"] or signals["riskLevel"] == "high":
        primary = "issue-impact-chain"
        secondary = "action-ladder"
    elif signals["statusTransitions"] >= 2 or signals["eventDepth"] >= 3:
        primary = "state-lane-flow"
        secondary = "context-chips"
    else:
        primary = "context-chips"
        secondary = "action-ladder"

    return {
        "primaryVisual": primary,
        "secondaryVisual": secondary,
        "entities": {
            "flowSteps": flow_steps or ["Single-step update"],
            "dependencies": dependencies or ([{"from": ticket.ticket_id, "to": "No hard dependency detected"}] if signals["hasDependency"] else []),
            "issueImpact": {"issue": issue, "impact": impact, "mitigation": actions[0] if actions else "Monitor progress."},
            "chips": chips,
        },
    }


def _make_insight(ticket: UnifiedTicket) -> str:
    if not ticket.timeline_events:
        return f"{ticket.ticket_id} had sparse activity logs; status ended at {ticket.current_status}."
    start = ticket.timeline_events[0]
    end = ticket.timeline_events[-1]
    return f"Moved from '{start['event']}' to '{end['event']}' and closed the week at status {ticket.current_status}."


def _make_context(ticket: UnifiedTicket, issue: str) -> str:
    details = issue if issue else "No explicit issue note captured."
    return f"Current context suggests {details}"


def _make_decision(ticket: UnifiedTicket, signals: dict[str, Any]) -> str:
    if _is_resolved(ticket.current_status):
        return "No escalation decision required; keep lightweight monitoring for regression."
    if signals["hasDependency"]:
        return "Decision needed: align upstream owner and lock dependency handoff timing."
    if signals["hasBlocker"]:
        return "Decision needed: prioritize blocker removal and confirm accountable owner today."
    return "Decision needed: set closure owner and target completion checkpoint."


def _make_actions(ticket: UnifiedTicket, signals: dict[str, Any]) -> list[str]:
    actions = []
    if signals["hasDependency"]:
        actions.append("Schedule dependency sync and confirm delivery handoff path.")
    if signals["hasBlocker"]:
        actions.append("Escalate blocker with owner and request unblock ETA.")
    if not _is_resolved(ticket.current_status):
        actions.append("Assign explicit closure owner for this cycle.")
        actions.append("Publish next status checkpoint with closure criteria.")
    else:
        actions.append("Validate post-resolution behavior and close follow-up checks.")
    return actions[:4]


def _make_speaker_script(ticket: UnifiedTicket, insight: str, context: str, decision: str, actions: list[str]) -> str:
    open_line = f"{ticket.ticket_id} moved this week with a clear outcome signal."
    action_line = actions[0] if actions else "Continue monitoring and report back next cycle."
    return "\n\n".join(
        [
            open_line,
            f"The non-obvious takeaway is: {insight}",
            f"Context to anchor the room: {context}",
            f"The decision point for the team: {decision}",
            f"My recommended immediate action: {action_line}",
        ]
    )


def _build_content_slide(ticket: UnifiedTicket) -> dict[str, Any]:
    issue = _extract_issue(ticket)
    risk = _risk_level(ticket, issue)
    signals = {
        "hasBlocker": _has_blocker(ticket),
        "hasDependency": _has_dependency(ticket),
        "statusTransitions": _status_transition_count(ticket.statuses),
        "riskLevel": risk,
        "eventDepth": len(ticket.timeline_events),
    }
    insight = _suppress_obvious_text(_make_insight(ticket), ticket.title, ticket.current_status) or _make_insight(ticket)
    context = _suppress_obvious_text(_make_context(ticket, issue), ticket.title, ticket.current_status) or _make_context(ticket, issue)
    decision = _suppress_obvious_text(_make_decision(ticket, signals), ticket.title, ticket.current_status) or _make_decision(ticket, signals)
    impact = "delivery risk remains active until closure." if not _is_resolved(ticket.current_status) else "delivery impact appears contained."
    actions = _make_actions(ticket, signals)
    visual_spec = _pick_visual_spec(signals, ticket, issue, impact, actions)
    script = _make_speaker_script(ticket, insight, context, decision, actions)

    return {
        "type": "content",
        "title": f"{ticket.ticket_id}: {ticket.title}",
        "status": ticket.current_status,
        "insight": insight,
        "context": context,
        "decision": decision,
        "actions": actions,
        "signals": signals,
        "visualSpec": visual_spec,
        "speakerScript": script,
        "meta": {"role": ticket.role, "ticketUrl": ticket.url, "lastUpdated": ticket.last_event_ts},
    }


def _status_counts(tickets: list[UnifiedTicket]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for ticket in tickets:
        key = ticket.current_status or "Unknown"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[0].lower()))


def _week_overview_script(week: str, total: int, unresolved: int) -> str:
    return "\n\n".join(
        [
            f"This week {week} includes {total} tracked tickets.",
            f"{unresolved} tickets remain unresolved and define the active risk envelope.",
            "We will focus on what changed materially, what risks remain, and what actions close them.",
        ]
    )


def build_payload(week: str, tickets: list[UnifiedTicket]) -> dict[str, Any]:
    unresolved = [ticket for ticket in tickets if not _is_resolved(ticket.current_status)]
    status_counts = _status_counts(tickets)
    slides: list[dict[str, Any]] = [
        {
            "type": "opening",
            "title": f"Weekly Ticket Report - {week}",
            "insight": f"{len(tickets)} tickets reviewed; {len(unresolved)} still require closure.",
            "speakerScript": _week_overview_script(week, len(tickets), len(unresolved)),
        }
    ]

    slides.extend(_build_content_slide(ticket) for ticket in tickets)

    closing_actions = [f"{ticket.ticket_id}: assign owner and closure checkpoint." for ticket in unresolved] or [
        "All tracked tickets are resolved; continue monitoring for regressions."
    ]
    slides.append(
        {
            "type": "closing",
            "title": "Risk Closure Commitments",
            "insight": "Close remaining risks through explicit ownership and dependency alignment.",
            "speakerScript": "\n\n".join(
                [
                    "Closing on unresolved risk commitments.",
                    "Each remaining ticket needs an owner and closure checkpoint before next report.",
                    "If dependencies remain, we escalate alignment immediately.",
                ]
            ),
            "actions": closing_actions[:6],
            "meta": {"statusCounts": status_counts},
        }
    )

    generated_at = "1970-01-01T00:00:00+00:00"
    known_last = [ticket.last_event_ts for ticket in tickets if ticket.last_event_ts != "Unknown"]
    if known_last:
        generated_at = sorted(known_last)[-1]

    return {
        "title": f"Weekly Ticket Report - {week}",
        "subtitle": "Insight-first deck generated from weekly ticket dumps",
        "generatedAt": generated_at,
        "presentationPolicy": {
            "textPolicy": "strict-summary",
            "diagramPolicy": "signal-required",
            "styleProfile": "narrative-cards",
        },
        "context": {"week": week, "ticketCount": len(tickets), "unresolvedCount": len(unresolved), "statusCounts": status_counts},
        "slides": slides,
    }


def invoke_renderer(python_bin: str, renderer_script: Path, payload_path: Path, output_dir: Path) -> None:
    command = [python_bin, str(renderer_script), "--input", str(payload_path), "--output", str(output_dir), "--theme", "default"]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            "Generic slideshow renderer failed\n"
            f"Command: {' '.join(command)}\n"
            f"STDOUT:\n{completed.stdout}\n"
            f"STDERR:\n{completed.stderr}"
        )
    if completed.stdout.strip():
        print(completed.stdout.strip())


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Required asset file not found: {path}")
    return path.read_text(encoding="utf-8")


def _render_notes(script: str) -> str:
    lines = [html.escape(line.strip()) for line in script.splitlines() if line.strip()]
    if not lines:
        return ""
    items = "".join(f"<li>{line}</li>" for line in lines)
    return f'<aside class="notes"><ul class="notes-list">{items}</ul></aside>'


def _render_visual(slide: dict[str, Any]) -> str:
    if slide.get("type") != "content":
        return ""
    spec = slide.get("visualSpec", {})
    primary = spec.get("primaryVisual", "none")
    entities = spec.get("entities", {})
    if primary == "state-lane-flow":
        steps = entities.get("flowSteps", [])[:5]
        cards = "".join(f'<span class="flow-step">{html.escape(step)}</span>' for step in steps)
        return f'<div class="visual flow">{cards}</div>'
    if primary == "dependency-map":
        deps = entities.get("dependencies", [])[:5]
        cards = "".join(
            f'<div class="dep"><strong>{html.escape(dep.get("from", ""))}</strong><span>depends on</span><p>{html.escape(dep.get("to", ""))}</p></div>'
            for dep in deps
        )
        return f'<div class="visual deps">{cards}</div>'
    if primary == "issue-impact-chain":
        chain = entities.get("issueImpact", {})
        return (
            '<div class="visual chain">'
            f'<p><strong>Issue:</strong> {html.escape(chain.get("issue", ""))}</p>'
            f'<p><strong>Impact:</strong> {html.escape(chain.get("impact", ""))}</p>'
            f'<p><strong>Mitigation:</strong> {html.escape(chain.get("mitigation", ""))}</p>'
            "</div>"
        )
    chips = entities.get("chips", [])
    chip_html = "".join(f'<span class="chip">{html.escape(chip)}</span>' for chip in chips)
    return f'<div class="visual chips">{chip_html}</div>'


def _render_slide(slide: dict[str, Any]) -> str:
    title = html.escape(str(slide.get("title", "")))
    insight = html.escape(str(slide.get("insight", "")))
    script = str(slide.get("speakerScript", ""))
    notes = _render_notes(script)

    if slide.get("type") == "content":
        context = html.escape(str(slide.get("context", "")))
        decision = html.escape(str(slide.get("decision", "")))
        actions = slide.get("actions", [])
        actions_html = "".join(f"<li>{html.escape(str(action))}</li>" for action in actions[:4])
        visual = _render_visual(slide)
        return (
            '<section class="ticket-slide">'
            f'<header><h2>{title}</h2></header>'
            '<div class="grid">'
            f'<article class="panel"><h3>Insight</h3><p>{insight}</p></article>'
            f'<article class="panel"><h3>Why This Matters</h3><p>{context}</p></article>'
            f'<article class="panel"><h3>Decision Needed</h3><p>{decision}</p></article>'
            f'<article class="panel"><h3>Next Actions</h3><ul>{actions_html}</ul></article>'
            f'<article class="panel visual-panel">{visual}</article>'
            "</div>"
            f"{notes}"
            "</section>"
        )

    actions = slide.get("actions", [])
    action_html = "".join(f"<li>{html.escape(str(action))}</li>" for action in actions[:6])
    extra = f"<ul>{action_html}</ul>" if action_html else ""
    return (
        "<section>"
        f"<h2>{title}</h2>"
        f"<p>{insight}</p>"
        f"{extra}"
        f"{notes}"
        "</section>"
    )


def _safe_json_script_payload(value: str) -> str:
    return json.dumps(value).replace("</", "<\\/")


def render_reveal_single_file(payload: dict[str, Any], out_file: Path, assets_root: Path, theme_name: str) -> None:
    reveal_js = read_text(assets_root / "dist" / "reveal.js")
    reveal_css = read_text(assets_root / "dist" / "reveal.css")
    reveal_theme_css = read_text(assets_root / "dist" / "theme" / f"{theme_name}.css")
    notes_js = read_text(assets_root / "plugin" / "notes" / "notes.js")

    sections = "".join(_render_slide(slide) for slide in payload.get("slides", []))
    reveal_js_json = _safe_json_script_payload(reveal_js)
    reveal_css_json = _safe_json_script_payload(reveal_css)
    reveal_theme_css_json = _safe_json_script_payload(reveal_theme_css)
    notes_js_json = _safe_json_script_payload(notes_js)

    title = html.escape(str(payload.get("title", "Weekly Ticket Report")))
    subtitle = html.escape(str(payload.get("subtitle", "")))

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    body {{ margin: 0; background: #020617; }}
    .reveal .slides section {{ text-align: left; padding: 24px 36px; }}
    .ticket-slide .grid {{ display: grid; grid-template-columns: 1fr 1fr 1.1fr; gap: 12px; }}
    .panel {{ border: 1px solid rgba(148,163,184,.35); border-radius: 10px; background: rgba(15,23,42,.6); padding: 10px; }}
    .panel h3 {{ margin: 0 0 8px 0; font-size: 16px; text-transform: uppercase; letter-spacing: .04em; }}
    .panel p {{ margin: 0; font-size: 18px; line-height: 1.35; }}
    .panel ul {{ margin: 0; padding-left: 20px; }}
    .visual.chips {{ display: flex; gap: 6px; flex-wrap: wrap; }}
    .chip {{ border-radius: 999px; border: 1px solid rgba(148,163,184,.55); padding: 4px 10px; font-size: 13px; }}
    .visual.flow {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .flow-step {{ border: 1px solid rgba(148,163,184,.5); padding: 6px 10px; border-radius: 999px; font-size: 13px; }}
    .visual.deps {{ display: grid; gap: 8px; }}
    .dep {{ border: 1px dashed rgba(148,163,184,.45); border-radius: 8px; padding: 8px; }}
    .dep strong {{ display: block; }}
    .dep span {{ display: inline-block; font-size: 11px; text-transform: uppercase; color: #7dd3fc; margin-top: 3px; }}
    .dep p {{ margin: 4px 0 0 0; font-size: 14px; }}
    .visual.chain p {{ margin: 6px 0; font-size: 14px; }}
    .notes-list {{ margin: 0; padding-left: 16px; }}
    .notes-list li {{ margin: 4px 0; }}
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <section>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </section>
      {sections}
    </div>
  </div>
  <script id="asset-reveal-css" type="application/json">{reveal_css_json}</script>
  <script id="asset-reveal-theme-css" type="application/json">{reveal_theme_css_json}</script>
  <script id="asset-reveal-js" type="application/json">{reveal_js_json}</script>
  <script id="asset-notes-js" type="application/json">{notes_js_json}</script>
  <script>
    (function() {{
      function parseJsonText(id) {{
        var el = document.getElementById(id);
        if (!el) throw new Error("Missing asset payload: " + id);
        return JSON.parse(el.textContent || '""');
      }}
      function injectStyle(css) {{
        var style = document.createElement("style");
        style.textContent = css;
        document.head.appendChild(style);
      }}
      function injectScript(js) {{
        var script = document.createElement("script");
        script.text = js;
        document.body.appendChild(script);
      }}
      injectStyle(parseJsonText("asset-reveal-css"));
      injectStyle(parseJsonText("asset-reveal-theme-css"));
      injectScript(parseJsonText("asset-reveal-js"));
      injectScript(parseJsonText("asset-notes-js"));
      Reveal.initialize({{
        hash: true,
        controls: true,
        progress: true,
        center: false,
        transition: "slide",
        plugins: [RevealNotes]
      }});
    }})();
  </script>
</body>
</html>
"""

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html_doc, encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_root = Path(args.input_root)
    week = resolve_week(input_root, args.week)
    week_dir = input_root / week
    dump_files = list_dump_files(week_dir)

    all_records: list[TicketRecord] = []
    for path in dump_files:
        all_records.extend(parse_tickets_section(path.read_text(encoding="utf-8")))

    unified = merge_records(all_records)
    payload = build_payload(week, unified)

    out_dir = Path(args.output_root) / week
    out_dir.mkdir(parents=True, exist_ok=True)

    payload_path = out_dir / f"{week}-weekly-ticket-slides.json"
    payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    week_payload_copy = out_dir / f"{week}-weekly-ticket-slideshow.json"
    week_payload_copy.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    week_reveal_path = out_dir / f"{week}-weekly-ticket-slideshow-reveal.html"
    week_deck_path = out_dir / f"{week}-weekly-ticket-slideshow.html"
    week_presenter_path = out_dir / f"{week}-weekly-ticket-slideshow-presenter.html"

    if args.renderer == "reveal-single":
        render_reveal_single_file(payload, week_reveal_path, Path(args.reveal_assets_root), args.reveal_theme)
    else:
        renderer_script = Path(args.renderer_script)
        invoke_renderer(args.python_bin, renderer_script, payload_path, out_dir)
        shutil.copy2(out_dir / "index.html", week_deck_path)
        shutil.copy2(out_dir / "presenter.html", week_presenter_path)
        shutil.copy2(out_dir / "slides.json", week_payload_copy)

    unresolved = payload.get("context", {}).get("unresolvedCount", 0)
    print(f"Week: {week}")
    print(f"Dump files: {len(dump_files)}")
    print(f"Unified tickets: {len(unified)}")
    print(f"Slides: {len(payload.get('slides', []))}")
    print(f"Unresolved tickets: {unresolved}")
    print(f"Wrapper payload: {payload_path}")
    if args.renderer == "reveal-single":
        print(f"Reveal single-file deck: {week_reveal_path}")
    else:
        print(f"Audience deck: {out_dir / 'index.html'}")
        print(f"Presenter view: {out_dir / 'presenter.html'}")
        print(f"Week deck file: {week_deck_path}")
        print(f"Week presenter file: {week_presenter_path}")
    print(f"Week payload file: {week_payload_copy}")


if __name__ == "__main__":
    main()
