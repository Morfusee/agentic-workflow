# TLDR Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create an invocable `tldr` skill that compresses text, links, files, or clearly referenced content into a faithful, natural-language summary with adaptive length and no filler.

**Architecture:** Keep the skill declarative and self-contained. Put source resolution, semantic compression, and output rules in `SKILL.md`; put only user-facing invocation metadata in `agents/openai.yaml`. Use Skill Creator validation for structure and isolated OpenCode runs for behavioral checks.

**Tech Stack:** Markdown, YAML, Skill Creator Python utilities, OpenCode CLI with `opencode-go/deepseek-v4-flash`

---

## File structure

- Create `skills/knowledge/tldr/SKILL.md`: define invocation triggers, source acquisition, meaning preservation, compression, and output behavior.
- Create `skills/knowledge/tldr/agents/openai.yaml`: define the display name, short description, and default `$tldr` prompt.

Do not create scripts, references, assets, fixtures, or auxiliary documentation inside the skill.

### Task 1: Scaffold the skill

**Files:**
- Create: `skills/knowledge/tldr/SKILL.md`
- Create: `skills/knowledge/tldr/agents/openai.yaml`

- [ ] **Step 1: Confirm the target is new**

Run:

```powershell
Test-Path -LiteralPath 'skills/knowledge/tldr'
```

Expected: `False`. If it is `True`, inspect the directory and preserve its contents instead of overwriting it.

- [ ] **Step 2: Initialize the skill with the approved metadata**

Run:

```powershell
python "$HOME/.codex/skills/.system/skill-creator/scripts/init_skill.py" tldr --path skills/knowledge --interface 'display_name=TLDR' --interface 'short_description=Turn dense content into a faithful, plain TLDR' --interface 'default_prompt=Use $tldr to give me a faithful, no-fluff summary of this content.'
```

Expected: the command reports successful creation of `skills/knowledge/tldr/`, `SKILL.md`, and `agents/openai.yaml`.

- [ ] **Step 3: Confirm only the approved skill files were scaffolded**

Run:

```powershell
Get-ChildItem -LiteralPath 'skills/knowledge/tldr' -Recurse -Force | Select-Object -ExpandProperty FullName
```

Expected: one `SKILL.md`, one `agents` directory, and one `agents/openai.yaml`; no `scripts`, `references`, `assets`, or example files.

### Task 2: Implement the TLDR contract

**Files:**
- Modify: `skills/knowledge/tldr/SKILL.md`
- Verify: `skills/knowledge/tldr/agents/openai.yaml`

- [ ] **Step 1: Replace the generated `SKILL.md` with the complete workflow**

Write exactly:

```markdown
---
name: tldr
description: Condense pasted text, links, files, or referenced content into a faithful, plain-language TLDR. Use when the user invokes /tldr, asks to “tldr me this” or “tldr me that,” or wants word soup and fluff removed while preserving essential claims, reasoning, evidence, caveats, decisions, and implications.
---

# TLDR

Produce semantic compression: preserve the source's meaning while removing words the reader does not need.

## Workflow

1. Resolve the source from explicit text, a link, an attached or local file, or the nearest unambiguous conversational referent. Ask one concise question only when `this` or `that` has no clear referent.
2. Read the complete available source before drafting. Retrieve linked content and use the appropriate reader for files. If the source cannot be accessed, state the limitation plainly and stop.
3. Identify the central point, essential claims and reasoning, necessary evidence, decisions or actions, conclusion-changing caveats, and practical significance. Preserve uncertainty and disagreement. Distinguish what the source claims from established fact; do not fact-check unless asked.
4. Remove repetition, throat-clearing, promotional language, redundant examples, empty hedging, jargon that can be stated plainly, and other word soup. Never add unsupported claims, certainty, judgment, or implications.
5. Return the TLDR directly. Use one short paragraph for straightforward material. Add compact bullets only when distinct claims, steps, positions, or caveats would otherwise be hard to follow. Use as many words as semantic completeness requires, then stop.

## Output rules

- Let the reader skip the original while still understanding what it says, why it says it, why it matters, and what materially qualifies it.
- Write clear, concrete, natural prose with varied sentence structure and ordinary words.
- Preserve necessary technical terms; explain them briefly only when understanding depends on them.
- Omit greetings, process narration, `Here is your TLDR`, closing offers, repetitive conclusions, canned AI transitions, and excessive headings.
- Follow a user-supplied length or format constraint when it does not require misrepresenting the source. If it does, state the conflict briefly.
```

