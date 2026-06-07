# Character & Dungeon Guardrails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement structural guardrail validation for character sheets and dungeons — required fields, connectivity checks, and theme matching — as a v0 validation module in the game server.

**Architecture:** A `validation/` module inside the server with two validators (character, dungeon) and a shared pipeline. v0 implements only structural checks; the AI validation agent is specified but deferred. The pipeline returns PASS/FAIL with structured error messages.

**Tech Stack:** Python 3.11+, pytest

---

## File Structure

```
code/server/
├── validation/
│   ├── __init__.py           # exports validate_character, validate_dungeon
│   ├── character.py          # structural checks for character sheets
│   ├── dungeon.py            # structural checks for dungeon maps
│   └── pipeline.py           # orchestrates checks, returns Pass/FailResult
└── tests/
    ├── test_character_validation.py
    └── test_dungeon_validation.py
docs/specifications/
├── agents-behaviour/
│   └── validator.md           # spec: AI validation agent behavior
└── game-design/
    ├── character-guardrails.md # spec: character structural + AI rules
    ├── dungeon-design.md       # spec: dungeon creation rules
    └── dungeon-guardrails.md   # spec: dungeon structural + AI rules
```

---

### Task 1: Character Guardrails Spec Document

**Files:**
- Create: `docs/specifications/game-design/character-guardrails.md`

- [ ] **Step 1: Write the spec document**

```markdown
# Character Guardrails

## Structural Requirements

Every character sheet submitted to the server MUST include the following fields. Missing fields result in hard rejection with a message pointing to the missing field.

### Resources (min 1)

Each resource requires:

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | mana, stamina, cooldown, uses_per_rest, or custom |
| `max` | integer | Maximum value of this resource |
| `current` | integer | Current value (initialized to `max` on creation) |
| `regen_rate` | integer | Amount regenerated per interval |
| `regen_interval` | string | When regen occurs: "turn", "short_rest", "long_rest" |

### Failure Conditions (min 1)

Each failure condition requires:

| Field | Type | Description |
|-------|------|-------------|
| `trigger` | string | What causes this condition (e.g., "hp_depleted", "mana_depleted", "burnout") |
| `effect` | string | What happens when triggered (e.g., "unconscious", "vulnerable", "can_be_harmed") |
| `recovery` | string | How to recover from this condition (e.g., "short_rest", "long_rest", "regain_mana") |

### Tradeoffs (min 1)

Each tradeoff requires:

| Field | Type | Description |
|-------|------|-------------|
| `strength` | string | What the character gains |
| `weakness` | string | What the character gives up or suffers |

## AI Validation Principles

After structural validation passes, the validator agent evaluates:

1. **Meaningfulness** — Is each resource genuinely constrained? A resource with `max: 999999` is not meaningful.
2. **Believability** — Is the failure condition reachable in normal play? "If the universe ends" is not believable.
3. **Proportionality** — Does the tradeoff actually balance the strength? "Untouchable BUT lose 1 HP per hour" is not proportional.

## Validation Outcomes

- PASS: Character enters game state
- WARN: Borderline case, flagged for leader player review
- FAIL: Hard reject with reasoning and fix suggestion
```

- [ ] **Step 2: Commit**

```bash
git add docs/specifications/game-design/character-guardrails.md
git commit -m "docs(guardrails): add character guardrails specification"
```

---

### Task 2: Dungeon Guardrails Spec Document

**Files:**
- Create: `docs/specifications/game-design/dungeon-guardrails.md`

- [ ] **Step 1: Write the spec document**

