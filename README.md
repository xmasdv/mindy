# Mindy

Mindy is an early open-source desktop email client for multi-account independent professionals and reachable former Postbox users. It aims to make daily email simple, beautiful, fast, and reliable without accumulating feature bloat.

> **Status: personalization in progress.** A pinned Thunderbird/Gecko checkout and downstream patch flow have produced a working Windows 11 x64 Thunderbird-derived executable. It remains Thunderbird-branded and is not a supported Mindy package or installation.

Mindy is intended as a small downstream of Thunderbird ESR and Gecko. It is not Thunderbird, Mozilla, Postbox, eM Client, or Outlook, and it is not affiliated with their owners. Those names and trademarks belong to their respective owners.

Mindy is not currently webmail, an email provider, a production application, a download, or a complete Postbox replacement.

## Product principles

1. Make the frequent email workflow obvious and fast.
2. Preserve full account and folder access instead of hiding protocol reality.
3. Reuse mature Thunderbird capabilities and keep Mindy's downstream patch set small and isolated.
4. Protect identity selection, mailbox data, profiles, and update trust before adding convenience.
5. Establish Mindy's identity and core mail workspace before considering optional new capabilities.

## MVP at a glance

**Decided**

- Initial pilot platform: Windows 11 x64.
- Primary work surface: Unified Inbox and unified special folders.
- Equal-access secondary work surface: the complete per-account folder tree.
- Visual direction: an original Mindy shell, not a Thunderbird recolor or Outlook imitation.
- Calendar and contacts: accessible and account-backed, but not redesigned for MVP.
- Brand foundation: the Precision Workspace shell and provisional M-envelope identity documented in [DESIGN.md](DESIGN.md).

**Deferred**

- macOS and Linux pilots, without rejecting future support.
- Mobile, webmail/SaaS, teams, enterprise administration, and a full calendar or contacts redesign.
- Managed AI, personal memory, embeddings, knowledge graphs, and continual training.
- Local AI capabilities, until personalization and inherited mail workflows are established and deliberately reassessed.

## Inherited and custom scope

| Area | Source | MVP position |
|---|---|---|
| Gmail, Microsoft, and generic IMAP/SMTP accounts | Thunderbird | Inherited capability; Mindy must validate it through its shell and pilot workflows. |
| Identities, aliases, signatures, filters, search, offline/profile behavior, and security | Thunderbird | Inherited capability; correctness and regression coverage remain Mindy responsibilities. |
| Calendar, contacts, OpenPGP, S/MIME, and import/export | Thunderbird | Inherited and kept accessible; no broad redesign. |
| Mindy navigation and visual shell | Mindy | Custom MVP work. |
| Migration discovery and entry point | Mindy | Custom MVP work; this is not a promise of a completed Postbox importer. |
| Local draft assistant | Mindy | Deferred custom work; existing security boundaries remain requirements if it is resumed. |
| Pilot instrumentation | Mindy | Custom, consent-safe, content-free validation support. |

Inherited does not mean gap-free. The pinned baseline is Thunderbird 140.13.0esr; Exchange calendar/contact and Google Tasks limitations must be revalidated against it before pilot claims are made. Other notable caveats include no native scheduled send or Gmail-style undo send and no guaranteed official Postbox importer. Mindy does not claim OS-keychain protection or full-profile encryption.

## Documentation

| Document | Purpose |
|---|---|
| [Product](docs/PRODUCT.md) | Users, jobs, scope, interaction boundaries, and validation gates. |
| [Design](DESIGN.md) | Durable visual identity, layout, color, motion, state, and accessibility authority. |
| [Architecture](docs/ARCHITECTURE.md) | Intended downstream architecture, trust boundaries, and design status. |
| [Security](docs/SECURITY.md) | Threat model, invariants, telemetry exclusions, and disclosure guidance. |
| [Roadmap](docs/ROADMAP.md) | Phase order, exit criteria, and deferred work. |
| [Identity and services](docs/MINDY-IDENTITY-AND-SERVICES.md) | Development identity defaults, service ownership limits, and release evidence. |
| [Contributing](CONTRIBUTING.md) | Contribution, external build-storage, and review rules. |
| [Open-source model](docs/OPEN_SOURCE.md) | Core licensing, contribution terms, and sustainable development boundaries. |

These canonical documents define the public project. Existing market-research artifacts are supporting inputs only and are not authoritative product or engineering specifications.

## Participate

Open an issue to discuss evidence or a user problem. Code implementation requires a linked issue labeled `approved-for-implementation` by a maintainer; unsolicited or unscoped code pull requests may be closed, and only maintainers merge canonical changes. Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing work.

Do not file security vulnerabilities as public issues. Follow the private reporting guidance in [SECURITY.md](docs/SECURITY.md#reporting-a-vulnerability).

## License

Mindy's core is licensed under the [Mozilla Public License 2.0](LICENSE), which permits commercial use subject to its terms. Thunderbird-derived files retain their applicable MPL obligations. Future separately distributed services or assets may use explicitly stated terms; see the [open-source model](docs/OPEN_SOURCE.md).

## Development build status

The repository contains immutable upstream pins, bootstrap tooling, and an ordered downstream patch flow. Native source and object files must remain outside OneDrive: the repository's `vendor/` path is a junction to `C:\mozilla-source\mindy\vendor`, and the current object directory is physically `C:\mozilla-source\mindy\vendor\gecko\obj-mindy-pilot`.

Builds must remain external and resource-bounded. A local pilot build has succeeded, but no supported release, installer, publisher identity, signing infrastructure, or production update service is claimed here.
