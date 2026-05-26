---
title: Weekly Brief Example
---

# Weekly Brief Example

Use this as the target handoff shape from `$weekly-ticket-slideshow-generator` to `$revealjs-presenter`.

The weekly skill should stop at this information layer.
The slideshow skill should use this information layer to compose slides, notes, layout, and HTML.

## Example

```yaml
week: "2026-W20"
title: "Weekly Delivery Narrative - 2026-W20"
subtitle: "Admin usability, checkout accuracy, and marketplace admin behavior"
summary:
  objective: "The week covered checkout fixes, marketplace admin issues, and admin usability follow-through."
  why_it_matters: "The brief shows the work completed, the items that were checked, and the small set still open."
  evidence:
    - "6 tickets were done by week close."
    - "4 tickets remained in pending review."
    - "Multiple completed items were verified in staging."
sections:
  - key: "weekly-story"
    title: "The Week's Story"
    objective_summary: "The work grouped into checkout accuracy, marketplace admin fixes, and admin usability follow-through."
    why_it_matters: "Grouping the work shows the shape of the week, while the detail below shows what was actually done."
    supporting_evidence:
      - "Checkout-related tickets addressed price display, discount breakdowns, and pay-link behavior."
      - "Marketplace-related tickets addressed unclear admin errors and access behavior."
      - "Admin usability tickets covered search, refresh, copy, and table behavior."
    work_detail:
      - "NGN-589: corrected item prices on the payment complete page after Pay Link checkout."
      - "NGN-562: checked discounted transaction details on fresh transactions and confirmed expected values."
      - "NGN-624 and NGN-628: handled marketplace admin error and access issues."
      - "NGN-600, NGN-630, NGN-631, and NGN-632: carried usability issues into review with concrete follow-through items."
    presenter_notes: "The work this week fell into three areas: checkout accuracy, marketplace admin fixes, and admin usability follow-through. This section covers each one with the specific tickets that represent the actual work done."
    takeaway: "The week was concentrated in a few visible workflows, with concrete ticket work in each one."
  - key: "executive-snapshot"
    title: "Executive Snapshot"
    objective_summary: "The week closed with six done items and four pending-review items."
    why_it_matters: "The remaining work is limited in scope and already defined."
    supporting_evidence:
      - "Several completed items were verified in staging."
      - "No major blockers were recorded in the stand-up notes."
    work_detail:
      - "Done items included checkout, reporting, and marketplace admin fixes."
      - "Pending-review items focused on admin usability rather than new investigation."
      - "Validation activity showed up in both ticket movement and staging notes."
    presenter_notes: "Six items were completed with staging verification, and four remain in the review queue with clear scope. No blockers were recorded."
    takeaway: "The week ended with checked fixes and a short open list."
  - key: "activity-flow"
    title: "Activity Flow"
    objective_summary: "Issues were documented, moved into work or review, and checked where possible."
    why_it_matters: "This shows progress through the week rather than only end-state counts."
    supporting_evidence:
      - "Done: NGN-561, NGN-562, NGN-589, NGN-590, NGN-624, NGN-628"
      - "Pending Review: NGN-600, NGN-630, NGN-631, NGN-632"
    work_detail:
      - "NGN-561 and NGN-562 moved through validation on payment-related behavior."
      - "NGN-624 and NGN-628 closed marketplace admin issues after follow-through."
      - "NGN-600, NGN-630, NGN-631, and NGN-632 formed the review queue for remaining admin usability work."
      - "MANUAL-001: updated internal deployment documentation was done as a side task without a Linear ticket."
    presenter_notes: "Tickets moved through several stages during the week: initial validation, ticket creation, verification in staging, and finally the review queue for remaining items. The flow shows progress rather than just end-state counts."
    takeaway: "The week ended with a small amount of open work, not with open uncertainty."
  - key: "priority-work"
    title: "Priority Work"
    objective_summary: "A smaller set of tickets captures the work completed, the checks performed, and the remaining open items."
    why_it_matters: "These items show the work with enough detail for team visibility without listing every ticket."
    supporting_evidence:
      - "NGN-589 corrected item prices on the payment complete page."
      - "NGN-562 verified discounted transaction detail values."
      - "NGN-624 and NGN-628 improved marketplace admin behavior."
      - "NGN-600, NGN-630, NGN-631, and NGN-632 remained in pending review."
    work_detail:
      - "NGN-589: fixed the display issue so completed payments showed the correct item prices."
      - "NGN-562: verified discounted transaction detail values on new transactions instead of relying on assumption."
      - "NGN-624: addressed the marketplace admin error path."
      - "NGN-628: checked marketplace app installation access behavior."
      - "NGN-600: followed up on Partner Users search reload behavior."
      - "NGN-630: followed up on service provider refresh behavior after create."
      - "NGN-631: followed up on contact email copy behavior in customer details."
      - "NGN-632: followed up on customer table navigation and cutoff behavior."
    presenter_notes: "On priority work, NGN-589 fixed the item price display on the Payment Complete page so users see the actual item cost instead of zero dollars after a Pay Link checkout. The fix uses a fallback that multiplies unit price by quantity when the item total field is missing in the success-state response. NGN-562 verified the Transaction Details cost breakdown for discounted Pay Links in staging, confirming the Subtotal, Discount, and Total Charge values are correct on freshly created transactions. NGN-624 and NGN-628 improved marketplace admin behavior: the duplicate category slug now shows a readable validation toast instead of a raw Prisma error, and App Installs loads without the previous GraphQL environment and permissions errors. Both were verified in staging. NGN-600, NGN-630, NGN-631, and NGN-632 remain in pending review for admin usability follow-through: Partner Users search reload, service provider list refresh, clipboard copy, and customer table navigation."
    takeaway: "The priority set should show both completed fixes and pending open items."
  - key: "impact"
    title: "What Changed"
    objective_summary: "Several common workflows now return clearer results or have a defined open item."
    why_it_matters: "This ties the ticket work back to what changed in the product or in the work queue."
    supporting_evidence:
      - "Checkout values and transaction details were corrected or verified."
      - "Marketplace admin error handling was clarified."
      - "Search and table behavior issues were isolated into the remaining queue."
    work_detail:
      - "Completed checkout tickets reduced incorrect or unclear payment details."
      - "Marketplace admin tickets removed or clarified error cases."
      - "The remaining usability items were narrowed into specific review-ready tasks instead of broad complaints."
    presenter_notes: "The main results this week: checkout values and transaction details are now correct or verified, marketplace admin errors are readable instead of raw output, and the remaining queue is four specific usability items rather than open-ended investigation."
    takeaway: "The main result is clearer workflow behavior and a cleaner remaining queue."
  - key: "open-items"
    title: "Open Items"
    objective_summary: "The remaining work is already defined in the queue."
    why_it_matters: "The open queue is already defined."
    supporting_evidence:
      - "NGN-600 covers Partner Users search reload behavior."
      - "NGN-630 covers service provider refresh behavior."
      - "NGN-631 covers clipboard copy behavior."
      - "NGN-632 covers customer table navigation and cutoff behavior."
    work_detail:
      - "The queue starts with four known review items rather than new intake."
      - "Each item already has a clear behavior to validate or close."
      - "The queue is concentrated in admin usability follow-through."
    presenter_notes: "The open queue has four scoped items: Partner Users search reload, service provider list refresh, clipboard copy, and customer table navigation. Each has concrete reproduction steps and clear acceptance criteria. No blockers are in the way."
    takeaway: "The queue remains short and specific."
closing:
  objective: "The week covered completed fixes, completed checks, and a short list of remaining open items."
  presenter_notes: "Six items done with staging verification, four open items with clear scope, and zero blockers. The open queue is concentrated in admin usability follow-through with concrete reproduction steps on each item."
```