```markdown
# Dungeon Guardrails

## Structural Requirements

Every dungeon definition submitted to the server MUST include the following fields. Missing fields result in hard rejection with a message pointing to the missing field.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `entrance` | string | How players enter (location reference or narrative trigger) |
| `completion_condition` | string | What ends the dungeon (e.g., "boss_defeated", "artifact_retrieved", "escape") |
| `rooms` | array, min 2 | Room definitions (see below) |
| `theme_tag` | string | Must match the campaign seed's declared tone (e.g., "medieval_fantasy") |

### Room Definition

Each room requires:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique room identifier |
| `name` | string | Room name |
| `description` | string | Narrative description |
| `connections` | array, min 1 | IDs of connected rooms. At least one room must be marked as `entrance: true`. At least one room must be marked as `completion: true`. |

The connection `true` fields replace the top-level `entrance`/`completion_condition` from the flat model — a dungeon is valid if a path exists from the entrance-tagged room to the completion-tagged room. Rooms with no connections (orphaned) are rejected.

## AI Validation Principles

1. **Solvability** — Can the party complete the dungeon at their current level? No level 99 wizard gates.
2. **Spatial coherence** — Do rooms make sense as a connected space? No "door to the surface of the sun."
3. **Thematic integrity** — Does it fit the campaign's setting? No sci-fi in medieval fantasy.

## Validation Outcomes

- PASS: Dungeon enters game state
- WARN: Borderline case, flagged for leader player review
- FAIL: Hard reject with reasoning and fix suggestion
```

- [ ] **Step 2: Commit**

```bash
git add docs/specifications/game-design/dungeon-guardrails.md
git commit -m "docs(guardrails): add dungeon guardrails specification"
```

---

### Task 3: Dungeon Design Spec Document

**Files:**
- Create: `docs/specifications/game-design/dungeon-design.md`

- [ ] **Step 1: Write the spec document**

```markdown
# Dungeon Design

## Overview

Dungeons are defined as a graph of connected rooms with an entrance, a completion condition, and obstacles. They exist within the campaign's established theme and world rules.

## Dungeon Schema

```yaml
dungeon:
  name: "Cragmaw Hideout"
  theme_tag: "medieval_fantasy"
  rooms:
    - id: "entrance"
      name: "Cave Mouth"
      description: "A narrow opening in the hillside. The air is cool and damp."
      entrance: true
      connections: ["guard_post"]
    - id: "guard_post"
      name: "Goblin Guard Post"
      description: "Crude barricades block the passage. Two goblins argue over a game of dice."
      connections: ["entrance", "flooded_tunnel"]
    - id: "flooded_tunnel"
      name: "Flooded Tunnel"
      description: "Knee-deep water. Something glints beneath the surface."
      connections: ["guard_post", "boss_chamber"]
    - id: "boss_chamber"
      name: "Chieftain's Chamber"
      description: "A larger cavern. The goblin chief sits on a throne of stolen goods."
      completion: true
      connections: ["flooded_tunnel"]
```

## Design Rules

1. At least 2 rooms
2. Exactly one room tagged `entrance: true`
3. Exactly one room tagged `completion: true` (or more for multi-exit dungeons)
4. All rooms must be connected to the graph — no orphaned rooms
5. Theme must match the campaign seed's declared theme tag

## Validation

Dungeons are validated through the guardrails pipeline. See `dungeon-guardrails.md`.
```

- [ ] **Step 2: Commit**

```bash
git add docs/specifications/game-design/dungeon-design.md
git commit -m "docs(dungeons): add dungeon design specification"
```

---

### Task 4: Validator Agent Spec Document

**Files:**
- Create: `docs/specifications/agents-behaviour/validator.md`

- [ ] **Step 1: Write the spec document**

```markdown
# Validator Agent

## Role

The validator agent enforces character and dungeon guardrails. It is called by the server during creation pipelines (character creation in Step 1 of the gameplay loop; dungeon design during Step 3).

## v0 Scope

In v0, the validator agent is a specification only — the structural checks run in the server. The AI validation layer (meaningfulness, believability, proportionality, solvability, coherence, thematic integrity) is deferred to post-v0.

## When Invoked

- **Character creation:** After a player submits a character sheet, before it enters `game/state.json`
- **Dungeon design:** When the DM generates or loads a dungeon, before it becomes the active dungeon

## Behavior

1. Receive a character sheet or dungeon definition
2. If v0: delegate to server-side structural validation (agents do not run code)
3. If post-v0: run AI evaluation against the principles defined in `character-guardrails.md` and `dungeon-guardrails.md`
4. Return one of: PASS, WARN (flagged for human review), FAIL (rejected with reasoning)

## AI Validation Prompt (Post-v0)

```
You are a validator for character and dungeon submissions in a D&D game.

