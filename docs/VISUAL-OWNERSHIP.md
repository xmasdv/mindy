# Mindy Visual Ownership Architecture

Mindy owns presentation additively. Thunderbird continues to own mail, calendar, contact, protocol, security, storage, command, and platform behavior; Mindy consumes that behavior through narrow contracts and renders an independent Precision Workspace component system.

## Architecture Decision

```text
Thunderbird behavior and controllers
             |
             v
stable Mindy adapters, hooks, and normalized state
             |
             v
Mindy surface components and coordinators
             |
             v
shared Mindy primitives
             |
             v
semantic tokens -> theme values -> platform adaptations
```

Dependency direction is downward only. Tokens do not know primitives; primitives do not know product surfaces; components do not call Thunderbird globals directly; Thunderbird controllers do not import Mindy presentation.

## Package and File Boundaries

The paths below are the required target ownership model. Exact build manifests may vary with the pinned Thunderbird source, but equivalent responsibilities must not be merged back into upstream theme files.

| Layer | Target namespace | Owns | Must not own |
|---|---|---|---|
| Contracts | `comm/mindy/contracts/` | adapter interfaces, state schemas, capability flags, versioned hook contracts | visual values, controller implementations |
| Adapters | `comm/mindy/adapters/` | translation from Thunderbird events/models/commands into Mindy contracts | DOM presentation, copied protocol logic |
| Hooks | minimal reviewed edits under existing `comm/mail/**` hosts | stable mount points, semantic attributes, adapter registration | layout styling, color values, duplicated markup trees |
| Tokens | `comm/mindy/ui/tokens/` | primitives, semantic roles, theme maps, forced-colors mappings | selectors for specific Thunderbird documents |
| Primitives | `comm/mindy/ui/primitives/` | buttons, fields, lists, menus, tabs, banners, dialogs, progress, focus behavior | mail-specific controller calls |
| Components | `comm/mindy/ui/components/` | domain components such as folder rows, message rows, reader headers, recipient fields | direct access to unversioned Thunderbird globals |
| Surfaces | `comm/mindy/ui/surfaces/` | shell, onboarding, mail, reader, compose, search, calendar, contacts, settings, secondary-product composition | duplicated business behavior |
| Themes | `comm/mindy/ui/themes/` | light, dark, system, and high-contrast semantic assignments | component-local hard-coded palettes |
| Brand | `comm/mail/branding/mindy/` plus repository source assets | application identity and generated platform assets | general component styling |
| Verification | `comm/mindy/test/` and downstream repository contracts | adapter, component, screenshot, drift, and accessibility checks | production-only branches |

If upstream packaging makes a separate directory temporarily impractical, a transitional `mindy/` subtree under the nearest host package is permitted. Ownership and dependency rules remain unchanged, and the transition must include an extraction issue rather than becoming the permanent shape by accident.

## Layer Contracts

### Semantic Tokens

Tokens are the only source of visual values. They use purpose names, not surface or hue names.

- Primitive values define raw color, type, spacing, radius, elevation, motion, and z-order scales.
- Semantic roles define canvas, surface, text, border, action, selection, focus, status, and overlay meaning.
- Component aliases exist only when a semantic role is insufficient, such as `message-row-unread-text` or `recipient-chip-invalid-border`.
- Light, dark, system, and high-contrast themes assign values to the same semantic roles.
- Provider and extension content may consume a restricted theme bridge; it may not mutate core semantic roles.
- No surface stylesheet may redefine a semantic role locally.

### Primitives

Primitives own interaction presentation and accessibility invariants: visible focus, minimum discernible target, disabled semantics, pressed/selected distinction, forced-colors support, reduced motion, error association, keyboard behavior, and localization expansion. A primitive accepts semantic data and events; it never imports Thunderbird controllers.

### Components

Components combine primitives around one recognizable user job. They expose explicit states, avoid querying ambient DOM for business state, and receive commands through adapters. Components may be shared across surfaces only where semantics match; visual similarity alone is not enough.

### Surfaces

