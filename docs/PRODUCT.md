# Mindy Product Definition

<!-- impeccable:product-schema 1 -->

Mindy gives multi-account independent professionals a focused desktop email workspace without removing access to the full account structure they depend on.

**Status:** Product direction is **Decided** for design work. MVP details remain subject to the final design phase gate and pilot evidence. See the [roadmap](ROADMAP.md).

## Project state

Mindy is an early implementation project. A pinned upstream checkout, reproducible Windows build, and first downstream mail-shell seam exist; there is no supported installation yet. The initial pilot target is Windows 11 x64.

The approved **Precision Workspace** direction defines Mindy's primary inbox composition, visual tokens, responsive topology, and accessibility constraints. `DESIGN.md` is the durable system contract; the final logo asset remains provisional.

## Problem

People working independently across several email accounts need to process messages quickly while preserving correct sender identity, account boundaries, folders, offline access, and mature mail security. Existing clients can expose the required power but often make the daily workflow visually dense or force users to choose between a unified view and account-level control.

Mindy addresses that workflow problem. It is not an attempt to rebuild every groupware feature or create a new mail service.

## Users

### Target users

- Independent professionals who actively use multiple email accounts.
- People who value a native, installable desktop workflow and full folder access.
- Reachable former Postbox users seeking a sustainable desktop client direction.

### Non-target users for MVP

- Teams requiring shared workspaces or collaboration features.
- Enterprises requiring centralized administration or policy management.
- Users seeking webmail, SaaS, or mobile clients.
- Users whose primary need is a redesigned calendar, contacts suite, or task manager.
- Users seeking autonomous or cloud-managed AI.

## Jobs to be done

1. See and process important mail across accounts in one coherent work surface.
2. Move immediately from the unified view to any account and folder without losing orientation.
3. Reply from the correct identity with the expected signature and account behavior.
4. Search, filter, work offline, and use established encryption and certificate features.
5. Access account-backed calendars and contacts without making them the MVP design focus.
6. Discover available migration paths when moving from an existing client.
7. Optionally draft or revise text locally while retaining complete control over the result.

## Product principles

| Principle | Product consequence |
|---|---|
| Simple | Prioritize the recurring mail workflow; disclose advanced capability progressively. |
| Beautiful | Build a structurally original Mindy shell rather than recoloring Thunderbird or imitating Outlook. |
| Fast | Keep interaction paths short and validate responsiveness; do not claim performance before measurement. |
| Reliable | Preserve identity, folder, message, profile, and offline correctness ahead of novelty. |
| Focused | Inherit mature services and resist parallel features or broad redesigns. |

## Core workflow: two equal navigation modes

**Decided:** Neither mode is a fallback.

### Unified work surface

The default daily view centers Unified Inbox and unified special folders. It supports triage and processing across accounts while keeping account and identity context visible.

### Full account tree

The complete per-account folder tree is equally accessible. Users can inspect provider-specific and custom folders, understand where data lives, and perform account-scoped work without fighting the unified view.

### Shell constraint

The shell must be structurally Mindy's own information architecture and interaction design. It must not copy Postbox or eM Client assets, reduce the work to a Thunderbird recolor, or imitate Outlook.

## MVP scope

### Inherited capability to expose and validate

- Gmail, Microsoft, and generic IMAP/SMTP account support.
- Identities and aliases, signatures, filters and rules, search, offline/profile behavior, and mail security.
- Calendar and contacts, OpenPGP and S/MIME, and import/export surfaces.

These are Thunderbird capabilities, not Mindy custom-feature claims. Mindy still owns shell integration, regression testing, and an honest presentation of inherited limitations.

### Custom Mindy work

- The dual-navigation Mindy shell.
- A migration discovery and entry point, without promising a completed Postbox importer.
- An optional local draft assistant within the boundary below.
- Consent-safe, content-free instrumentation for pilot validation.

### Out of scope

- Webmail/SaaS, mobile, teams, and enterprise administration.
- Full calendar or contacts redesign.
- A managed AI service.
- Full personal memory, embeddings, a knowledge graph, or continual training.
- Autonomous mailbox operations.

## AI interaction boundary

**Decided:** The assistant drafts text; the user remains the only actor.

| Allowed | Prohibited in MVP |
|---|---|
| Optional use, disabled until a runtime and model are separately downloaded. | Cloud inference or network access. |
| Current thread or selected message as explicit context. | Credentials, attachments, tools, or autonomous search. |
| Sent-message exemplars selected explicitly by the user. | Embeddings, knowledge graphs, continual training, or implicit personal memory. |
| Plaintext draft preview and user-controlled apply. | Sending, saving, scheduling, moving, deleting, labeling, or administering anything. |

Generated text is untrusted output. It enters the compose editor only after preview and an explicit user action; normal compose and send safeguards still apply. Technical enforcement is defined in [SECURITY.md](SECURITY.md) and [ARCHITECTURE.md](ARCHITECTURE.md#local-ai-data-flow).

## Calendar and contacts

**Decided:** Calendar and contacts remain accessible and account-backed in MVP.

**Planned:** Mindy's shell will preserve access and validate inherited behavior without redesigning these areas.

**Known caveat:** Microsoft Exchange calendar and contacts are not complete in Thunderbird 153 ESR. Google Tasks also has an inherited gap. These limitations must be represented honestly during account setup, migration discovery, and pilot support.

## Other inherited caveats

- Scheduled send and Gmail-style undo send are not native inherited capabilities.
- No official Postbox importer is guaranteed.
- OS-keychain storage and full-profile encryption must not be claimed.

## Provisional validation gates

These are pilot decision gates, not scientific market facts. Numeric thresholds are **Unknown** until the pilot protocol is approved; they must be set before participant data is evaluated, not retrofitted afterward.

| Gate | Evidence to collect | Provisional pass condition |
|---|---|---|
| Account connection | Real supported-provider setup attempts and failures. | Target accounts connect without unresolved data-integrity or security failures. |
| Multi-account use | Repeated unified and per-account workflows. | Participants can use both navigation modes without losing account context. |
| Identity and data integrity | Sender identity, signatures, folders, offline state, and message operations. | No unresolved wrong-identity, loss, corruption, or cross-account defects. |
| Retention | Weekly activity over a four-week pilot window. | The approved retention threshold is met with interpretable reasons for attrition. |
| AI edit acceptance | Preview, apply, edit, reject, and disable events without content capture. | The approved acceptance threshold is met without safety-boundary violations. |
| Support burden | Setup and recurring support incidents. | Burden remains within the approved capacity threshold. |
| Willingness to pay | Structured participant feedback after meaningful use. | The approved threshold supports continued product investment. |

## Related documents

[Overview](../README.md) | [Design](../DESIGN.md) | [Architecture](ARCHITECTURE.md) | [Security](SECURITY.md) | [Roadmap](ROADMAP.md) | [Contributing](../CONTRIBUTING.md)
