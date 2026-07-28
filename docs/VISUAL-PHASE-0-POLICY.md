# Phase 0 Visual Contract Policy

These rules are the entry gate for later visual work. They establish vocabulary and evidence ownership only; they do not create a package, runtime behavior, product surface, or visual baseline.

## Forbidden coupling

Reject later changes that:

- target anonymous structure, generated classes, positional child order, toolkit internals, or broad descendants without a registered semantic hook;
- let components call or import unversioned Thunderbird globals instead of a declared adapter contract;
- place Mindy layout or styling ownership directly in upstream theme or controller files;
- introduce visual literals outside a future centrally reviewed semantic-token authority;
- style provider-hosted or native content as though Mindy owns it; or
- register a hook, selector exception, or ownership boundary without its surface IDs, rationale, owner, removal condition, and drift check.

Explicit `inherited-native` and `inherited-external` registry boundaries are allowed. Mindy may own the invocation, disclosure, identity, restricted bridge, return focus, and failure wrapper while the external party retains its visuals. This policy names contract concepts only and does not authorize Phase 1 package paths.

## Fixture data

- Fixtures must be deterministic, synthetic, offline-safe by default, and reproducible from a documented seed or checked-in non-sensitive input.
- Real credentials, tokens, mailbox content, addresses, contacts, calendars, profile data, and other personal data are prohibited.
- Provider behavior must use mocks or local deterministic substitutes until separately reviewed manual evidence is available.
- Logs must exclude secrets, network payloads, personal paths, and unrelated profile or crash data.
- Time, locale, random IDs, and ordering must be fixed when they affect evidence.

## Baseline approval

A candidate record requires complete provenance under `screenshot-manifest.schema.json`. The implementer cannot approve their own candidate: a different reviewer must classify the delta and record their identity. Missing provenance, unresolved deltas, or absent independent review fail closed. Historical captures in `rejected-evidence.json` remain rejected comparison evidence and cannot be promoted in place; a fresh candidate capture and separate approval are required.

## Provider, native, and accessibility unknowns

| Boundary | Known gap | Status / evidence needed |
|---|---|---|
| OAuth and provider authorization | Branding, denial, popup, timeout, and return-focus variants are provider-dependent. | Pending controlled provider matrix; no acceptance inferred. |
| Privacy, help, release notes, support, and add-on content | Remote content, origin treatment, offline behavior, and provider drift are not controlled. | Pending link/offline checks and external-origin review. |
| Windows lifecycle and native UI | Installer, update, crash, UAC, defaults, notifications, print, and picker variants are not fully observed. | Pending clean-VM native matrix. |
| Assistive technology | Screen-reader routes, forced colors, reduced motion, IME, and platform scaling lack systematic evidence. | Pending independent accessibility review. |
| Historical runtime captures | Build artifact and patch-series identity are incomplete; privacy and stock composition residue are visible. | Rejected historical comparison only. |

Unknowns remain pending until controlled evidence exists. A native or provider boundary may be truthfully inherited without being accepted as Mindy-owned.

## Rollback

Revert only `contracts/visual/`, this policy, `tools/validate-visual-contracts.py`, and `evidence/visual/rejected-historical/`. No runtime, build, package, profile, user-data, or product rollback is involved.
