#!/usr/bin/env python3
import argparse
import json
import html
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
RISK_KEYWORDS = ("block", "blocked", "risk", "incident", "urgent", "delay", "dependency")
MOMENTUM_KEYWORDS = ("merged", "shipped", "released", "completed", "resolved", "closed")
ISSUE_KEYWORDS = ("block", "blocked", "risk", "incident", "urgent", "delay", "dependency", "failed", "error")


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
    parser = argparse.ArgumentParser(description="Generate weekly ticket flow slideshow via generic slideshow wrapper.")
    parser.add_argument("--week", help="ISO week folder name (e.g. 2026-W20).")
    parser.add_argument("--input-root", default="memory/tickets", help="Ticket dump root directory.")
    parser.add_argument("--output-root", default="memory/tickets", help="Output root directory. Week folder will be created or reused under this root.")
    parser.add_argument("--renderer-script", default="skills/slideshow-generator/scripts/generate_slideshow.py", help="Path to generic slideshow renderer script.")
    parser.add_argument("--python-bin", default=sys.executable, help="Python executable for invoking generic renderer.")
    parser.add_argument("--renderer", choices=["reveal-single", "legacy"], default="reveal-single", help="Renderer mode. 'reveal-single' outputs one bundled Reveal.js HTML file.")
    parser.add_argument("--reveal-assets-root", default="skills/weekly-ticket-slideshow-generator/assets/vendor/reveal", help="Root directory containing vendored Reveal.js assets.")
    parser.add_argument("--reveal-theme", default="black", help="Reveal theme file name (without .css), looked up under dist/theme.")
    parser.add_argument("--screen", default="1920x1080", help="Target screen size for layout policy (default 1920x1080).")
    parser.add_argument("--detail-profile", choices=["adaptive", "compact", "verbose"], default="adaptive", help="Controls speaker-note depth.")
    parser.add_argument("--visuals", choices=["on", "off"], default="off", help="Enable or disable supplementary inline visuals (non-graph).")
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
    files = [p for p in week_dir.iterdir() if p.is_file() and DUMP_FILE_RE.match(p.name)]
    return sorted(files)


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_tickets_section(text: str) -> list[TicketRecord]:
    marker = "# All Scraped Tickets"
    idx = text.find(marker)
    if idx == -1:
        return []
    body = text[idx + len(marker) :]
    lines = body.splitlines()

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
                if item.activity_date and re.match(r"^\d{4}-\d{2}-\d{2}$", item.activity_date):
                    timeline_events.append(
                        {
                            "timestamp": fallback_ts(item.activity_date),
                            "event": f"activity snapshot (status {item.status})",
                        }
                    )

        seen = set()
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


def make_flow_summary(ticket: UnifiedTicket, max_middle: int = 2) -> str:
    if not ticket.timeline_events:
        return f"No timeline events were captured this week. Current state is {ticket.current_status}."

    start = ticket.timeline_events[0]
    end = ticket.timeline_events[-1]
    middle = ticket.timeline_events[1:-1]

    start_text = f"Started with {start['event']} ({start['timestamp']})."
    mid_text = ""
    if middle:
        mids = "; ".join(f"{m['event']} ({m['timestamp']})" for m in middle[:max_middle])
        more = "" if len(middle) <= max_middle else f" +{len(middle)-max_middle} more transitions"
        mid_text = f" Progressed through {mids}{more}."
    end_text = f" Ended with {end['event']} ({end['timestamp']}) and status {ticket.current_status}."
    return start_text + mid_text + end_text


def _extract_issue_statement(ticket: UnifiedTicket) -> str:
    text_parts = [ticket.title] + ticket.notes + [ev.get("event", "") for ev in ticket.timeline_events]
    for part in text_parts:
        lower = part.lower()
        if any(keyword in lower for keyword in ISSUE_KEYWORDS):
            return normalize_space(part)
    if _is_resolved(ticket.current_status):
        return "No active issue remains; ticket appears resolved."
    return "Issue not explicitly captured in notes; unresolved status indicates pending closure work."


def _impact_statement(ticket: UnifiedTicket) -> str:
    if _is_resolved(ticket.current_status):
        return "Impact is contained for now; monitor for regressions."
    return "Impact is active until closure; this may affect delivery confidence."