## Notes

1. Keep the brief objective and source-backed.
2. Avoid persuasive or celebratory phrasing.
3. Give `$revealjs-presenter` enough information to compose slides without re-reading raw dump files.
4. Use `work_detail` to preserve the ticket and task visibility that would be lost in a thin summary.
5. When the user asks for in-depth coverage, expand the `sections` list so individual tickets can become their own sections instead of being flattened into grouped summaries.
6. Manual task IDs use the `MANUAL-###` prefix. Treat them alongside tickets in all sections, using only title, status, and activity notes as evidence. Keep manual task narration factual and brief.
7. Never include dates, days of the week, or temporal markers in any section, presenter note, or work detail field. This is a weekly summary report. The brief communicates what happened, not when it happened.
8. Never use ticket data from the `# Unselected Tickets` dump section. Unselected tickets are carry-over candidates only and must not appear in `summary.evidence`, `sections[*].work_detail`, `sections[*].supporting_evidence`, `open-items`, or `closing`. The only exception is when the same ticket ID also appears in `# Selected Tickets` or `# All Scraped Tickets`.
9. Assign each piece of information to exactly one section. If a ticket problem description appears in `weekly-story`, do not repeat it in `priority-work` or `impact`. If a status count appears in `executive-snapshot`, do not restate it in `closing`. The `priority-work` section is the primary home for ticket-level detail; all other sections must reference tickets with short pointers rather than restating full descriptions.