Evaluate the submission against these principles:

CHARACTER:
- Meaningfulness: Are resources genuinely constrained?
- Believability: Is the failure condition reachable?
- Proportionality: Does each tradeoff balance its strength?

DUNGEON:
- Solvability: Can the party complete it at their level?
- Spatial coherence: Do rooms make sense as a connected space?
- Thematic integrity: Does it fit the campaign's theme?

Return: PASS, WARN (borderline, flag for human), or FAIL (reject with reasoning).
```
```

- [ ] **Step 2: Commit**

```bash
git add docs/specifications/agents-behaviour/validator.md
git commit -m "docs(validator): add validator agent specification"
```

---

### Task 5: Validation Data Models

**Files:**
- Create: `code/server/validation/__init__.py`
- Create: `code/server/validation/pipeline.py`

- [ ] **Step 1: Write the data models and result type**

Create `code/server/validation/__init__.py`:

```python
from .pipeline import PassResult, FailResult, validate_character, validate_dungeon

__all__ = ["PassResult", "FailResult", "validate_character", "validate_dungeon"]
```

Create `code/server/validation/pipeline.py`:

```python
from dataclasses import dataclass, field
from typing import Literal
from .character import check_character_structure
from .dungeon import check_dungeon_structure


@dataclass
class FailResult:
    status: Literal["FAIL"] = "FAIL"
    errors: list[str] = field(default_factory=list)


@dataclass
class PassResult:
    status: Literal["PASS"] = "PASS"


def validate_character(character: dict) -> PassResult | FailResult:
    errors = check_character_structure(character)
    if errors:
        return FailResult(errors=errors)
    return PassResult()


def validate_dungeon(dungeon: dict) -> PassResult | FailResult:
    errors = check_dungeon_structure(dungeon)
    if errors:
        return FailResult(errors=errors)
    return PassResult()
```

- [ ] **Step 2: Run Python to verify syntax**

```bash
python -m py_compile code/server/validation/__init__.py && python -m py_compile code/server/validation/pipeline.py
```

- [ ] **Step 3: Commit**

```bash
git add code/server/validation/__init__.py code/server/validation/pipeline.py
git commit -m "feat(validation): add pipeline and result types"
```

---

### Task 6: Character Structural Validation

**Files:**
- Create: `code/server/validation/character.py`
- Create: `code/server/tests/test_character_validation.py`

- [ ] **Step 1: Write the failing test**

Create `code/server/tests/test_character_validation.py`:

```python
import pytest
from code.server.validation.character import check_character_structure


class TestCharacterStructure:
    def test_empty_character_fails(self):
        errors = check_character_structure({})
        assert len(errors) > 0
        assert any("resources" in e.lower() for e in errors)

    def test_missing_resources_fails(self):
        char = {
            "failure_conditions": [{"trigger": "hp_depleted", "effect": "unconscious", "recovery": "long_rest"}],
            "tradeoffs": [{"strength": "high damage", "weakness": "low defense"}]
        }
        errors = check_character_structure(char)
        assert any("resources" in e.lower() for e in errors)

    def test_missing_failure_conditions_fails(self):
        char = {
            "resources": [{"type": "mana", "max": 100, "current": 100, "regen_rate": 5, "regen_interval": "turn"}],
            "tradeoffs": [{"strength": "high damage", "weakness": "low defense"}]
        }
        errors = check_character_structure(char)
        assert any("failure" in e.lower() for e in errors)

    def test_missing_tradeoffs_fails(self):
        char = {
            "resources": [{"type": "mana", "max": 100, "current": 100, "regen_rate": 5, "regen_interval": "turn"}],
            "failure_conditions": [{"trigger": "hp_depleted", "effect": "unconscious", "recovery": "long_rest"}]
        }
        errors = check_character_structure(char)
        assert any("tradeoff" in e.lower() for e in errors)

    def test_empty_resources_array_fails(self):
        char = {
            "resources": [],
            "failure_conditions": [{"trigger": "hp_depleted", "effect": "unconscious", "recovery": "long_rest"}],
            "tradeoffs": [{"strength": "high damage", "weakness": "low defense"}]
        }
        errors = check_character_structure(char)
        assert any("at least one resource" in e.lower() for e in errors)

    def test_empty_failure_conditions_array_fails(self):
        char = {
            "resources": [{"type": "mana", "max": 100, "current": 100, "regen_rate": 5, "regen_interval": "turn"}],
            "failure_conditions": [],
            "tradeoffs": [{"strength": "high damage", "weakness": "low defense"}]
        }
        errors = check_character_structure(char)
        assert any("at least one failure" in e.lower() for e in errors)

    def test_empty_tradeoffs_array_fails(self):
        char = {
            "resources": [{"type": "mana", "max": 100, "current": 100, "regen_rate": 5, "regen_interval": "turn"}],
            "failure_conditions": [{"trigger": "hp_depleted", "effect": "unconscious", "recovery": "long_rest"}],
            "tradeoffs": []
        }
        errors = check_character_structure(char)
        assert any("at least one tradeoff" in e.lower() for e in errors)

    def test_resource_missing_required_fields(self):
        char = {
            "resources": [{"type": "mana"}],
            "failure_conditions": [{"trigger": "hp_depleted", "effect": "unconscious", "recovery": "long_rest"}],
            "tradeoffs": [{"strength": "high damage", "weakness": "low defense"}]
        }
        errors = check_character_structure(char)
        assert any("resource" in e.lower() and "missing" in e.lower() for e in errors)

    def test_failure_condition_missing_required_fields(self):
        char = {
            "resources": [{"type": "mana", "max": 100, "current": 100, "regen_rate": 5, "regen_interval": "turn"}],
            "failure_conditions": [{"trigger": "hp_depleted"}],
            "tradeoffs": [{"strength": "high damage", "weakness": "low defense"}]
        }
        errors = check_character_structure(char)
        assert any("failure" in e.lower() and "missing" in e.lower() for e in errors)

    def test_tradeoff_missing_required_fields(self):
        char = {
            "resources": [{"type": "mana", "max": 100, "current": 100, "regen_rate": 5, "regen_interval": "turn"}],
            "failure_conditions": [{"trigger": "hp_depleted", "effect": "unconscious", "recovery": "long_rest"}],
            "tradeoffs": [{"strength": "high damage"}]
        }
        errors = check_character_structure(char)
        assert any("tradeoff" in e.lower() and "missing" in e.lower() for e in errors)

    def test_valid_character_passes(self):
        char = {
            "resources": [{"type": "mana", "max": 100, "current": 100, "regen_rate": 5, "regen_interval": "turn"}],
            "failure_conditions": [{"trigger": "hp_depleted", "effect": "unconscious", "recovery": "long_rest"}],
            "tradeoffs": [{"strength": "high damage", "weakness": "low defense"}]
        }
        errors = check_character_structure(char)
        assert errors == []

    def test_valid_character_with_custom_resource_type(self):
        char = {
            "resources": [{"type": "stamina", "max": 50, "current": 50, "regen_rate": 10, "regen_interval": "short_rest"}],
            "failure_conditions": [{"trigger": "stamina_depleted", "effect": "burnout_vulnerable", "recovery": "short_rest"}],
            "tradeoffs": [{"strength": "invulnerable while stamina > 0", "weakness": "cannot attack while stamina recharging"}]
        }
        errors = check_character_structure(char)
        assert errors == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest code/server/tests/test_character_validation.py -v
```
Expected: FAIL with ModuleNotFoundError for `character`