Surfaces coordinate components, responsive topology, routing, focus restoration, loading/error boundaries, and native/provider handoffs. Every surface maps to one or more IDs in [`VISUAL-AUDIT.md`](VISUAL-AUDIT.md). A surface can preserve an inherited content browser while replacing its surrounding chrome.

## Adapter and Hook Policy

An adapter is justified when Mindy needs data, commands, lifecycle events, or capability information from Thunderbird. It must:

1. Publish a small, versioned interface with documented null, error, and loading states.
2. Normalize unstable upstream object shapes before they enter components.
3. Preserve upstream security checks and command enablement.
4. Expose events instead of requiring components to poll or scrape the DOM.
5. Include contract fixtures that can run without real accounts or provider credentials.
6. Fail visibly when an expected upstream capability disappears.

A hook is the smallest upstream edit needed to mount a Mindy surface or register an adapter. Preferred hooks are a module import, a named mount element, a semantic data attribute, or an event bridge. Hooks must not include visual values or reproduce upstream markup.

Selectors against unowned anonymous structure, generated class names, positional child order, or broad document descendants are forbidden. If an upstream node must be addressed, give it one reviewed semantic hook and test that contract.

## Forbidden Direct Edits

- Do not place Mindy color, spacing, shape, type, or motion values in upstream Thunderbird theme files.
- Do not add another independent `mindy*.css` palette for each surface.
- Do not copy Thunderbird controller logic into Mindy components.
- Do not replace privileged, protocol, security, or storage behavior to simplify presentation.
- Do not target unstable child order, toolkit internals, or anonymous content with deep selectors.
- Do not hide inherited controls to create an appearance if the behavior remains reachable elsewhere without a designed route.
- Do not style provider-hosted pages as though Mindy owns their content.
- Do not imitate native pickers, UAC, certificate, or operating-system prompts with web chrome.
- Do not permit extensions or third-party themes to overwrite core focus, danger, warning, or selection semantics.

## Allowed Exceptions

An exception requires a written rationale, owner, upstream path, expected removal condition, and focused drift test. Permitted categories are:

- A minimal mount or semantic attribute where no supported extension point exists.
- A packaging manifest entry required to ship Mindy-owned modules or assets.
- A toolkit theme bridge for a privileged dialog that cannot host a separate component tree.
- A platform identity change required by executable, installer, notification, or registration APIs.
- A short-lived migration shim that keeps one work unit reversible while a surface moves behind an adapter.

Exceptions never authorize local token duplication or direct controller forks.

## Native and External Boundaries

| Boundary | Ownership rule | Required evidence |
|---|---|---|
| Windows file/folder/color/font/application pickers | Native visuals remain inherited. Mindy owns initiating copy, icon where supported, and return focus/state. | platform screenshots and cancellation/permission tests |
| UAC, default-app, protocol, notification, taskbar, and system settings | Windows owns chrome. Mindy owns identity, registrations, payload, and transition guidance. | clean-VM manual matrix |
| Print and print preview | Toolkit/native document is inherited. Mindy owns command entry, document correctness, and return path. | fixture output plus native screenshots |
| OAuth/provider sign-in | Provider owns authorization page. Mindy owns preflight, origin disclosure, blocked/denied/return states. | mocked callbacks plus provider-dependent manual validation |
| Privacy, help, release notes, and support web pages | Remote content is inherited and labeled as external. Mindy owns destination choice and offline/error wrapper. | link contracts, offline state, external-origin review |
| Add-on catalog and extension content | Provider/extension content remains inherited within a restricted theme bridge. Mindy owns host navigation, trust prompts, compatibility, and fallback. | mocked catalog and signed-extension checks |

## Update Safety Contract

Mozilla updates cannot honestly be guaranteed harmless. They can change markup, command APIs, toolkit rendering, platform behavior, localization, or content in ways that affect Mindy. The enforceable guarantee is narrower: an update must not alter Mindy personalization silently.

### Mandatory Drift Gates

Every upstream update candidate must pass all gates before it can become a Mindy baseline:

