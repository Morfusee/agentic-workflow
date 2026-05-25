# Ticket Dump

Generated: 2026-05-25 22:06 UTC
Requested range: 2026-05-25
Dump file date: 2026-05-25

---

# Stand-up Script

Yesterday, I reviewed Mitch's PR for the Global Schema implementation and asked for a few changes on the code. I also coordinated with Mikko to request that the assets be sent over as SVGs so we could use them in the email template. I continued working on the email footer template — the mockup changed completely, so I had to make some major revisions, but I integrated the new SVG assets into the template. I also had a quick call with Ibrahim about the Certification Pages Redesign, created a collaboration space for the team of four, and set up an alignment meeting so we can sync on that task.

Today, I plan to continue working on the LLMs.txt task, polish and finalize the Email Footer Template, and coordinate with Mikko for the collation of the footer with his Email Header Template.

No major blockers right now.

---

# Selected Tasks

- 86d31nyg2: Global Schema
  - Status: code review
  - Activity date: 2026-05-25
  - URL: https://app.clickup.com/t/86d31nyg2
  - Reference: `# All Scraped Tasks` -> `## 86d31nyg2: Global Schema`
  - Stand-up relevance: Reviewed PR and asked for code changes; coordinated for SVG assets

- 86d31eyzz: Implement email footer template
  - Status: in progress
  - Activity date: 2026-05-25
  - URL: https://app.clickup.com/t/86d31eyzz
  - Reference: `# All Scraped Tasks` -> `## 86d31eyzz: Implement email footer template`
  - Stand-up relevance: Continued implementation with major revisions after mockup change; integrated new SVG assets

- 86d2ymvcu: Certification Pages Redesign
  - Status: in progress
  - Activity date: 2026-05-25
  - URL: https://app.clickup.com/t/86d2ymvcu
  - Reference: `# All Scraped Tasks` -> `## 86d2ymvcu: Certification Pages Redesign`
  - Stand-up relevance: Had alignment call with Ibrahim; created team space and meet invite

- [Manual] MANUAL-001: Created collaboration space for team of 4
  - Status: Done
  - Activity date: 2026-05-25
  - Reference: `# Manual Tasks` -> `## MANUAL-001: Created collaboration space for team of 4`
  - Stand-up relevance: Set up workspace for the Page Redesign team

- 86d32pnat: CMS-managed content served at /llms.txt
  - Status: in progress
  - Activity date: 2026-05-21
  - URL: https://app.clickup.com/t/86d32pnat
  - Reference: `# All Scraped Tasks` -> `## 86d32pnat: CMS-managed content served at /llms.txt`
  - Stand-up relevance: Selected for next-day plan; will continue working on it

- [Manual] MANUAL-002: Created alignment meet invite for Page Redesign task
  - Status: Done
  - Activity date: 2026-05-25
  - Reference: `# Manual Tasks` -> `## MANUAL-002: Created alignment meet invite for Page Redesign task`
  - Stand-up relevance: Scheduled sync meeting for the four-person team

---

# Unselected Tasks

Carry-over tasks not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

No unselected tasks — all tasks from this dump were selected.

---

# Manual Tasks

## MANUAL-001: Created collaboration space for team of 4

Status: Done
Activity date: 2026-05-25
My role: dev-owner

### Description
Created a collaboration space for the four-person team to work on shared tasks including the Certification Pages Redesign and email template work.

### Activity Notes
Created the space to facilitate coordination across the Global Schema, email footer, and Page Redesign tasks.

## MANUAL-002: Created alignment meet invite for Page Redesign task

Status: Done
Activity date: 2026-05-25
My role: dev-owner

### Description
Created a meeting invite for an alignment call regarding the Certification Pages Redesign task for the team of four.

### Activity Notes
Scheduled the alignment meeting to sync the team on the Page Redesign approach and deliverables.

---

# All Scraped Tasks

## 86d31nyg2: Global Schema

Status: code review
Activity date: 2026-05-25
URL: https://app.clickup.com/t/86d31nyg2
Initial dev assignee: MITCH CABRERA
Testing actors: None identified
My role for this task: contributor

### Why this task was included
User-reported activity on 2026-05-25: reviewed Mitch's Global Schema PR and coordinated w Mitch to request assets be sent as SVGs for the email template. ClickUp shows no user activity for this task on 2026-05-25; inclusion is based on user's explicit report.

### Description
Acceptance Criteria
SchemaGenerator should be aptly renamed to PageSchemaGenerator (which will be used more in the next tickets)
GlobalSchemaGenerator which create the schema below for all app pages
All pages of the website should pass validation in
There should be a public folder that contains the logo (perhaps compress the logo)
This needs to be present on all pages. Currently there is a SchemaGenerator that creates a schema specifically for the faq page

