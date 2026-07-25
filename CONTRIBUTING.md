# Contributing to Mindy

Mindy is currently a pre-code project. Community members are welcome to open issues, discuss evidence, and describe user problems. Contributions should reduce uncertainty in the product, architecture, security model, or delivery plan without implying that a source tree or runnable build already exists.

## Issue-first governance

- Start proposed work with a public issue unless it concerns a security vulnerability.
- Code implementation requires a linked issue that a maintainer has labeled `approved-for-implementation`.
- Follow the scope authorized in that issue and any maintainer-owned design or task artifact. Unsolicited or unscoped code pull requests may be closed.
- Only maintainers merge changes into the canonical Mindy repository.
- MPL-2.0 permits external forks subject to its terms, but changes in a fork do not alter canonical Mindy unless a maintainer merges them here.
- Never report a security vulnerability in a public issue. Follow the private process in [SECURITY.md](docs/SECURITY.md#reporting-a-vulnerability).

## Before proposing work

1. Read the [project overview](README.md), [product definition](docs/PRODUCT.md), [architecture](docs/ARCHITECTURE.md), [security model](docs/SECURITY.md), [roadmap](docs/ROADMAP.md), and [open-source model](docs/OPEN_SOURCE.md).
2. Open or join an issue to discuss scope before producing broad designs, generated code, patch sets, or implementation plans.
3. Identify whether the change belongs upstream, in a small downstream patch, or in an isolated Mindy-owned component.
4. State what is decided, planned, deferred, and unknown. Do not present design intent as implemented behavior.

## Scope rules

- Protect the small, isolated downstream patch-set strategy.
- Prefer inherited Thunderbird capability over a parallel Mindy implementation when the inherited behavior meets the product need.
- Reject feature bloat that does not support the defined MVP jobs or pilot decisions.
- Do not copy Postbox, eM Client, Thunderbird, Outlook, or other products' proprietary assets.
- Do not introduce source code or broad patches without an accepted design and task-level artifact.
- Do not add build instructions until a checkout and scripts exist and the commands have been verified.
- Keep technical artifacts and issue titles or descriptions in professional English where practical.
- Participate respectfully; critique ideas and evidence, not people.

## Contribution license

The Mindy core is licensed under the [Mozilla Public License 2.0](LICENSE). Unless a path explicitly states another compatible license, contributions submitted to this repository are provided under MPL-2.0. Preserve all applicable upstream and third-party notices.

There is no Contributor License Agreement. The project does not promise future relicensing; relicensing third-party contributions would require adequate contributor rights and a separate governance decision. See the [open-source model](docs/OPEN_SOURCE.md). This project documentation is not legal advice.

## Security-sensitive changes

Changes involving mailbox content, profiles, identity selection, authentication, AI context, subprocesses, updates, downloads, signing, telemetry, or migration must include:

- Assets and trust boundaries affected.
- Abuse and failure cases, including malicious inbound email.
- Fail-closed behavior.
- Data read, written, retained, or transmitted.
- Tests that prove the relevant invariants in [SECURITY.md](docs/SECURITY.md).

Security constraints are acceptance criteria, not cleanup work.

Do not disclose vulnerabilities or sensitive details in public issues. Use the private process in [SECURITY.md](docs/SECURITY.md#reporting-a-vulnerability).

## Testing expectations

**Current:** Documentation changes must be checked for internal consistency, accurate status labels, valid relative links, and unsupported claims.

**Planned after the scaffold exists:** Every behavior change must have coverage at the lowest useful layer, plus integration or end-to-end coverage where an upstream boundary, mailbox state, identity, installer, update, or AI sandbox is involved. The intended layers are described in [ARCHITECTURE.md](docs/ARCHITECTURE.md#testing-layers).

No contributor should claim tests, builds, or automation ran unless they exist and were actually executed.

## Commits and pull requests

These conventions describe the intended review discipline; no repository automation is currently claimed.

- Keep commits as reviewable work units with tests and documentation beside the behavior they explain.
- Use concise conventional commit subjects, such as `docs: define pilot gates`.
- Keep pull requests focused on one decision or implementation slice.
- Link the approved issue and any applicable maintainer-owned design or task artifact.
- Explain intent, scope, security impact, verification, inherited-versus-custom boundaries, and known follow-up work.
- Avoid generated churn and unrelated formatting changes.
- Do not add AI attribution or `Co-authored-by` trailers.

## Documentation ownership

Update the document that owns the changed decision instead of duplicating long explanations:

| Change | Canonical document |
|---|---|
| User, workflow, MVP, or validation | [PRODUCT.md](docs/PRODUCT.md) |
| Components, boundaries, topology, or tests | [ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Threats, invariants, trust, or disclosure | [SECURITY.md](docs/SECURITY.md) |
| Sequence, phase gate, or deferral | [ROADMAP.md](docs/ROADMAP.md) |
| Project summary or document map | [README.md](README.md) |
| Contribution and review practice | This file |
