# Mindy Architecture

Mindy is an independent downstream of Thunderbird ESR/Gecko, with immutable upstream pins, an ordered isolated patch set, and rapid intake of upstream security updates. A working Thunderbird-derived baseline exists; Mindy's distinct branding and workspace remain in progress.

> **Implementation status:** The source/bootstrap topology and local Windows build baseline are verified. Unless marked **Established** or **Decided**, components and release mechanisms below remain **Planned**, **Deferred**, or **Unknown**.

## System context

| Boundary | Responsibility | Status |
|---|---|---|
| Thunderbird ESR/Gecko | Mail protocols, profiles, offline behavior, search, identities, security, calendar, contacts, and other mature services. | **Decided** dependency direction. |
| Mindy downstream | Product identity, shell, integration seams, migration entry point, and pilot instrumentation. | **In progress** custom scope. |
| Mail and groupware providers | Remote account, message, calendar, and contact services. | External systems; provider behavior is not controlled by Mindy. |
| Local AI runtime/model | Optional local inference downloaded separately from the application. | **Deferred**; no active implementation priority. |
| Release services | Signed application, runtime, model, and update distribution. | **Planned**; ownership and endpoints are **Unknown**. |

## Upstream and downstream boundary

**Decided**

- Track Thunderbird ESR/Gecko rather than forking protocol and profile services into a new stack.
- Keep Mindy changes small, isolated, and reviewable.
- Prioritize rapid upstream security intake.
- Treat inherited capability as an integration and regression surface, not as custom Mindy implementation.

**Established**

- Maintain a superproject/overlay that records immutable upstream revisions and applies ordered downstream patches.
- Keep native source and object files outside the OneDrive repository through the `vendor/` junction.

**Planned**
- Prefer stable extension, theme, and composition seams before patching upstream internals.
- Escalate unavoidable upstream changes as narrow patches with explicit rationale and tests.

## Source and build topology

The checkout uses the Firefox/Gecko source root with Thunderbird nested at `comm/`. Both revisions are pinned immutably, with compatibility recorded and checked through `.gecko_rev.yml`.

```text
Mindy repository (OneDrive)           Metadata, docs, tools, config, patches
`-- vendor/                           Junction to C:\mozilla-source\mindy\vendor
    `-- gecko/                        Pinned Firefox/Gecko source root
        |-- comm/                     Pinned Thunderbird source
        |-- .gecko_rev.yml            Compatibility declaration/check
        `-- obj-mindy-pilot/          External native build output
```

Mozilla build and packaging surfaces are the foundation. The bootstrap tooling, source pins, patch ordering, and one local Windows build have been verified. That executable remains Thunderbird-branded; it is not evidence of a supported release, installer, signing path, or production update service.

Native builds must remain external and resource-bounded. Do not move source or object output into OneDrive. Application identifiers, domains, update endpoints, certificates, and signing infrastructure remain **Unknown** pending ownership validation.

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

Visual authority now lives in [DESIGN.md](../DESIGN.md). Architecture must prevent the shell from becoming either a cosmetic Thunderbird skin or a parallel mail engine.

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

The local assistant is deferred. If resumed, it is an optional drafting subsystem, not a mailbox agent.

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
| `vendor/gecko/` | Pinned upstream Firefox/Gecko checkout through the external junction. | **Established** |
| `vendor/gecko/comm/` | Pinned upstream Thunderbird checkout. | **Established** |
| `vendor/gecko/comm/.gecko_rev.yml` | Immutable compatibility declaration/check. | **Established** |
| `sources.lock`, `config/`, `tools/` | Upstream pins, build configuration, bootstrap, and verification inputs. | **Established** |
| `patches/` | Ordered minimal downstream patch series and rationale. | **Established** |
| Mindy shell area | Navigation, visual shell, and integration adapters. | **In progress; final seams remain planned** |
| AI broker/sandbox area | Protocol, policy enforcement, local process, and tests. | **Deferred; path unknown** |
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

Focused bootstrap verification exists. Broader shell, inherited-service, packaging, security, and pilot test commands remain **Planned** and must be documented only after verification.

## Open task-level question

**Unknown:** Can Mindy's branding and Precision Workspace shell replace Thunderbird identity cleanly while preserving maintainable upstream seams and avoiding unowned release identifiers or trust infrastructure?

This question belongs to personalization and release-readiness work; it must not be answered with invented identifiers or unverified packaging claims.

## Related documents

[Overview](../README.md) | [Product](PRODUCT.md) | [Security](SECURITY.md) | [Roadmap](ROADMAP.md) | [Contributing](../CONTRIBUTING.md)