- [ ] **Step 3: Write minimal implementation**

Create `code/server/validation/character.py`:

```python
RESOURCE_REQUIRED_FIELDS = ["type", "max", "current", "regen_rate", "regen_interval"]
FAILURE_CONDITION_REQUIRED_FIELDS = ["trigger", "effect", "recovery"]
TRADEOFF_REQUIRED_FIELDS = ["strength", "weakness"]


def check_character_structure(character: dict) -> list[str]:
    errors = []

    resources = character.get("resources")
    if not isinstance(resources, list) or len(resources) == 0:
        errors.append("Character must have at least one resource")
    else:
        for i, resource in enumerate(resources):
            for field in RESOURCE_REQUIRED_FIELDS:
                if field not in resource:
                    errors.append(f"Resource {i} is missing required field '{field}'")

    failure_conditions = character.get("failure_conditions")
    if not isinstance(failure_conditions, list) or len(failure_conditions) == 0:
        errors.append("Character must have at least one failure condition")
    else:
        for i, fc in enumerate(failure_conditions):
            for field in FAILURE_CONDITION_REQUIRED_FIELDS:
                if field not in fc:
                    errors.append(f"Failure condition {i} is missing required field '{field}'")

    tradeoffs = character.get("tradeoffs")
    if not isinstance(tradeoffs, list) or len(tradeoffs) == 0:
        errors.append("Character must have at least one tradeoff")
    else:
        for i, tradeoff in enumerate(tradeoffs):
            for field in TRADEOFF_REQUIRED_FIELDS:
                if field not in tradeoff:
                    errors.append(f"Tradeoff {i} is missing required field '{field}'")

    return errors
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest code/server/tests/test_character_validation.py -v
```
Expected: PASS (11 tests)

- [ ] **Step 5: Commit**

```bash
git add code/server/validation/character.py code/server/tests/test_character_validation.py
git commit -m "feat(validation): add character structural validation"
```

---

### Task 7: Dungeon Structural Validation

**Files:**
- Create: `code/server/validation/dungeon.py`
- Create: `code/server/tests/test_dungeon_validation.py`

- [ ] **Step 1: Write the failing test**

Create `code/server/tests/test_dungeon_validation.py`:

```python
import pytest
from code.server.validation.dungeon import check_dungeon_structure


def _valid_room(id, name="Room", connections=None, entrance=False, completion=False):
    return {
        "id": id,
        "name": name,
        "description": "A room.",
        "entrance": entrance,
        "completion": completion,
        "connections": connections or []
    }


class TestDungeonStructure:
    def test_empty_dungeon_fails(self):
        errors = check_dungeon_structure({})
        assert any("rooms" in e.lower() for e in errors)

    def test_single_room_fails(self):
        dungeon = {
            "theme_tag": "medieval_fantasy",
            "rooms": [_valid_room("r1")]
        }
        errors = check_dungeon_structure(dungeon)
        assert any("at least 2 rooms" in e.lower() for e in errors)

    def test_missing_theme_tag_fails(self):
        dungeon = {
            "rooms": [_valid_room("entrance", entrance=True), _valid_room("exit", completion=True)]
        }
        errors = check_dungeon_structure(dungeon)
        assert any("theme_tag" in e.lower() for e in errors)

    def test_no_entrance_fails(self):
        dungeon = {
            "theme_tag": "medieval_fantasy",
            "rooms": [
                _valid_room("r1", connections=["r2"]),
                _valid_room("r2", connections=["r1"], completion=True)
            ]
        }
        errors = check_dungeon_structure(dungeon)
        assert any("entrance" in e.lower() for e in errors)

    def test_no_completion_fails(self):
        dungeon = {
            "theme_tag": "medieval_fantasy",
            "rooms": [
                _valid_room("r1", connections=["r2"], entrance=True),
                _valid_room("r2", connections=["r1"])
            ]
        }
        errors = check_dungeon_structure(dungeon)
        assert any("completion" in e.lower() for e in errors)

    def test_orphaned_room_fails(self):
        dungeon = {
            "theme_tag": "medieval_fantasy",
            "rooms": [
                _valid_room("entrance", connections=["hall"], entrance=True),
                _valid_room("hall", connections=["entrance"]),
                _valid_room("orphan", connections=[]),
                _valid_room("boss", connections=["hall"], completion=True)
            ]
        }
        errors = check_dungeon_structure(dungeon)
        assert any("not connected" in e.lower() for e in errors)

    def test_no_path_from_entrance_to_completion_fails(self):
        dungeon = {
            "theme_tag": "medieval_fantasy",
            "rooms": [
                _valid_room("entrance", connections=["left"], entrance=True),
                _valid_room("left", connections=["entrance"]),
                _valid_room("right", connections=["boss"], completion=True),
                _valid_room("boss", connections=["right"])
            ]
        }
        errors = check_dungeon_structure(dungeon)
        assert any("no path" in e.lower() for e in errors)

    def test_room_missing_required_fields_fails(self):
        dungeon = {
            "theme_tag": "medieval_fantasy",
            "rooms": [
                {"id": "r1"},
                _valid_room("r2", completion=True)
            ]
        }
        errors = check_dungeon_structure(dungeon)
        assert any("missing required field" in e.lower() for e in errors)

    def test_valid_linear_dungeon_passes(self):
        dungeon = {
            "theme_tag": "medieval_fantasy",
            "rooms": [
                _valid_room("entrance", connections=["hall"], entrance=True),
                _valid_room("hall", connections=["entrance", "boss"]),
                _valid_room("boss", connections=["hall"], completion=True)
            ]
        }
        errors = check_dungeon_structure(dungeon)
        assert errors == []

    def test_valid_branching_dungeon_passes(self):
        dungeon = {
            "theme_tag": "dark_fantasy",
            "rooms": [
                _valid_room("start", connections=["left", "right", "center"], entrance=True),
                _valid_room("left", connections=["start"]),
                _valid_room("right", connections=["start"]),
                _valid_room("center", connections=["start", "boss"]),
                _valid_room("boss", connections=["center"], completion=True)
            ]
        }
        errors = check_dungeon_structure(dungeon)
        assert errors == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest code/server/tests/test_dungeon_validation.py -v
```
Expected: FAIL with ModuleNotFoundError for `dungeon`

- [ ] **Step 3: Write minimal implementation**

Create `code/server/validation/dungeon.py`:

```python
ROOM_REQUIRED_FIELDS = ["id", "name", "description", "entrance", "completion", "connections"]


def check_dungeon_structure(dungeon: dict) -> list[str]:
    errors = []

    rooms = dungeon.get("rooms")
    if not isinstance(rooms, list) or len(rooms) < 2:
        errors.append("Dungeon must have at least 2 rooms")
        return errors

    theme_tag = dungeon.get("theme_tag")
    if not theme_tag or not isinstance(theme_tag, str):
        errors.append("Dungeon must have a 'theme_tag' string")

    for i, room in enumerate(rooms):
        for field in ROOM_REQUIRED_FIELDS:
            if field not in room:
                errors.append(f"Room {i} ('{room.get('id', 'unknown')}') is missing required field '{field}'")

    if errors:
        return errors

    entrances = [r for r in rooms if r.get("entrance") is True]
    completions = [r for r in rooms if r.get("completion") is True]

    if len(entrances) == 0:
        errors.append("Dungeon must have exactly one entrance room (entrance: true)")
    elif len(entrances) > 1:
        errors.append(f"Dungeon has {len(entrances)} entrance rooms, expected exactly 1")

    if len(completions) == 0:
        errors.append("Dungeon must have at least one completion room (completion: true)")

    if errors:
        return errors

    orphaned = [r for r in rooms if len(r.get("connections", [])) == 0]
    if orphaned:
        names = [r["id"] for r in orphaned]
        errors.append(f"Rooms are not connected to any other room: {', '.join(names)}")

    entrance_id = entrances[0]["id"]
    completion_ids = {r["id"] for r in completions}

    reachable = _bfs(entrance_id, rooms)
    unreachable_completions = completion_ids - reachable
    if unreachable_completions:
        names = ", ".join(unreachable_completions)
        errors.append(f"No path from entrance '{entrance_id}' to completion room(s): {names}")

    return errors


def _bfs(start_id: str, rooms: list[dict]) -> set[str]:
    adjacency = {r["id"]: r.get("connections", []) for r in rooms}
    visited = set()
    queue = [start_id]
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        for neighbor in adjacency.get(current, []):
            if neighbor not in visited:
                queue.append(neighbor)
    return visited
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest code/server/tests/test_dungeon_validation.py -v
```
Expected: PASS (10 tests)

