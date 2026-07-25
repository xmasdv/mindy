# Mindy Architecture

Mindy is planned as a branded downstream of Thunderbird ESR/Gecko, with a small isolated patch set and rapid intake of upstream security updates. This document records design intent; it does not describe an implemented system.

> **Design status:** Nearly complete, but the final phase gate has not passed. Unless marked **Decided**, every topology, component, file area, and release mechanism below is **Planned** and provisional.

## System context

| Boundary | Responsibility | Status |
|---|---|---|
| Thunderbird ESR/Gecko | Mail protocols, profiles, offline behavior, search, identities, security, calendar, contacts, and other mature services. | **Decided** dependency direction. |
| Mindy downstream | Product shell, integration seams, migration entry point, local draft assistant broker/UI, and pilot instrumentation. | **Planned** custom scope. |
| Mail and groupware providers | Remote account, message, calendar, and contact services. | External systems; provider behavior is not controlled by Mindy. |
| Local AI runtime/model | Optional local inference downloaded separately from the application. | **Planned** and disabled by default. |
| Release services | Signed application, runtime, model, and update distribution. | **Planned**; ownership and endpoints are **Unknown**. |

## Upstream and downstream boundary

**Decided**

- Track Thunderbird ESR/Gecko rather than forking protocol and profile services into a new stack.
- Keep Mindy changes small, isolated, and reviewable.
- Prioritize rapid upstream security intake.
- Treat inherited capability as an integration and regression surface, not as custom Mindy implementation.

**Planned**

- Maintain a superproject/overlay that records immutable upstream revisions and applies ordered downstream patches.
- Prefer stable extension, theme, and composition seams before patching upstream internals.
- Escalate unavoidable upstream changes as narrow patches with explicit rationale and tests.

## Intended source and build topology

The intended checkout uses the Firefox/Gecko source root with Thunderbird nested at `comm/`. Both revisions are to be pinned immutably, with compatibility recorded and checked through `.gecko_rev.yml`.

```text
Firefox/Gecko root                    Planned upstream checkout
|-- comm/                             Planned Thunderbird checkout
|-- .gecko_rev.yml                    Planned compatibility declaration/check
`-- Mindy-owned overlay/patch areas   Planned; exact locations unknown
```

Mozilla build and packaging surfaces are the intended foundation. A Windows release, signing, and update path is also planned. No checkout, scripts, or verified commands exist, so this document intentionally provides no runnable build instructions.

Exact upstream pins, patch seams, application identifiers, domains, update endpoints, certificates, and signing infrastructure are **Unknown** until scaffold and ownership validation.

## Shell architecture

**Decided behavior**

- Unified Inbox and unified special folders form the primary work surface.
- The complete per-account folder tree remains equally accessible.
- Account and sender identity context must remain visible across both modes.
- Calendar and contacts remain reachable without an MVP redesign.

**Planned structure**

- A Mindy-owned shell composes navigation, work surfaces, commands, and status from inherited Thunderbird services.
- Adaptation layers isolate shell components from unstable upstream implementation details.
- Custom state remains minimal; mailbox, account, identity, calendar, and contact truth stays in inherited services.

Visual treatment and component details remain downstream design work. Architecture must prevent the shell from becoming either a cosmetic Thunderbird skin or a parallel mail engine.

## Inherited-service boundary

| Inherited service | Mindy responsibility |
|---|---|
| Account and protocol services | Expose setup and errors coherently; regression-test supported providers. |
| Folder and message stores | Present unified and account views without duplicating authoritative data. |
| Identities, aliases, and signatures | Preserve selection and send correctness across shell workflows. |
| Search, filters, rules, and offline/profile behavior | Integrate existing surfaces and avoid unsupported replacement layers. |
| Calendar and contacts | Keep accessible and account-backed; disclose provider gaps. |
| OpenPGP and S/MIME | Preserve security behavior and avoid bypassing inherited checks. |
| Import/export | Provide discovery and entry, while distinguishing available paths from unsupported migration promises. |

## Local AI data flow

The local assistant is an optional drafting subsystem, not a mailbox agent.

```text
Explicit user selection
        |
