# TLDR Skill Design

## Goal

Create a `tldr` skill that turns a supplied or clearly referenced body of content into a faithful, compact explanation written in natural human language. The result must remove verbal padding without removing qualifications that materially affect the meaning.

## Invocation and inputs

Support direct invocations such as:

- `/tldr me this`
- `/tldr me that`
- `/tldr me this: <body of text>`
- `/tldr me this: <link>`

Treat pasted text, accessible links, attached or local documents, and the nearest unambiguous conversational referent as valid sources. When a link is supplied, retrieve and read its relevant contents before summarizing. Ask a concise clarifying question only when `this` or `that` has no clear referent. Report an access limitation plainly when the source cannot be read.

## Summarization behavior

Read the complete available source before drafting. Preserve the source's:

- central point or purpose;
- essential claims and reasoning;
- evidence needed to understand those claims;
- decisions, outcomes, or recommended actions;
- caveats, uncertainty, disagreement, and tradeoffs that change the conclusion;
- practical significance.

Compress repeated examples, throat-clearing, promotional language, jargon, hedging that adds no meaning, and other word soup. Do not introduce claims, certainty, judgment, or implications unsupported by the source.

“Full extent” means semantic completeness, not retention of every detail. A reader should be able to skip the original and still understand what it says, why it says it, why it matters, and what materially qualifies it.

## Output contract

Lead directly with the summary. Do not add a greeting, process narration, `Here is your TLDR`, a closing offer, or other filler.

Use adaptive length:

- Return one short paragraph for straightforward material.
- Add compact bullets only when distinct claims, steps, positions, or caveats would otherwise become hard to follow.
- Use as many words as semantic completeness requires, then stop.

Write clear, concrete, natural prose. Prefer ordinary words and varied sentence structure. Avoid canned AI phrasing, inflated transitions, repetitive conclusions, and excessive headings. Preserve necessary technical terms and briefly explain them only when the source depends on them.

## Skill structure

Create the skill at `skills/knowledge/tldr/` with only:

- `SKILL.md`, containing YAML frontmatter with `name` and `description` plus the operational workflow;
- `agents/openai.yaml`, containing quoted interface strings and a default prompt that explicitly invokes `$tldr`.

Do not add scripts, references, assets, or auxiliary documentation. The workflow requires semantic judgment and has no repeated deterministic operation that benefits from code.

## Validation

Run the Skill Creator validation script and inspect both generated files. Forward-test the skill on at least:

1. a short, padded passage;
2. a dense passage with a conclusion-changing caveat;
3. a link-backed source;
4. an ambiguous `this` or `that` request.

The skill passes when its outputs are concise, faithful, free of conversational filler, adapt their structure to source complexity, preserve material qualifications, and ask for context only when the referent genuinely cannot be resolved.

## Out of scope

- Fixed word or character limits unless a user supplies one.
- Commentary, critique, fact-checking, or rewriting unless explicitly requested alongside the TLDR.
- Mechanical extraction pipelines or domain-specific summary templates.
