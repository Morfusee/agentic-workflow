---
name: react-quality-review
description: Comprehensive React/TypeScript code quality review for best practices, performance, accessibility, testing, and adherence to CODE_STANDARDS.md
---

Perform a comprehensive React/TypeScript code quality review against CODE_STANDARDS.md.

Workflow
1. Determine review scope and focus areas from the user.
2. Scan target files based on scope and requested focus areas.
3. Analyze each file against CODE_STANDARDS.md and the checklist.
4. Run automated checks where possible (tsconfig strict mode, test files/coverage, common anti-patterns).
5. Produce a detailed report with file paths, line numbers, code snippets, and fixes.

Use the full checklist and output format in `skills/react-quality-review/references/react-quality-review-checklist.md`.