{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Mapúa Malayan Digital College",
  "alternateName": "MMDC",
  "url": "https://www.mmdc.mcl.edu.ph/",
  "inLanguage": ["en", "fil"],
  "publisher": {
    "@type": "Organization",
    "name": "Mapúa Malayan Digital College",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.mmdc.mcl.edu.ph/2023-MMDC-Logo.png",
      "width": 512,
      "height": 512
    }
  }
}

### Comments
#### MITCH CABRERA - 2026-05-20 12:49 UTC
Implemented the Global Schema ticket requirements and attached the PR for review. Also verified the schema rendering and validation locally, including the global WebSite schema and existing FAQ schema functionality.

PR:
github.com/mmdc-tech/website/pull/245

### Activity Timeline
- 2026-05-20 12:49 UTC: MITCH CABRERA commented with PR link
- 2026-05-25: User reported reviewing Mitch's PR and coordinating for SVG assets (not tracked in ClickUp)

### In-Range Day Mapping
- 2026-05-25: User reported reviewing PR and coordinating for SVG assets

### Activity Notes
Reviewed Mitch's PR for the Global Schema implementation. Coordinated with Mitch to request assets be sent as SVGs for the email template.

---

## 86d31eyzz: Implement email footer template

Status: in progress
Activity date: 2026-05-25
URL: https://app.clickup.com/t/86d31eyzz
Initial dev assignee: Mark Rolis Valenzuela
Testing actors: None identified
My role for this task: dev-owner

### Why this task was included
User-reported activity on 2026-05-25: continued working on the Email Template Footer. ClickUp shows no user activity for this task on 2026-05-25; inclusion is based on user's explicit report.

### Description
Description
Implement the email footer HTML template based on the attached footer mockup. All footer content is static.
Scope
Build footer HTML using table-based layout for email client compatibility
Implement static footer content matching the footer mockup
Base the template on the sample HTML attached to the epic
Deliverable
Template uses inline styles and table-based layout for email compatibility

### Comments
No comments found.

### Activity Timeline
- 2026-05-18 22:31 UTC: created by Mark Rolis Valenzuela
- 2026-05-18 22:31 UTC: linked to epic EM Email templates design
- 2026-05-19 15:36 UTC: last updated
- 2026-05-25: User reported continuing work (not tracked in ClickUp)

### In-Range Day Mapping
- 2026-05-25: User reported continuing work on Email Template Footer

### Activity Notes
Continued working on the Email Template Footer implementation.

---

## 86d2ymvcu: Certification Pages Redesign

Status: in progress
Activity date: 2026-05-25
URL: https://app.clickup.com/t/86d2ymvcu
Initial dev assignee: Not available
Testing actors: None identified
My role for this task: contributor

### Why this task was included
User-reported activity on 2026-05-25: coordinated with Ibrahim for the Page Redesign task, created a space for the team of 4, created a meet invite for an alignment call, and had a call with Ibrahim regarding the task. ClickUp shows no user activity for this task on 2026-05-25; inclusion is based on user's explicit report.

### Description
Mock up:

### Comments
No comments found.

### Activity Timeline
- 2026-05-11 12:14 UTC: created by Paul Fernandez
- 2026-05-20 20:26 UTC: last updated
- 2026-05-25: User reported coordinating with Ibrahim, creating team space, creating meet invite, and having a call (not tracked in ClickUp)

### In-Range Day Mapping
- 2026-05-25: User reported coordinating w Ibrahim, creating space, creating meet invite, having alignment call

### Activity Notes
Coordinated with Ibrahim for the Page Redesign task. Created a collaboration space for the team of 4. Created a meet invite for an alignment call regarding the Page Redesign task. Had a call with Ibrahim regarding the Page Redesign task.

---

## 86d32pnat: CMS-managed content served at /llms.txt

Status: in progress
Activity date: 2026-05-21
URL: https://app.clickup.com/t/86d32pnat
Initial dev assignee: Mark Rolis Valenzuela
Testing actors: None identified
My role for this task: dev-owner

### Why this task was included
User explicitly added to stand-up for next-day plan on 2026-05-25. ClickUp shows task was created by user on 2026-05-21; no in-range activity for 2026-05-25.

### Description
Definition of Done
We want to have a way in CMS where we can manage LLMs.txt content via a Payload entity.
Upon saving and syncing into production, content is served at https://mmdc.mcl.edu.ph/llms.txt similar to how robots.txt works.

References
Epic: https://app.clickup.com/t/86d32m54w
Read up: https://www.hostinger.com/tutorials/what-is-llms-txt

### Comments
No comments found.

### Activity Timeline
- 2026-05-21 14:35 UTC: created by Mark Rolis Valenzuela
- 2026-05-21 14:37 UTC: linked to epic LLMs.txt
- 2026-05-25: User selected for next-day plan (stand-up, not ClickUp activity)

### In-Range Day Mapping
- 2026-05-25: User added to stand-up for next-day plan

### Activity Notes
Task was created on 2026-05-21. User plans to continue working on it as next-day priority.