Deterministic context broker
        |  allowed plaintext context only
Sandboxed local inference process
        |  generated plaintext only
Draft preview
        |  explicit user apply
Compose editor
```

**Decided invariants**

- Context is limited to the current thread or selected message plus sent exemplars explicitly selected by the user.
- The broker is deterministic, validates every request and response, and fails closed.
- The inference process has no network, credentials, tools, attachments, mailbox write APIs, autonomous search, embeddings, knowledge graph, or continual training.
- Output can only be previewed and explicitly applied as plaintext to a draft.
- The assistant cannot send, save, schedule, move, delete, label, or administer mailbox data.

Process sandbox details are **Planned** and must be validated on Windows before AI reaches a pilot. See [SECURITY.md](SECURITY.md#ai-and-subprocess-invariants).

## Release and update trust

**Planned:** Application, AI runtime, and AI model artifacts use separate trust and update paths. Each artifact is signed, version-constrained, and protected against rollback. Compromise or approval of one artifact class must not grant authority over another.

**Unknown:** Final ownership, identifiers, distribution domains, endpoints, certificates, key custody, rotation, recovery, and incident procedures.

No production release pipeline or update service currently exists.

## Planned file areas

Names beyond established upstream locations are deliberately descriptive, not promises of final paths.

| Area | Intended contents | Status |
|---|---|---|
| Gecko root | Upstream Firefox/Gecko checkout. | **Planned** |
| `comm/` | Upstream Thunderbird checkout. | **Planned** |
| `.gecko_rev.yml` | Immutable compatibility declaration/check. | **Planned** |
| Superproject metadata | Upstream pins and reproducibility inputs. | **Planned; path unknown** |
| Ordered patch area | Minimal downstream patch series and rationale. | **Planned; path unknown** |
| Mindy shell area | Navigation, visual shell, and integration adapters. | **Planned; seam and path unknown** |
| AI broker/sandbox area | Protocol, policy enforcement, local process, and tests. | **Planned; path unknown** |
| Packaging/update area | Windows branding, packaging, signing, and update configuration. | **Planned; ownership-dependent** |

## Testing layers

| Layer | Intended proof |
|---|---|
| Policy and unit | Navigation state, identity decisions, AI broker allowlists, serialization, and fail-closed behavior. |
| Upstream integration | Accounts, folders, messages, identities, search, offline state, calendar, contacts, and security surfaces still work through Mindy seams. |
| Profile fixtures | Multi-account, alias, folder, migration-discovery, encrypted-message, and failure scenarios without production credentials or personal data. |
| End to end | Windows account setup, dual navigation, compose/send identity, offline/restart, calendar/contact access, and AI preview/apply. |
| Security | Malicious email content, context injection, sandbox escape attempts, unauthorized writes/network use, signature failure, and rollback rejection. |
| Packaging and update | Reproducibility evidence, signed artifact verification, clean install, upgrade, rollback prevention, and separated trust paths. |
| Pilot validation | Consent-safe content-free events supporting the gates in [PRODUCT.md](PRODUCT.md#provisional-validation-gates). |

Exact frameworks and commands are **Unknown** until the scaffold exists.

## Open task-level question

**Unknown:** Can the initial upstream scaffold simultaneously validate compatible immutable Gecko/Thunderbird pins, identify maintainable shell patch seams, and establish ownership-dependent release identifiers and trust infrastructure without expanding the downstream patch budget?

This question belongs to scaffold tasks and the final design gate; it must not be answered by invented identifiers or untested build instructions.

## Related documents

[Overview](../README.md) | [Product](PRODUCT.md) | [Security](SECURITY.md) | [Roadmap](ROADMAP.md) | [Contributing](../CONTRIBUTING.md)
