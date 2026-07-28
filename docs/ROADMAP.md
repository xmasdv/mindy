# Mindy Roadmap

Mindy advances through evidence-based phase gates rather than date promises. Each phase must satisfy its exit criteria before the next phase can be treated as committed implementation work.

**Current phase:** Mindy brand foundation and personalization of the verified Thunderbird-derived baseline.

## Phase path

| Phase | Outcome | Status |
|---|---|---|
| 1. Documentation and design gate | Canonical scope, architecture, security invariants, and visual authority are coherent. | **In progress** |
| 2. Upstream scaffold and reproducible Windows build | Compatible pinned upstream sources produce a repeatable Windows 11 x64 build. | **Baseline build verified; hardening remains** |
| 3. Mindy personalization and vertical shell slice | Branding and one end-to-end workflow prove Mindy's identity, shell, and upstream seams. | **In progress** |
| 4. Inherited regression surface | Account, mail, identity, calendar, and contacts behavior is validated through Mindy. | **Planned** |
| 5. Optional local AI | The constrained draft assistant works without mailbox authority. | **Deferred pending reassessment** |
| 6. Consented pilot | Real users generate content-free evidence against provisional gates. | **Planned** |
| 7. Decision gate | Evidence determines whether to continue, revise, narrow, or stop. | **Planned** |

## 1. Documentation and design gate

### Work

- Keep the canonical document set internally consistent.
- Maintain [DESIGN.md](../DESIGN.md) as the durable visual authority.
- Distinguish inherited behavior, Mindy custom work, provisional details, and unknown ownership-dependent infrastructure.
- Define threat cases and pre-pilot validation thresholds.

### Exit criteria

- [ ] Product, architecture, security, roadmap, and contribution boundaries agree.
- [x] Brand thesis, semantic color roles, layout, motion, states, accessibility, and anti-patterns are documented.
- [ ] Canonical project documents remain consistent as personalization lands.
- [ ] No document confuses the verified local baseline with a Mindy-branded release, supported installation, signing system, or update service.

## 2. Upstream scaffold and reproducible Windows build

### Work

- Establish the Firefox/Gecko root with Thunderbird at `comm/`.
- Pin both upstream revisions immutably and check compatibility through `.gecko_rev.yml`.
- Establish the superproject/overlay and ordered minimal patch flow.
- Use Mozilla build and packaging surfaces for Windows 11 x64.
- Keep native source and object output outside OneDrive through the repository's `vendor/` junction and use resource-bounded builds.

### Exit criteria

- [ ] A clean environment can reproduce the documented Windows build from pinned inputs.
- [ ] Upstream compatibility and patch order fail clearly when invalid.
- [ ] The downstream patch inventory is small, isolated, reviewed, and justified.
- [ ] Provisional branding and release identifiers cannot be mistaken for owned production values.
- [ ] Baseline upstream tests and packaging smoke checks are recorded.

## 3. Mindy personalization and vertical shell slice

### Work

- Replace Thunderbird branding with the provisional Mindy identity without inventing production publisher or update values.
- Apply the [Precision Workspace visual authority](../DESIGN.md) without merely recoloring Thunderbird or imitating Outlook.
- Implement a narrow Mindy shell path spanning account data, Unified Inbox, per-account tree, message reading, and compose entry.
- Preserve visible account and identity context.
- Prove adaptation seams without creating a parallel mailbox model.

### Exit criteria

- [ ] One real supported account can complete the vertical workflow on Windows 11 x64.
- [ ] Unified and per-account navigation reach the same authoritative data safely.
- [ ] Identity context remains visible and correct through compose entry.
- [ ] The result is structurally Mindy, not a recolor or imitation.
- [ ] Patch size and upstream coupling remain within the approved design boundary.

## 4. Inherited account, calendar, and contact regression surface

### Work

- Exercise Gmail, Microsoft, and generic IMAP/SMTP paths.
- Cover identities, aliases, signatures, filters, rules, search, offline/profile behavior, OpenPGP/S/MIME, and import/export discovery.
- Keep calendar and contacts accessible and account-backed.
- Represent inherited gaps honestly.

### Exit criteria

- [ ] Multi-account and alias scenarios pass identity and data-integrity tests.
- [ ] Offline, restart, provider-failure, and profile fixtures produce no unresolved loss or corruption.
- [ ] Calendar/contact access works for supported inherited cases.
- [ ] Exchange calendar/contact incompleteness, Google Tasks, scheduled-send, undo-send, and Postbox-import caveats are visible where relevant.
- [ ] Migration UI promises discovery and available paths, not a guaranteed importer.

## 5. Optional local AI

This phase is deferred. It requires an explicit product reassessment after personalization and inherited mail workflows are established.

### Work

- Implement the deterministic broker, sandboxed local process, separate runtime/model downloads, preview, and explicit apply flow.
- Add adversarial context, output, sandbox, and update tests.
- Keep ordinary mail workflows complete with AI disabled.

### Exit criteria

- [ ] No runtime or model is required for non-AI use.
- [ ] Context is limited to explicit allowed sources.
- [ ] Network, tools, credentials, attachments, search, write APIs, and autonomous actions are denied and tested.
- [ ] Only plaintext preview and explicit apply can reach the compose editor.
- [ ] Application, runtime, and model trust paths are signed, separate, compatible, and anti-rollback.
- [ ] The [security invariants](SECURITY.md#ai-and-subprocess-invariants) pass review.

## 6. Consented pilot

### Work

- Recruit participants matching the target-user definition.
- Connect real accounts and observe multi-account weekly use over a four-week window.
- Collect only approved content-free metrics and structured feedback.
- Measure support burden, AI edit acceptance where enabled, and willingness to pay.

### Exit criteria

- [ ] Participants give informed consent and can withdraw instrumentation.
- [ ] Pre-approved thresholds exist for every [validation gate](PRODUCT.md#provisional-validation-gates).
- [ ] No unresolved identity, data-integrity, security, or update-trust blocker remains.
- [ ] Evidence is interpretable without message, prompt, draft, or generated content.
- [ ] Support incidents and participant attrition have documented causes.

## 7. Decision gate

The pilot does not imply launch. Review account success, multi-account behavior, identity/data integrity, four-week retention, AI edit acceptance, support burden, and willingness to pay together.

### Exit criteria

- [ ] Continue, revise, narrow, or stop is recorded with evidence and limitations.
- [ ] Any next platform or feature phase receives its own design, security review, and validation plan.
- [ ] Provisional gates are not presented as scientific market facts.

## Deferred, not committed

| Area | Position |
|---|---|
| macOS and Linux | **Deferred**, not rejected; revisit after the Windows pilot decision. |
| Mobile and webmail/SaaS | **Deferred outside MVP**. |
| Teams and enterprise administration | **Deferred outside MVP**. |
| Full calendar/contact redesign | **Deferred**; inherited accessible surfaces remain in MVP. |
| Local or managed AI capability | **Deferred pending deliberate reassessment**; the documented security boundary remains mandatory if resumed. |
| Scheduled send and Gmail-style undo send | **Deferred custom work**; not native inherited features. |
| Guaranteed Postbox importer | **Unknown**; MVP promises migration discovery, not importer completion. |
| Personal memory, embeddings, knowledge graph, continual training | **Deferred outside MVP**. |

There are no delivery dates or platform commitments beyond this gated sequence.

## Related documents

[Overview](../README.md) | [Product](PRODUCT.md) | [Architecture](ARCHITECTURE.md) | [Security](SECURITY.md) | [Contributing](../CONTRIBUTING.md)