- [ ] **Step 5: Commit**

```bash
git add code/server/validation/dungeon.py code/server/tests/test_dungeon_validation.py
git commit -m "feat(validation): add dungeon structural validation with BFS path check"
```

---

### Task 8: Integration Test - Full Pipeline

**Files:**
- Create: `code/server/tests/test_validation_pipeline.py`

- [ ] **Step 1: Write the failing test**

Create `code/server/tests/test_validation_pipeline.py`:

```python
from code.server.validation import validate_character, validate_dungeon, PassResult, FailResult


class TestValidationPipeline:
    def test_validate_character_returns_pass_for_valid(self):
        char = {
            "resources": [{"type": "mana", "max": 100, "current": 100, "regen_rate": 5, "regen_interval": "turn"}],
            "failure_conditions": [{"trigger": "hp_depleted", "effect": "unconscious", "recovery": "long_rest"}],
            "tradeoffs": [{"strength": "high damage", "weakness": "low defense"}]
        }
        result = validate_character(char)
        assert isinstance(result, PassResult)
        assert result.status == "PASS"

    def test_validate_character_returns_fail_for_invalid(self):
        char = {"resources": []}
        result = validate_character(char)
        assert isinstance(result, FailResult)
        assert result.status == "FAIL"
        assert len(result.errors) > 0

    def test_validate_dungeon_returns_pass_for_valid(self):
        dungeon = {
            "theme_tag": "medieval_fantasy",
            "rooms": [
                {"id": "start", "name": "Start", "description": "Beginning.", "entrance": True, "completion": False, "connections": ["end"]},
                {"id": "end", "name": "End", "description": "The end.", "entrance": False, "completion": True, "connections": ["start"]}
            ]
        }
        result = validate_dungeon(dungeon)
        assert isinstance(result, PassResult)
        assert result.status == "PASS"

    def test_validate_dungeon_returns_fail_for_invalid(self):
        dungeon = {"rooms": []}
        result = validate_dungeon(dungeon)
        assert isinstance(result, FailResult)
        assert result.status == "FAIL"
        assert len(result.errors) > 0
```

- [ ] **Step 2: Run test to verify it passes**

```bash
python -m pytest code/server/tests/test_validation_pipeline.py -v
```
Expected: PASS (4 tests)

- [ ] **Step 3: Commit**

```bash
git add code/server/tests/test_validation_pipeline.py
git commit -m "test(validation): add pipeline integration tests"
```

---

### Task 9: Run Full Test Suite and Finalize

- [ ] **Step 1: Run all validation tests**

```bash
python -m pytest code/server/tests/ -v
```
Expected: PASS (25 tests across all 3 test files)

- [ ] **Step 2: Commit any final fixes**

```bash
git add -A && git diff --cached --stat
```
If clean: no action. If test fixes were needed:
```bash
git commit -m "test(validation): finalize test suite"
```
