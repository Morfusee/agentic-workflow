# Ticket Comment Format

Use this exact structure for ticket implementation notifications.

```md
All requirements for this ticket are already implemented and committed.

**Branch**: [Branch]

### What changed:
- [Bulletpoint 1]
- [Bulletpoint 2]
- [Bulletpoint 3]

### Notes:
[Paragraph of notes if there are any]

### Required action/s:
- [Bulletpoint 1]
- [Bulletpoint 2]
```

## Rules

- Omit the `Notes:` paragraph only when there are no relevant notes and the provider/comment context allows omission. Otherwise write `None.`
- Required actions should be concrete, such as review, QA verification, deployment, or product acceptance.
- Never include developer names, commit hashes, emojis, or verbose implementation logs.