1. **Source pin gate:** record exact Gecko and comm revisions and verify their compatibility relationship.
2. **Patch applicability gate:** apply the minimal hook/identity series with strict checks; rejects or fuzz outside the approved threshold block the update.
3. **Contract gate:** compile or load every adapter and assert expected commands, events, mount points, state fields, and capability flags.
4. **Forbidden-coupling gate:** reject new direct imports from components to upstream globals, new deep selectors, and visual values outside the token package.
5. **Static identity gate:** scan strings, icons, manifests, registrations, remote defaults, and package contents for unintended upstream identity leakage.
6. **Screenshot gate:** compare the required state matrix against reviewed baselines using deterministic fixtures and recorded environment metadata.
7. **Accessibility gate:** verify focus, keyboard route, names/roles, high contrast, reduced motion, zoom, pseudo-localization, and RTL for affected surfaces.
8. **Behavior gate:** run focused upstream and Mindy browser tests for every changed adapter or surface.
9. **Native boundary gate:** rehearse affected Windows lifecycle and picker flows on a clean supported environment.
10. **Update rehearsal gate:** build and exercise the candidate from a clean checkout/profile before replacing any accepted baseline.

Any unresolved contract, screenshot, identity, accessibility, or patch delta is fail-closed. The update remains a candidate; maintainers must classify the delta as expected and approve a new baseline, adapt Mindy, or reject the update. Baselines are never regenerated automatically as a way to make a gate pass.

## Screenshot Baselines

Each baseline record includes surface ID, fixture, state, viewport/window size, OS scaling, app zoom, theme, contrast mode, locale/direction, source revisions, patch-series hash, build artifact hash, and verifier identity.

Required dimensions are selected by relevance rather than multiplied blindly:

| Dimension | Baseline values |
|---|---|
| Theme | light, dark, system; high contrast for critical controls and every major shell |
| Width | wide, medium, narrow for adaptive surfaces |
| Scale | default plus 200% app zoom; Windows 125% and 200% for representative native boundaries |
| Direction | English LTR, pseudo-expanded, one RTL locale |
| Data | empty, populated, loading, recoverable error, offline where meaningful |
| Focus | mouse-rest state and representative keyboard-focus state |
| Platform | Windows primary; additional supported platforms before declaring support for those platforms |

Pixel diffs are triage signals, not automatic quality judgments. Geometry, token, text overflow, focus, and identity regions receive stricter masks than provider content, timestamps, caret blink, or native nondeterminism. Dynamic masks must be narrow and reviewed.

## Verification Matrix

| Change class | Static | Browser/component | Runtime visual | Native/manual |
|---|---|---|---|---|
| Tokens/themes | schema, contrast, forbidden literals | primitive state gallery | theme and high-contrast matrix | OS system-theme transition |
| Primitive | dependency and accessibility contract | keyboard/state tests | focused component screenshots | assistive technology sample |
| Adapter/hook | API shape, mount point, forbidden coupling | upstream fixture and command tests | host surface smoke | provider/native only if crossed |
| Surface | ID mapping, route and dependency checks | state and interaction suite | required screenshot matrix | task-based review where automation cannot reach |
| Brand/platform | asset provenance, manifests, strings | package-level contracts | launch/About captures | clean-VM install/update/default-app checks |
| Upstream update | pins, patch applicability, drift scan | affected upstream plus Mindy suites | all changed baseline regions | all changed native/provider boundaries |

No implementation section can be self-approved by its author. Each section requires another implementation agent for execution or review and a fresh runtime visual verifier who did not write the section. Provider-dependent unknowns remain explicitly pending until observed in a controlled environment.

## Conflict Policy

- **No conflict:** proceed through all gates.
- **Mechanical hook conflict with unchanged behavior:** adapt the hook, update its contract fixture, and require independent review.
- **Adapter contract change:** block; version or rewrite the adapter before surfaces consume the update.
- **Visual delta with unchanged contract:** block; classify against `DESIGN.md` and baseline evidence before approval.
- **Behavior/security change:** upstream behavior wins unless Mindy has an explicitly reviewed product requirement and equivalent security evidence.
- **Unowned provider/native delta:** document and manually verify the boundary; do not claim control that Mindy does not possess.
- **Ambiguous delta:** block. Silence is never approval.