- [ ] **Step 2: Verify the generated UI metadata**

Run:

```powershell
Get-Content -Raw -LiteralPath 'skills/knowledge/tldr/agents/openai.yaml'
```

Expected:

```yaml
interface:
  display_name: "TLDR"
  short_description: "Turn dense content into a faithful, plain TLDR"
  default_prompt: "Use $tldr to give me a faithful, no-fluff summary of this content."
```

If generation differs, update the file to match this content exactly.

- [ ] **Step 3: Check the change for scope and formatting**

Run:

```powershell
git diff --check -- skills/knowledge/tldr
git status --short -- skills/knowledge/tldr
```

Expected: no whitespace errors and only the new `skills/knowledge/tldr/` directory appears.

### Task 3: Validate structure and behavior

**Files:**
- Verify: `skills/knowledge/tldr/SKILL.md`
- Verify: `skills/knowledge/tldr/agents/openai.yaml`

- [ ] **Step 1: Run Skill Creator structural validation**

Run:

```powershell
python "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" 'skills/knowledge/tldr'
```

Expected: `Skill is valid!`

- [ ] **Step 2: Forward-test a short padded passage**

Run:

```powershell
opencode run --model opencode-go/deepseek-v4-flash --dir . 'Use the tldr skill at skills/knowledge/tldr/SKILL.md. Do not edit files. Answer: /tldr me this: At this point in time, it is important to note that the committee has made the decision to delay the launch from May to July because the payment system failed security testing. The team remains very committed to ensuring a seamless and robust experience.'
```

Expected: a direct sentence saying the launch moved from May to July because the payment system failed security testing; no preamble or promotional filler.

- [ ] **Step 3: Forward-test a conclusion-changing caveat**

Run:

```powershell
opencode run --model opencode-go/deepseek-v4-flash --dir . 'Use the tldr skill at skills/knowledge/tldr/SKILL.md. Do not edit files. Answer: /tldr me this: A four-week trial reduced average support response time by 40 percent, from ten hours to six. The company plans to expand the tool next quarter. However, only 12 experienced agents joined the trial, they handled simpler tickets than the rest of the team, and customer satisfaction was not measured, so the trial does not yet show that the tool will improve support overall.'
```

Expected: preserve both the 40 percent response-time improvement and the limits on sample size, ticket difficulty, and missing satisfaction data; do not present the trial as conclusive.

- [ ] **Step 4: Forward-test a link-backed source**

Run:

```powershell
opencode run --model opencode-go/deepseek-v4-flash --dir . 'Use the tldr skill at skills/knowledge/tldr/SKILL.md. Do not edit files. Answer: /tldr me this: https://www.rfc-editor.org/rfc/rfc2119'
```

Expected: retrieve the RFC and directly explain that it standardizes requirement keywords such as `MUST`, `SHOULD`, and `MAY`, including their different obligation levels. If network access is unavailable, state that limitation without inventing a summary from the URL alone.

- [ ] **Step 5: Forward-test an unresolved referent**

Run:

```powershell
opencode run --model opencode-go/deepseek-v4-flash --dir . 'Use the tldr skill at skills/knowledge/tldr/SKILL.md. Do not edit files. There is no prior conversational content. Answer: /tldr me this'
```

Expected: one concise request for the text, link, file, or content to summarize; no fabricated referent.

- [ ] **Step 6: Inspect the final diff and preserve unrelated work**

Run:

```powershell
git status --short
git diff --no-ext-diff -- skills/knowledge/tldr
```

Expected: the TLDR skill contains only the two approved files. `memory/docs/superpowers/plans/2026-07-13-portless-app-url-migration.md` remains untouched.

- [ ] **Step 7: Commit the skill as one logical change**

Run:

```powershell
git add -- skills/knowledge/tldr/SKILL.md skills/knowledge/tldr/agents/openai.yaml
git diff --cached --check
git commit -m "feat(tldr): add concise summarization skill"
```

Expected: one Conventional Commit containing only the two TLDR skill files.