def _next_step_statement(ticket: UnifiedTicket) -> str:
    if _is_resolved(ticket.current_status):
        return "Confirm post-merge validation and close follow-up checks."
    return "Assign clear owner, unblock dependencies, and target closure in the current cycle."


def _ticket_story_items(ticket: UnifiedTicket, hidden_count: int) -> list[str]:
    items = [
        f"What happened: {make_flow_summary(ticket, max_middle=2)}",
        f"Issue: {_extract_issue_statement(ticket)}",
        f"Impact: {_impact_statement(ticket)}",
        f"Next step: {_next_step_statement(ticket)}",
    ]
    if hidden_count > 0:
        items.append(f"Additional context: {hidden_count} more event(s) are covered in speaker notes.")
    return items


def make_presenter_script(ticket: UnifiedTicket, detail_profile: str = "adaptive") -> str:
    timeline_len = len(ticket.timeline_events)
    has_status_change = len(set(s.lower() for s in ticket.statuses if s)) > 1
    unresolved = not _is_resolved(ticket.current_status)
    note_density = len(ticket.notes)

    complexity = timeline_len + (2 if has_status_change else 0) + (2 if unresolved else 0) + min(note_density, 3)
    if detail_profile == "compact":
        mode = "compact"
    elif detail_profile == "verbose":
        mode = "verbose"
    else:
        if complexity <= 3:
            mode = "compact"
        elif complexity <= 7:
            mode = "balanced"
        else:
            mode = "verbose"

    issue_line = _extract_issue_statement(ticket)
    impact_line = _impact_statement(ticket)
    next_step = _next_step_statement(ticket)

    if not ticket.timeline_events:
        return "\n".join(
            [
                f"Slide goal: explain {ticket.ticket_id} clearly in under 45 seconds.",
                f"Say: {ticket.ticket_id} - {ticket.title}.",
                "What happened: no timeline evidence captured this week.",
                f"Issue: {issue_line}",
                f"Impact: {impact_line}",
                f"Next step: {next_step}",
                "Transition: move to the next ticket and compare delivery risk.",
            ]
        )

    first = ticket.timeline_events[0]
    last = ticket.timeline_events[-1]

    parts = [
        f"Slide goal: explain {ticket.ticket_id} clearly in under 60 seconds.",
        f"Say: {ticket.ticket_id} - {ticket.title}.",
        f"What happened: started with {first['event']} on {first['timestamp']}.",
        f"Current state: {ticket.current_status}; latest update was {last['event']} on {last['timestamp']}.",
        f"Issue: {issue_line}",
        f"Impact: {impact_line}",
    ]

    if mode in {"balanced", "verbose"} and timeline_len > 2:
        mids = ticket.timeline_events[1:-1]
        max_mid = 2 if mode == "balanced" else 4
        rendered = "; ".join(f"{e['event']} ({e['timestamp']})" for e in mids[:max_mid])
        if rendered:
            parts.append(f"Key transitions: {rendered}.")
        if len(mids) > max_mid:
            parts.append(f"Additional transitions not shown on slide: {len(mids) - max_mid}.")

    if mode == "verbose" and ticket.notes:
        notes_excerpt = " ".join(ticket.notes[:2])
        parts.append(f"Context notes: {notes_excerpt}")

    parts.append(f"Next step: {next_step}")
    parts.append("Transition: hand off to the next ticket with contrast on risk and momentum.")
    return "\n".join(parts)


def _status_counts(tickets: list[UnifiedTicket]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for t in tickets:
        key = t.current_status or "Unknown"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[0].lower()))


def _day_activity_counts(tickets: list[UnifiedTicket]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for t in tickets:
        for event in t.timeline_events:
            ts = event.get("timestamp", "")
            day = ts[:10] if len(ts) >= 10 else "Unknown"
            counts[day] = counts.get(day, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[0]))


def _infer_text_signals(ticket: UnifiedTicket) -> dict[str, Any]:
    text = " ".join([ticket.title] + ticket.notes + [e.get("event", "") for e in ticket.timeline_events]).lower()
    risk_hits = sum(text.count(k) for k in RISK_KEYWORDS)
    momentum_hits = sum(text.count(k) for k in MOMENTUM_KEYWORDS)
    blockers = "blocked" in text or "dependency" in text
    return {
        "riskScore": risk_hits,
        "momentumScore": momentum_hits,
        "hasBlockers": blockers,
        "visualCandidates": (
            ["risk-matrix", "relationship-map"] if (risk_hits > momentum_hits or blockers) else ["flow-nodes", "trend-line"]
        ),
    }