## Update Workflow and Rebase Procedure

1. Create an isolated update branch/worktree from the accepted Mindy baseline.
2. Record current pins, patch hash, artifact hash, baseline manifest, and known provider/native unknowns.
3. Update Gecko and comm pins together according to upstream compatibility metadata.
4. Run patch applicability without mutating the accepted baseline. Stop on rejected or unexpected fuzzy application.
5. Reapply only identity, packaging, and minimal hook patches; Mindy UI packages remain additive.
6. Run contract and forbidden-coupling gates before building.
7. Build a candidate artifact in an isolated output directory and record its hash.
8. Run focused behavior tests, then static identity/accessibility checks.
9. Execute deterministic runtime screenshot scenarios with a fresh disposable profile and fixture data.
10. Rehearse affected native and provider-dependent flows separately.
11. Have an independent verifier classify every delta and record evidence.
12. Approve new pins and baselines only after all blocking deltas are resolved. Preserve the previous accepted artifact and manifest until rollback is no longer needed.

## Rollback

Rollback operates at work-unit and upstream-baseline granularity:

- Every surface migration remains switchable to the last accepted inherited host until its adapter and screenshots pass.
- Token and primitive changes are versioned together; surfaces do not consume partially migrated role sets.
- An update candidate never overwrites the last accepted source pins, patch manifest, screenshots, or artifact.
- If a regression escapes a gate, restore the last accepted pins and Mindy package version, then retain the failed candidate evidence for diagnosis.
- Data formats and profiles remain under Thunderbird compatibility rules; visual rollback must not require user-data rollback.

## Migration from Patches 0002 and 0007-0013

The current patches are dismantled incrementally, not in a big-bang replacement.

1. **Freeze evidence:** retain patch files and current runtime captures as rejected-approach evidence. Do not treat their colors or selectors as authority.
2. **Extract roles:** map every repeated `--mindy-*` value to the new primitive and semantic token packages; add literal-value and duplicate-role gates.
3. **Introduce package roots:** ship tokens, primitives, adapter interfaces, and a surface registry without changing visible behavior.
4. **Wrap existing hooks:** convert `data-mindy-*` markers and stylesheet links into minimal mount/registration hooks where still needed.
5. **Migrate shell first:** replace `mindyWorkspace.css` behavior with owned SH components; keep a reversible inherited fallback.
6. **Migrate mail, reader, and compose separately:** move one surface ID work unit at a time from deep selectors to adapters and components. Remove selectors only after equivalent behavior and screenshots pass.
7. **Migrate first-run and account-free states:** replace patch-local palettes and inserted presentation markup with shared onboarding components and account adapters.
8. **Remove obsolete CSS:** delete each old `mindy*.css` package entry when no accepted surface references it; forbid reintroduction through static checks.
9. **Shrink the patch series:** leave only branding, platform identity, packaging, remote-default policy, and unavoidable stable hooks.
10. **Rehearse upstream update:** prove the isolated package survives a representative comm/Gecko update with fail-closed drift gates before considering the migration accepted.

Local AI is explicitly deferred and out of scope for this visual ownership migration.

## Ownership Review Checklist

- [ ] Every changed surface references IDs from [`VISUAL-AUDIT.md`](VISUAL-AUDIT.md).
- [ ] Visual values resolve through semantic tokens.
- [ ] Components communicate with Thunderbird only through adapters.
- [ ] Upstream edits are minimal hooks with drift tests and removal conditions.
- [ ] Native and provider content is labeled inherited rather than omitted.
- [ ] Deterministic state fixtures cover success, loading, empty, offline, and recoverable errors where relevant.
- [ ] Accessibility, localization, zoom, and adaptive checks are present.
- [ ] Screenshot provenance includes source and artifact identity.
- [ ] Another agent reviewed implementation and a fresh runtime verifier classified visual evidence.
- [ ] Rollback restores the last accepted visual package without changing user data.
