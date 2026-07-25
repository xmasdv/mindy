# Mindy

Mindy is an early, pre-implementation open-source desktop email client project for multi-account independent professionals and reachable former Postbox users. It aims to make daily email simple, beautiful, fast, and reliable without accumulating feature bloat.

> **Status: pre-implementation.** Product proposal and specification work exists in Engram, and the technical design is nearly complete, but the final design phase gate has not passed. There is no product source checkout, runnable build, package, or supported installation yet.

Mindy is intended as a small downstream of Thunderbird ESR and Gecko. It is not Thunderbird, Mozilla, Postbox, eM Client, or Outlook, and it is not affiliated with their owners. Those names and trademarks belong to their respective owners.

Mindy is not currently webmail, an email provider, a production application, a download, or a complete Postbox replacement.

## Product principles

1. Make the frequent email workflow obvious and fast.
2. Preserve full account and folder access instead of hiding protocol reality.
3. Reuse mature Thunderbird capabilities and keep Mindy's downstream patch set small and isolated.
4. Protect identity selection, mailbox data, profiles, and update trust before adding convenience.
5. Keep optional local AI narrow, inspectable, and unable to act on a mailbox.

## MVP at a glance

**Decided**

- Initial pilot platform: Windows 11 x64.
- Primary work surface: Unified Inbox and unified special folders.
- Equal-access secondary work surface: the complete per-account folder tree.
- Visual direction: an original Mindy shell, not a Thunderbird recolor or Outlook imitation.
- Calendar and contacts: accessible and account-backed, but not redesigned for MVP.
- AI: an optional, separately downloaded local draft assistant with no mailbox actions.

**Deferred**

- macOS and Linux pilots, without rejecting future support.
- Mobile, webmail/SaaS, teams, enterprise administration, and a full calendar or contacts redesign.
- Managed AI, personal memory, embeddings, knowledge graphs, and continual training.

## Inherited and custom scope

| Area | Source | MVP position |
|---|---|---|
| Gmail, Microsoft, and generic IMAP/SMTP accounts | Thunderbird | Inherited capability; Mindy must validate it through its shell and pilot workflows. |
| Identities, aliases, signatures, filters, search, offline/profile behavior, and security | Thunderbird | Inherited capability; correctness and regression coverage remain Mindy responsibilities. |
| Calendar, contacts, OpenPGP, S/MIME, and import/export | Thunderbird | Inherited and kept accessible; no broad redesign. |
| Mindy navigation and visual shell | Mindy | Custom MVP work. |
| Migration discovery and entry point | Mindy | Custom MVP work; this is not a promise of a completed Postbox importer. |
| Local draft assistant | Mindy | Optional custom MVP work, disabled until its runtime and model are separately downloaded. |
| Pilot instrumentation | Mindy | Custom, consent-safe, content-free validation support. |

Inherited does not mean gap-free. Notable caveats include incomplete Microsoft Exchange calendar/contact support in Thunderbird 153 ESR, no native scheduled send or Gmail-style undo send, no guaranteed official Postbox importer, and a Google Tasks gap. Mindy does not claim OS-keychain protection or full-profile encryption.

## Documentation

| Document | Purpose |
|---|---|
| [Product](docs/PRODUCT.md) | Users, jobs, scope, interaction boundaries, and validation gates. |
| [Architecture](docs/ARCHITECTURE.md) | Intended downstream architecture, trust boundaries, and design status. |
| [Security](docs/SECURITY.md) | Threat model, invariants, telemetry exclusions, and disclosure guidance. |
| [Roadmap](docs/ROADMAP.md) | Phase order, exit criteria, and deferred work. |
| [Contributing](CONTRIBUTING.md) | Pre-code contribution and review rules. |
| [Open-source model](docs/OPEN_SOURCE.md) | Core licensing, contribution terms, and sustainable development boundaries. |

These canonical documents define the public project. Existing market-research artifacts are supporting inputs only and are not authoritative product or engineering specifications.

## Participate

Open an issue to discuss evidence or a user problem. Code implementation requires a linked issue labeled `approved-for-implementation` by a maintainer; unsolicited or unscoped code pull requests may be closed, and only maintainers merge canonical changes. Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing work.

Do not file security vulnerabilities as public issues. Follow the private reporting guidance in [SECURITY.md](docs/SECURITY.md#reporting-a-vulnerability).

## License

Mindy's core is licensed under the [Mozilla Public License 2.0](LICENSE), which permits commercial use subject to its terms. Thunderbird-derived files retain their applicable MPL obligations. Future separately distributed services or assets may use explicitly stated terms; see the [open-source model](docs/OPEN_SOURCE.md).

## No runnable build yet

There are intentionally no build commands here. The upstream checkout, downstream scaffold, scripts, pins, identifiers, signing infrastructure, and update endpoints have not been established or validated. The first executable milestone is defined in the [roadmap](docs/ROADMAP.md).