def _select_ticket_layout(ticket: UnifiedTicket, signals: dict[str, Any]) -> str:
    timeline_len = len(ticket.timeline_events)
    status_churn = len(set(s.lower() for s in ticket.statuses if s))
    unresolved = not _is_resolved(ticket.current_status)
    if signals["hasBlockers"] or (unresolved and signals["riskScore"] > 0):
        return "comparison"
    if timeline_len >= 4 or status_churn >= 3:
        return "timeline-focus"
    if len(ticket.notes) >= 3:
        return "dense-notes"
    return "two-column"


def _deck_defaults() -> dict[str, Any]:
    return {
        "version": "1.0",
        "defaultLayout": "two-column",
        "layoutOrder": ["hero", "chart-focus", "timeline-focus", "two-column", "comparison", "dense-notes"],
        "visualOrder": ["kpi-strip", "status-bars", "trend-line", "flow-nodes", "relationship-map", "risk-matrix"],
        "constraints": {
            "maxMetaItems": 4,
            "maxTimelineItems": 5,
            "maxBulletItems": 6,
            "truncatePolicy": "tail",
            "aspect": "16:9",
        },
    }


def _build_render_plan(slide_type: str, ticket: UnifiedTicket | None = None, status_counts: dict[str, int] | None = None, unresolved: int = 0) -> dict[str, Any]:
    if slide_type == "opening":
        return {
            "layout": "hero",
            "regions": {"headline": "title", "narrative": "body", "evidence": "meta"},
            "visuals": [{"type": "kpi-strip"}],
            "emphasis": ["momentum"],
            "constraints": {"reserveWhitespace": "medium"},
        }
    if slide_type == "health":
        return {
            "layout": "two-column",
            "regions": {"headline": "title", "narrative": "body", "evidence": "meta", "callouts": "items"},
            "visuals": [],
            "emphasis": ["risk" if unresolved > 0 else "momentum"],
            "constraints": {"maxVisuals": 0},
        }
    if slide_type == "closing":
        return {
            "layout": "comparison",
            "regions": {"headline": "title", "callouts": "items", "narrative": "body"},
            "visuals": [{"type": "risk-matrix"}],
            "emphasis": ["risk", "blockers"],
            "constraints": {"maxBulletItems": 8},
        }
    if slide_type == "empty":
        return {
            "layout": "hero",
            "regions": {"headline": "title", "narrative": "body"},
            "visuals": [],
            "emphasis": ["none"],
            "constraints": {"reserveWhitespace": "high"},
        }
    if ticket is None:
        return {"layout": "two-column", "regions": {}, "visuals": [], "emphasis": [], "constraints": {}}

    signals = _infer_text_signals(ticket)
    layout = _select_ticket_layout(ticket, signals)
    visuals = [{"type": "flow-nodes"}]
    for candidate in signals["visualCandidates"]:
        if candidate != "flow-nodes":
            visuals.append({"type": candidate})
            break
    emphasis = ["risk" if signals["riskScore"] > signals["momentumScore"] else "momentum"]
    if signals["hasBlockers"]:
        emphasis.append("blockers")

    return {
        "layout": layout,
        "regions": {"headline": "title", "narrative": "body", "timeline": "timeline", "evidence": "meta", "callouts": "items"},
        "visuals": visuals,
        "emphasis": emphasis,
        "constraints": {
            "maxTimelineItems": 5,
            "maxBulletItems": 6,
            "truncatePolicy": "tail",
        },
    }


