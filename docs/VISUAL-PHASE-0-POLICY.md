# Phase 0 Visual Contract Policy

These rules establish evidence ownership and contract vocabulary only. They create no package, runtime behavior, product surface, or baseline.

## Forbidden coupling

Reject anonymous/generated/positional deep selectors, component access to unversioned Thunderbird globals, direct upstream visual ownership, visual literals outside future semantic tokens, counterfeit provider/native styling, and unregistered exceptions. Every exception needs surface IDs, rationale, owner, removal condition, and a drift check.

`inherited-native` and `inherited-external` are explicit boundaries. Mindy may own invocation, disclosure, identity, a restricted bridge, return focus, and failure wrappers while the external party retains its visuals. This vocabulary does not authorize Phase 1 package paths.

## Fixture data

- Fixtures are deterministic, synthetic, offline-safe, seeded, and reproducible.
- Real credentials, tokens, mailbox content, addresses, contacts, calendars, profiles, and personal data are prohibited.
- Provider behavior uses mocks or local substitutes until separately reviewed manual evidence exists.
- Logs exclude secrets, network payloads, personal paths, unrelated profiles, and crash data.
- Time, locale, IDs, and ordering are fixed when they affect evidence.

## Baseline approval

The standard-library validator enforces the exact supported contract subset; it is not a general JSON Schema engine. Candidates require complete hashes and provenance. Accepted baselines require a non-empty reviewer different from the capture actor. Rejected paths or hashes cannot be reused or promoted; a fresh capture is mandatory.

## Provider, native, and accessibility unknowns

| Boundary | Gap | Required evidence |
|---|---|---|
| OAuth/providers | Branding, denial, timeout, return focus | Controlled provider matrix; pending |
| Remote support/add-ons | Origin, offline behavior, drift | Link/offline/external-origin review; pending |
| Windows native UI | Install, update, crash, UAC, defaults, print, pickers | Clean-VM matrix; pending |
| Assistive technology | Screen readers, forced colors, motion, IME, scaling | Independent accessibility review; pending |
| Historical captures | Artifact and patch identity incomplete; three captures redacted/cropped | Rejected comparison only |

Unknowns remain pending until controlled evidence exists. Inheritance does not imply Mindy ownership or acceptance.

## Rollback

Revert only `contracts/visual/`, this policy, `tools/validate-visual-contracts.py`, its focused tests, and `evidence/visual/rejected-historical/`. No runtime, build, package, profile, user-data, or product rollback is involved.
