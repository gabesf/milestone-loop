---
name: app-overview
description: Step 1 of the milestone-loop workflow. Creates the application
  overview document for the approver's sign-off, and records the project's
  Language.
disable-model-invocation: true
---

# Application overview (approval document)

Create `docs/overview.md`: a non-technical description of the application
whose purpose is to get the approver's sign-off before any implementation
planning happens. The approver and the language rules are defined in the
conventions' "Approver" and "Language and labels" sections.

## Preflight

1. Ensure `docs/` exists at the repository root — create it if it doesn't. The
   overview document is always created inside this folder.
2. If `docs/overview.md` already exists, ask whether to revise it or
   start over. Never silently overwrite.
3. Read the `conventions` reference: `../conventions/SKILL.md` relative to
   this skill's base directory, or the `conventions` skill by name on hosts
   that don't state it. Load the stack reference as its "Stack reference"
   section says (at this step the `Stack:` line may not exist yet; that's
   fine) and apply its section for this skill before proceeding.

## Process

1. Ask the user for their description of the application and any existing
   documents (briefings, client emails, reference material). Ask explicitly
   for reference images too — mockups, moodboards, client art, screenshots
   of similar apps. Read/look at everything provided.
2. **Language.** If CLAUDE.md has no `Language:` line, ask which language
   the project's docs and chat should use, offering the language of the
   user's description as the default. Record `Language: <language>` in
   CLAUDE.md (create the file with just that line if it doesn't exist).
   **Push.** If CLAUDE.md has no `Push:` line, ask whether the workflow's
   commits go to the remote or stay local only, and record `Push: yes` or
   `Push: no` (conventions' "Push" section).
3. Save provided images under `docs/references/` with short descriptive
   kebab-case names (e.g. `mockup-home-screen.png`). If an image only
   exists in an external doc the user pointed to, extract or ask for it —
   the repository copy is what later steps will use.
4. Ask clarifying questions BEFORE writing. This is expected and encouraged —
   ask about anything ambiguous: target audience, core interactions, success
   criteria, what is explicitly out of scope, target hardware (only if already
   defined). Batch questions into one message when possible; iterate if the
   answers open new questions.
5. Write the document.
6. Present it and iterate on feedback until the draft is stable.
7. **Grill pass (optional, encouraged).** Once the draft is stable and before
   it goes to the approver, suggest the user run `/grill-me` on the document to
   stress-test their understanding of the product. Explicitly tell them it is
   optional but encouraged. If `/grill-me` is not installed, offer to
   install it (conventions' "Grill-me" section). If the grilling surfaces
   questions the dev cannot answer, do not guess and do not drop them:
   compile them into a short question list for the dev to submit to the
   approver (solo project: the dev settles them in a second pass). This
   happens BEFORE the document is sent for approval — fold
   the approver's answers back into the document first.

## Document format

Headings are fixed; the body follows the project's Language. Structure:

# [Application name]
## Goal
## Context and audience
## Experience
## Requirements
## Visual references (only when images exist — otherwise omit the section)
## Hardware (only when already defined — otherwise omit the section)
## Out of scope

Rules for the Visual references section:
- Embed each image from `docs/references/` with a relative markdown link and
  a one-line caption saying what it illustrates.
- Images are reference material, not commitments — if a mockup shows
  something out of scope, say so in the caption.
- Images relevant to a specific requirement may also be embedded next to it
  in Requirements instead.

Rules for the Requirements section:
- Every requirement gets an ID: R-01, R-02, ... These IDs are load-bearing:
  the milestone plan will map milestones to them, so each requirement must be
  a single, short, verifiable statement. Split compound requirements.
- Written from the user's/visitor's perspective, not the developer's.

Rules for the whole document:
- Non-technical. No architecture, no frameworks, no implementation details.
  The only technical content allowed is the hardware section.
- The approver must be able to read it in a few minutes. Prefer clear and short
  over exhaustive.

## Closing

When the user confirms the document is final:
1. Save it, commit it together with `docs/references/` and CLAUDE.md on
   the integration branch with message `docs: application overview` and
   push (unless `Push: no`), under the conventions' "Integration branch",
   "Push" and "Git safety" sections.
2. Remind the user: the next step (`/plan-milestones`) should only run AFTER
   the approver signs off on this document (on a solo project: after their
   own re-read). That approval is a human gate — do not offer to continue
   past it in this session.