def _health_snapshot_items(status_counts: dict[str, int], day_counts: dict[str, int], unresolved_count: int) -> list[str]:
    items: list[str] = []
    if status_counts:
        ordered = sorted(status_counts.items(), key=lambda x: (-x[1], x[0].lower()))
        top = ordered[:3]
        items.append("Top end-of-week statuses: " + ", ".join(f"{name} ({count})" for name, count in top))
    if day_counts:
        ordered_days = sorted(day_counts.items(), key=lambda x: (-x[1], x[0]))
        busiest_day, busiest_count = ordered_days[0]
        items.append(f"Most activity day: {busiest_day} ({busiest_count} updates)")
    if unresolved_count > 0:
        items.append(f"Open risk remains on {unresolved_count} ticket(s); focus on closure owners and blockers.")
    else:
        items.append("No end-of-week open risk detected in tracked tickets.")
    return items


def build_generic_payload(week: str, tickets: list[UnifiedTicket], detail_profile: str = "adaptive", visuals: str = "on") -> dict[str, Any]:
    unresolved = [t for t in tickets if not _is_resolved(t.current_status)]
    status_counts = _status_counts(tickets)
    day_counts = _day_activity_counts(tickets)

    slides: list[dict[str, Any]] = [
        {
            "type": "opening",
            "title": f"Weekly Ticket Flow Report - {week}",
            "body": "Executive and engineering weekly status brief derived from merged ticket activity.",
            "meta": [f"Tickets: {len(tickets)}", f"Resolved: {len(tickets) - len(unresolved)}", f"Unresolved: {len(unresolved)}"],
            "timeline": [],
            "presenterNotes": "\n".join(
                [
                    "Slide goal: frame the week in 30 seconds.",
                    "Say: this report summarizes what changed, where risk sits, and what actions we need next.",
                    "What happened: present total tickets, resolved count, and unresolved count.",
                    "Issue: unresolved tickets indicate potential delivery pressure.",
                    "Next step: use the next slide to highlight where attention is required.",
                ]
            ),
            "status": "overview",
            "items": [],
            "visual": "kpi",
            "renderPlan": _build_render_plan("opening"),
        }
    ]

    slides.append(
        {
            "type": "health",
            "title": "Weekly Situation Snapshot",
            "body": "Plain-language summary of what changed, where the pressure is, and what needs attention next.",
            "meta": [f"Generated week: {week}", "No status charts used; read this as context before ticket details."],
            "timeline": [],
            "presenterNotes": "\n".join(
                [
                    "Slide goal: provide context before ticket-level details.",
                    "Say: this snapshot explains where work concentrated and where unresolved ownership remains.",
                    "What happened: call out top statuses and busiest activity day.",
                    "Issue: identify unresolved concentration and blockers if present.",
                    "Next step: move ticket by ticket with owner-focused actions.",
                ]
            ),
            "status": "overview",
            "items": _health_snapshot_items(status_counts, day_counts, len(unresolved)),
            "visual": "none",
            "renderPlan": _build_render_plan("health", status_counts=status_counts, unresolved=len(unresolved)),
        }
    )

    for ticket in tickets:
        timeline_trim = ticket.timeline_events[:4]
        hidden_count = max(0, len(ticket.timeline_events) - len(timeline_trim))
        items = _ticket_story_items(ticket, hidden_count)

        slides.append(
            {
                "type": "content",
                "title": f"{ticket.ticket_id}: {ticket.title}",
                "body": make_flow_summary(ticket, max_middle=2),
                "meta": [f"Role: {ticket.role}", f"Status: {ticket.current_status}"],
                "timeline": timeline_trim,
                "presenterNotes": make_presenter_script(ticket, detail_profile=detail_profile),
                "status": ticket.current_status,
                "items": items,
                "ticketUrl": ticket.url,
                "visual": "ticket-flow" if visuals == "on" else "none",
                "renderPlan": _build_render_plan("content", ticket=ticket),
            }
        )

    slides.append(
        {
            "type": "closing",
            "title": "Risks and Follow-ups",
            "body": "Tickets still unresolved at the end of this weekly window.",
            "meta": [f"Unresolved count: {len(unresolved)}"],
            "timeline": [],
            "presenterNotes": "\n".join(
                [
                    "Slide goal: close with explicit ownership and timing.",
                    "Say: these unresolved tickets are the only active risks leaving this reporting window.",
                    "What happened: summarize unresolved list with current status.",
                    "Issue: highlight blockers, dependencies, or missing owner where relevant.",
                    "Next step: confirm who closes each ticket and by when before the next check-in.",
                ]
            ),
            "status": "risk",
            "items": [f"{t.ticket_id}: {t.title} ({t.current_status})" for t in unresolved] or ["All tracked tickets are resolved."],
            "visual": "risk",
            "renderPlan": _build_render_plan("closing"),
        }
    )

    if not tickets:
        slides.append(
            {
                "type": "empty",
                "title": "No Tickets Found",
                "body": "No compatible ticket dumps were found for this week.",
                "meta": [],
                "timeline": [],
                "presenterNotes": "No weekly ticket data was available.",
                "status": "empty",
                "items": [],
                "visual": "none",
                "renderPlan": _build_render_plan("empty"),
            }
        )

    generated_at = "1970-01-01T00:00:00+00:00"
    if tickets:
        known_last = [t.last_event_ts for t in tickets if t.last_event_ts != "Unknown"]
        if known_last:
            generated_at = sorted(known_last)[-1]

    return {
        "title": f"Weekly Ticket Flow Report - {week}",
        "subtitle": "Generated from weekly ticket dumps",
        "generatedAt": generated_at,
        "context": {
            "week": week,
            "ticketCount": len(tickets),
            "unresolvedCount": len(unresolved),
            "statusCounts": status_counts,
            "dayCounts": day_counts,
        },
        "renderDefaults": _deck_defaults(),
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


def _render_list(items: list[str], item_class: str) -> str:
    if not items:
        return ""
    lines = "".join(f"<li>{html.escape(item)}</li>" for item in items[:6])
    return f'<ul class="{item_class}">{lines}</ul>'


def _render_timeline(events: list[dict[str, str]]) -> str:
    if not events:
        return ""
    lines = []
    for event in events[:5]:
        ts = html.escape(event.get("timestamp", ""))
        label = html.escape(event.get("event", ""))
        lines.append(f"<li><strong>{ts}</strong> {label}</li>")
    return f'<ul class="timeline">{"".join(lines)}</ul>'


def _safe_json_script_payload(value: str) -> str:
    return json.dumps(value).replace("</", "<\\/")


def _render_notes_block(notes: str) -> str:
    if not notes:
        return ""
    lines = [html.escape(line.strip()) for line in notes.splitlines() if line.strip()]
    if not lines:
        return ""
    list_items = "".join(f"<li>{line}</li>" for line in lines)
    return f'<aside class="notes"><ul class="notes-list">{list_items}</ul></aside>'


def _timeline_step_labels(slide: dict[str, Any]) -> list[str]:
    events = slide.get("timeline", [])
    labels: list[str] = []
    if not isinstance(events, list):
        return labels
    for event in events[:4]:
        label = str(event.get("event", "")).strip()
        if not label:
            continue
        labels.append(label)
    return labels


def _render_visual_block(slide: dict[str, Any], payload: dict[str, Any]) -> str:
    visual = slide.get("visual", "none")
    if visual == "kpi":
        context = payload.get("context", {})
        total = int(context.get("ticketCount", 0))
        unresolved = int(context.get("unresolvedCount", 0))
        resolved = total - unresolved
        return (
            '<div class="kpi-strip">'
            f'<div class="kpi"><span class="kpi-label">Total</span><span class="kpi-value">{total}</span></div>'
            f'<div class="kpi"><span class="kpi-label">Resolved</span><span class="kpi-value">{resolved}</span></div>'
            f'<div class="kpi"><span class="kpi-label">Unresolved</span><span class="kpi-value">{unresolved}</span></div>'
            "</div>"
        )
    if visual == "ticket-flow":
        total = max(len(slide.get("timeline", [])), 1)
        circles = []
        for i in range(total):
            x = 24 + (i * 36)
            color = "#f59e0b" if i == total - 1 and slide.get("status", "").lower() not in UNRESOLVED_STATUSES else ("#22c55e" if i == total - 1 else "#60a5fa")
            circles.append(f'<circle cx="{x}" cy="16" r="7" fill="{color}" />')
            if i < total - 1:
                circles.append(f'<line x1="{x+8}" y1="16" x2="{x+28}" y2="16" stroke="#64748b" stroke-width="2" />')
        width = 40 + ((total - 1) * 36)
        flow = f'<svg viewBox="0 0 {width} 32" class="flow-svg" role="img" aria-label="Ticket flow marker">{"".join(circles)}</svg>'
        step_labels = _timeline_step_labels(slide)
        step_cards = ""
        if step_labels:
            step_cards = '<div class="flow-steps">' + "".join(f'<span class="flow-step">{html.escape(label)}</span>' for label in step_labels) + "</div>"
        url = html.escape(str(slide.get("ticketUrl", "Not available")))
        link = "" if url == "Not available" else f'<p class="ticket-link">Reference: <a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a></p>'
        return flow + step_cards + link
    return ""


def _render_slide(slide: dict[str, Any], payload: dict[str, Any]) -> str:
    title = html.escape(str(slide.get("title", "")))
    body = html.escape(str(slide.get("body", "")))
    status = html.escape(str(slide.get("status", "")))
    meta = _render_list([str(x) for x in slide.get("meta", [])], "meta")
    items = _render_list([str(x) for x in slide.get("items", [])], "items")
    timeline = _render_timeline(slide.get("timeline", []))
    notes = str(slide.get("presenterNotes", ""))
    visual_block = _render_visual_block(slide, payload)

    status_badge = f'<p class="status">{status}</p>' if status else ""
    notes_html = _render_notes_block(notes)
    return (
        '<section class="ticket-slide">'
        f'<header class="slide-header"><h2>{title}</h2>{status_badge}</header>'
        f'<div class="slide-body"><p>{body}</p>{visual_block}{meta}{timeline}{items}</div>'
        f"{notes_html}"
        "</section>"
    )


def render_reveal_single_file(payload: dict[str, Any], out_file: Path, assets_root: Path, theme_name: str, screen: str = "1920x1080") -> None:
    reveal_js = read_text(assets_root / "dist" / "reveal.js")
    reveal_css = read_text(assets_root / "dist" / "reveal.css")
    reveal_theme_css = read_text(assets_root / "dist" / "theme" / f"{theme_name}.css")
    notes_js = read_text(assets_root / "plugin" / "notes" / "notes.js")

    title = html.escape(str(payload.get("title", "Weekly Ticket Flow Report")))
    subtitle = html.escape(str(payload.get("subtitle", "")))
    generated = html.escape(str(payload.get("generatedAt", "")))
    screen_txt = html.escape(screen)

    slides = payload.get("slides", [])
    sections = "".join(_render_slide(slide, payload) for slide in slides if isinstance(slide, dict))

    reveal_js_json = _safe_json_script_payload(reveal_js)
    reveal_css_json = _safe_json_script_payload(reveal_css)
    reveal_theme_css_json = _safe_json_script_payload(reveal_theme_css)
    notes_js_json = _safe_json_script_payload(notes_js)

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    :root {{
      --deck-width: 1600px;
      --deck-height: 900px;
      --content-max-w: 1380px;
      --space-1: 8px;
      --space-2: 12px;
      --space-3: 16px;
      --space-4: 24px;
      --space-5: 32px;
      --font-xl: 48px;
      --font-lg: 34px;
      --font-md: 24px;
      --font-sm: 18px;
      --line: 1.35;
    }}
    body {{ margin: 0; background: #020617; }}
    .reveal {{ font-size: var(--font-sm); }}
    .reveal .slides section {{
      box-sizing: border-box;
      width: var(--deck-width);
      height: var(--deck-height);
      margin: 0 auto;
      padding: var(--space-4) var(--space-5);
      text-align: left;
      overflow: hidden;
    }}
    .ticket-slide {{ display: grid; grid-template-rows: auto 1fr; gap: var(--space-3); }}
    .slide-header {{ display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); min-height: 80px; }}
    .slide-header h2 {{ margin: 0; font-size: var(--font-lg); line-height: 1.15; max-width: 80%; }}
    .slide-body {{ max-width: var(--content-max-w); overflow: hidden; }}
    .slide-body > p {{ margin: 0 0 var(--space-2) 0; line-height: var(--line); font-size: var(--font-md); max-height: 120px; overflow: hidden; }}
    .status {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      background: rgba(255,255,255,0.14);
      font-size: 16px;
      padding: 6px 12px;
      margin: 0;
      white-space: nowrap;
    }}
    .kpi-strip {{ display: grid; grid-template-columns: repeat(3, minmax(180px, 1fr)); gap: var(--space-3); margin: var(--space-2) 0 var(--space-3); }}
    .kpi {{ background: rgba(15,23,42,0.45); border: 1px solid rgba(148,163,184,0.3); border-radius: 12px; padding: 14px; }}
    .kpi-label {{ display: block; font-size: 14px; color: #cbd5e1; }}
    .kpi-value {{ display: block; font-size: 34px; font-weight: 700; color: #f8fafc; margin-top: 4px; }}
    .viz-svg {{ width: 100%; max-width: 920px; height: auto; display: block; margin: 10px 0; }}
    .flow-svg {{ width: auto; height: 30px; display: block; margin: 8px 0 10px; }}
    .flow-steps {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 10px; }}
    .flow-step {{ font-size: 14px; padding: 5px 10px; border-radius: 999px; border: 1px solid rgba(148,163,184,0.4); background: rgba(15,23,42,0.5); }}
    .ticket-link {{ margin: 4px 0 12px; font-size: 14px; word-break: break-all; }}
    .ticket-link a {{ color: #38bdf8; text-decoration: none; }}
    .meta, .timeline, .items {{ margin: 8px 0; padding-left: 24px; font-size: 18px; line-height: 1.32; }}
    .timeline li, .items li, .meta li {{ margin: 2px 0; }}
    .meta li:nth-child(n+4), .timeline li:nth-child(n+6), .items li:nth-child(n+7) {{ display: none; }}
    .notes-list {{ margin: 0; padding-left: 18px; line-height: 1.35; }}
    .notes-list li {{ margin: 4px 0; }}
    .deck-meta {{ position: fixed; bottom: 10px; right: 14px; z-index: 30; font-size: 12px; color: rgba(255,255,255,0.7); }}
    .screen-meta {{ position: fixed; bottom: 10px; left: 14px; z-index: 30; font-size: 12px; color: rgba(255,255,255,0.7); }}
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <section>
        <h1 style="font-size:var(--font-xl);margin:0 0 12px 0;">{title}</h1>
        <p style="font-size:var(--font-md);margin:0;max-width:1200px;">{subtitle}</p>
        <aside class="notes">Open with the weekly summary and set context before moving into health visuals and ticket flow.</aside>
      </section>
      {sections}
    </div>
  </div>

  <div class="deck-meta">Generated: {generated}</div>
  <div class="screen-meta">Layout target: {screen_txt}</div>

  <script id="asset-reveal-css" type="application/json">{reveal_css_json}</script>
  <script id="asset-reveal-theme-css" type="application/json">{reveal_theme_css_json}</script>
  <script id="asset-reveal-js" type="application/json">{reveal_js_json}</script>
  <script id="asset-notes-js" type="application/json">{notes_js_json}</script>

  <script>
    (function() {{
      function parseJsonText(id) {{
        var el = document.getElementById(id);
        if (!el) throw new Error('Missing asset payload: ' + id);
        return JSON.parse(el.textContent || '""');
      }}
      function injectStyle(css) {{
        var style = document.createElement('style');
        style.textContent = css;
        document.head.appendChild(style);
      }}
      function injectScript(js) {{
        var script = document.createElement('script');
        script.text = js;
        document.body.appendChild(script);
      }}

      injectStyle(parseJsonText('asset-reveal-css'));
      injectStyle(parseJsonText('asset-reveal-theme-css'));
      injectScript(parseJsonText('asset-reveal-js'));
      injectScript(parseJsonText('asset-notes-js'));

      if (typeof Reveal === 'undefined') {{
        throw new Error('Reveal failed to load from bundled assets.');
      }}

      Reveal.initialize({{
        width: 1600,
        height: 900,
        margin: 0.02,
        minScale: 1,
        maxScale: 1,
        hash: true,
        controls: true,
        progress: true,
        center: false,
        transition: 'slide',
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
    payload = build_generic_payload(week, unified, detail_profile=args.detail_profile, visuals=args.visuals)

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
        render_reveal_single_file(
            payload=payload,
            out_file=week_reveal_path,
            assets_root=Path(args.reveal_assets_root),
            theme_name=args.reveal_theme,
            screen=args.screen,
        )
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
    print(f"Supplementary visuals: {args.visuals}")
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
