# Mindy Visual Reconstruction Plan

This plan converts the 80 audited surface families into dependency-ordered, reviewable implementation work. Acceptance is evidence-based: a work unit advances only when its contracts, behavior, accessibility, runtime visuals, and relevant native/provider boundaries have been independently verified.

## Delivery Rules

- Each implementation work unit is assigned to another engineering agent with the stated entry criteria and rollback boundary.
- A fresh runtime visual verifier, who did not author the unit, captures and classifies its runtime evidence.
- The documentation writer cannot approve implementation or visual baselines.
- Work units should remain reviewable slices. If a unit exceeds the repository's review budget, split by component or state without splitting tests and documentation from the behavior they verify.
- No acceptance statement uses elapsed time, release targets, or visual similarity alone.
- Unknown provider, account, network, hardware, and operating-system behavior remains explicitly pending until observed in a controlled environment.
- Local AI is explicitly deferred and out of scope for every phase.

## Evidence Model

Every unit produces an evidence manifest containing source revisions, patch-series hash, build artifact hash, fixture identity, operating system, scale, app zoom, theme, locale/direction, window dimensions, test commands/results, screenshot names, known unknowns, implementer, reviewer, and independent runtime verifier.

Verification labels used below:

| Label | Required evidence |
|---|---|
| Static | dependency rules, hook/adapter schemas, token/literal checks, localization/identity scans, link and ID contracts |
| Browser | deterministic controller/adapter/component interaction tests using synthetic fixtures |
| Runtime | fresh-profile screenshots and task-path observations from the candidate executable |
| Native/manual | operating-system, assistive-technology, provider, print, picker, installer, or credential-gated evidence not honestly covered by browser automation |

## Phase 0: Authority and Contracts

**Entry criteria:** the approved mockup, production mark, this audit, ownership architecture, pinned source revisions, rejected patch evidence, and retained runtime evidence are readable and hashable.

**Surface IDs:** none; this phase establishes the contract consumed by all inventory work.

**Deliverables:** an authority manifest; surface registry schema; adapter contract template; screenshot manifest schema; forbidden-coupling rules; fixture-data policy; baseline approval policy; provider/native unknown log.

**Verification:** Static validation checks authoritative paths, hashes, 80-ID registry membership, source pins, and prohibited guarantee language. Browser and runtime work are not applicable. Native/manual review confirms that external and native ownership labels are truthful.

**Runtime screenshot matrix:** no new product screenshots; index the retained first-run, account-free, privacy, About, narrow/focus, and restored-wide evidence as historical comparison only.

**Exit criteria:** reviewers can identify visual authority, implementation evidence, behavior authority, and rollback evidence without inference. A second agent approves the contract shape; no visual baseline is approved here.

**Upstream risk:** evidence can be misclassified as authority. **Rollback boundary:** documentation and manifests only.

## Phase 1: Package and Isolation

**Entry criteria:** Phase 0 contracts are accepted and the pinned Thunderbird tree builds before package changes.

**Surface IDs:** none; this phase creates the additive path used by later surfaces.

**Deliverables:** Mindy contract, adapter, UI, theme, brand, and test package roots; dependency enforcement; surface registry; minimal hook policy; transitional feature switch; packaging tests.

**Verification:** Static checks reject reverse dependencies, direct component-to-Thunderbird globals, deep selectors, visual literals outside tokens, and unregistered hooks. Browser smoke proves the inherited shell still starts with the feature switch off and the empty Mindy registry loads with it on. Runtime captures both paths without asserting visual progress. Native/manual is limited to package identity and startup.

**Runtime screenshot matrix:** inherited account-free shell, wide and narrow, feature switch off/on, light theme.

**Exit criteria:** additive packages load without changing behavior or accepted visuals, and removing the package registration returns to the prior state. Another agent reviews package ownership; a fresh verifier confirms no unintended delta.

**Upstream risk:** build-manifest and host registration churn. **Rollback boundary:** remove package and hook registrations; no profile/data migration.

## Phase 2: Design System

**Entry criteria:** additive package roots and dependency gates pass.

**Surface IDs:** none; semantic roles and primitives are cross-surface dependencies.

**Deliverables:** primitive and semantic token sets; light/dark/system/high-contrast mappings; typography evaluation harness; spacing/density, shape, elevation, icon, motion, focus, and state contracts; core buttons, fields, lists, menus, tabs, banners, dialogs, progress, and empty-state primitives.

**Verification:** Static contrast, token schema, forbidden literal, logical-property, reduced-motion, and primitive accessibility checks. Browser state gallery covers default, hover, active, selected, focus, disabled, loading, success, warning, error, and offline semantics. Runtime captures the gallery in theme, contrast, locale, direction, and zoom variants. Native/manual includes Windows font rendering and screen-reader/forced-colors review.

**Runtime screenshot matrix:** light/dark/system; normal/high contrast; LTR/pseudo-expanded/RTL; default/200% zoom; Windows 100%/200% scale for representative primitives.

**Exit criteria:** all later surfaces can be composed without local visual values, focus remains visible over every state, and typography remains provisional until the documented rendering/licensing evaluation is approved by another agent and fresh verifier.

**Upstream risk:** toolkit defaults can leak through unthemed controls. **Rollback boundary:** version tokens and primitives together; consumers remain on the prior accepted version.

## Phase 3: Application Shell

**Entry criteria:** Phase 2 primitives pass and stable shell command/tab/space adapters exist.

**Surface IDs:** SH-01, SH-02, SH-03, SH-04, SH-05, SH-06, SH-07.

**Deliverables:** owned frame, spaces rail, unified toolbar/search host, tabs, application menu, customization mode, and global feedback components; removal of equivalent provisional workspace selectors.

**Verification:** Static hook, command map, tab/space registry, identity, and token checks. Browser tests cover switching, overflow, customization/reset, keyboard menus, banners, persisted layout, and focus restoration. Runtime exercises launch, all spaces, tabs, menus, customization, offline banner, active/inactive window. Native/manual checks title bar, Windows scaling, keyboard accelerators, and screen reader.

**Runtime screenshot matrix:** wide/medium/narrow; light/dark/high contrast; default/200% zoom; no badge/badge/error; mouse-rest/keyboard-focus.

**Exit criteria:** the shell is recognizably Precision Workspace without hiding inherited behavior; every command path remains reachable; independent review finds no stock Thunderbird chrome in owned regions.

**Upstream risk:** high churn in messenger, unified toolbar, tabs, and customization hosts. **Rollback boundary:** shell feature switch restores the inherited host while retaining additive packages.

## Phase 4: Onboarding and Accounts

**Entry criteria:** shell routing, shared forms, dialogs, banners, and provider-boundary patterns pass.

**Surface IDs:** AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08.

**Deliverables:** first-run step shell, automatic discovery status, manual configuration form, OAuth preflight/return wrapper, result/recovery states, account-free hub, account/identity settings, migration/import/export wizard.

**Verification:** Static form/error associations, secret-handling boundaries, provider labels, adapter states, and localization checks. Browser fixtures cover found/not found, timeout, offline, invalid settings, duplicate account, success, partial failure, settings save/delete, and import cancellation. Runtime uses disposable profiles and synthetic providers without real credentials. Native/manual covers provider authorization, file pickers, destructive prompts, and screen-reader flow.

**Runtime screenshot matrix:** first-run pristine/invalid/searching/found/error; manual form; provider preflight/denied/return; account-free hub; one/multiple-account settings; migration progress/partial failure; wide/narrow, light/dark, LTR/RTL.

**Exit criteria:** a user can understand setup, trust boundaries, recovery, and account-free alternatives; provider-dependent results are recorded rather than inferred; old first-run/account-central palette fragments are removable.

**Upstream risk:** account hub and OAuth flows evolve frequently and depend on remote providers. **Rollback boundary:** each flow step can return to inherited rendering behind the same adapter without changing account data.

## Phase 5: Mail Workspace

**Entry criteria:** shell, synthetic mailbox fixtures, folder/message adapters, and responsive topology controller pass.

**Surface IDs:** MW-01, MW-02, MW-03, MW-04, MW-05, MW-06, MW-07, MW-08, MW-09, MW-10.

**Deliverables:** owned folder pane, unified modes, thread/message list, columns/sorting/grouping, density/layout modes, quick filter, pane coordinator, folder workflows, workspace states, and drag/context feedback.

**Verification:** Static state schema, command enablement, semantic row/cell, token, and no-deep-selector checks. Browser fixtures cover accounts/folders, read/unread/threaded mail, sort/group, card/table, splitters, filters, history/focus, properties, empty/offline/auth error, drag/drop, and context commands. Runtime uses deterministic populated and empty profiles. Native/manual covers keyboard tree/list navigation, screen reader, high contrast, display scaling, and any server-dependent properties.

**Runtime screenshot matrix:** empty/populated/loading/offline/auth error; table/card; unified/account tree; wide/medium/narrow; light/dark/high contrast; default/200% zoom; LTR/RTL; representative selected/focused/drag states.

**Exit criteria:** account and sender context remain visible, scan density is deliberate, pane adaptation preserves selection/focus, and inherited mail behavior passes focused upstream tests. A fresh verifier compares against the approved mockup by hierarchy and role, not pixel imitation.

**Upstream risk:** highest churn and largest behavioral blast radius. **Rollback boundary:** folder, list, filter, and coordinator migrations are separately switchable; no message-store changes.

## Phase 6: Reader

**Entry criteria:** mail coordinator, sanitized fixture corpus, reader/security adapters, and native-boundary wrappers pass.

**Surface IDs:** RD-01, RD-02, RD-03, RD-04, RD-05, RD-06.

**Deliverables:** owned reader frame/header/actions/attachments/security notices; content viewport contract; tab/window/source/print transitions; removal of provisional reader CSS.

**Verification:** Static content-boundary, action, attachment, security-status, and accessibility contracts. Browser fixtures cover HTML/plain text, long headers, blocked media, junk/phishing, signed/encrypted status, attachments, missing message, source, and alternate routes. Runtime captures deterministic messages without external media. Native/manual covers save/open/print, dangerous attachment prompts, screen reader reading order, and zoom/bidi.

**Runtime screenshot matrix:** no selection/loading/plain/HTML/blocked media/security warning/attachments; narrow/wide; light/dark/high contrast; default/200% zoom; LTR/RTL; keyboard focus on actions.

**Exit criteria:** content safety remains inherited, Mindy owns surrounding hierarchy, security notices remain unmistakable without color alone, and all alternate reading routes restore focus.

**Upstream risk:** privileged content browser and security behavior must not be forked. **Rollback boundary:** reader chrome can revert independently while content/controller remain unchanged.

## Phase 7: Compose

**Entry criteria:** synthetic identities, compose/editor/attachment adapters, shared forms/toolbars, and transport fixtures pass.

**Surface IDs:** CP-01, CP-02, CP-03, CP-04, CP-05, CP-06, CP-07.

**Deliverables:** owned compose frame, recipient field, metadata header, editor chrome, attachment queue, send/save status, and editor dialogs; removal of provisional compose CSS.

**Verification:** Static identity/recipient/error semantics, editor boundary, command enablement, autosave, and secret checks. Browser fixtures cover new/reply/forward, recipient autocomplete and invalid addresses, multiple identities, rich/plain text, bidi, attachments/cloud errors, send/save/offline failures, spellcheck, find, and close prompts. Runtime uses synthetic local transport and disposable drafts. Native/manual covers file pickers, provider cloud flows, screen reader, IME, clipboard, and OS scaling.

**Runtime screenshot matrix:** new/reply/forward; pristine/modified/sending/queued/saved/error; rich/plain; attachment upload/failure; missing subject/invalid recipient; wide/narrow; light/dark/high contrast; LTR/RTL; 200% zoom.

**Exit criteria:** compose is reachable with deterministic test identities, draft safety is proven, keyboard/IME editing remains intact, and provider-dependent attachment behavior is explicitly evidenced or pending.

**Upstream risk:** editor and compose command code are high-churn and data-loss sensitive. **Rollback boundary:** visual shell and each header/editor/attachment component can revert without altering draft format or transport behavior.

## Phase 8: Search and Rules

**Entry criteria:** message fixtures are indexed; query, result, filter, and rule adapters pass.

**Surface IDs:** SR-01, SR-02, SR-03, SR-04.

**Deliverables:** global search combobox, result/facet view, advanced/saved query builder, filter/rule list and editor.

**Verification:** Static query schema, active-descendant, row-group, reorder, and error contracts. Browser fixtures cover suggestions, no result, facets, malformed criteria, saved search, rule ordering, run failure, and deletion. Runtime uses a deterministic indexed mailbox. Native/manual covers screen-reader result navigation and provider/server-dependent rule execution.

**Runtime screenshot matrix:** empty query/suggestions/loading/results/no results/error; facet active; advanced query; rule list/editor/failure; wide/narrow; light/dark; keyboard focus.

**Exit criteria:** search and automation share primitives without conflating their semantics, result context is preserved, and rule failures provide recovery rather than silent loss.

**Upstream risk:** index and rule model changes can invalidate fixtures. **Rollback boundary:** entry, results, advanced search, and rules are independent adapter/component units.

## Phase 9: Calendar and Tasks

**Entry criteria:** shell spaces, calendar/task fixtures, item/provider adapters, and date/time localization tests pass.

**Surface IDs:** CA-01, CA-02, CA-03, CA-04, CA-05, CA-06, CA-07.

**Deliverables:** calendar views, agenda, event/task editor, recurrence/timezone/reminder dialogs, invitation scheduling, task view, and provider setup/status.

**Verification:** Static grid/list semantics, date/time roles, category alternatives, provider boundary, and logical-property checks. Browser fixtures cover all calendar views, overlapping events, drag, empty agenda, read-only/edit failure, recurrence/DST, invitations/conflicts, tasks, discovery/sync errors. Runtime uses local fixture calendars. Native/manual covers provider OAuth, screen-reader grid navigation, locale calendars, DST, high contrast, and print where relevant.

**Runtime screenshot matrix:** day/week/multiweek/month; today pane empty/populated; editor new/edit/error; recurrence/timezone; invitation states; tasks due/overdue/completed; provider setup/offline/error; LTR/RTL and wide/narrow.

**Exit criteria:** event density and selection remain legible in all views, date meaning never relies on color, and provider-dependent validation is recorded separately from local-calendar acceptance.

**Upstream risk:** calendar views and provider APIs have broad behavioral complexity. **Rollback boundary:** view chrome, editor, invitations, tasks, and provider setup migrate separately over unchanged calendar storage.

## Phase 10: Contacts

**Entry criteria:** address-book fixtures, vCard forms, source/list/detail adapters, and native import boundary pass.

**Surface IDs:** CT-01, CT-02, CT-03, CT-04, CT-05.

**Deliverables:** address-book shell, contact list/search, detail view, vCard editor, list/import/export/duplicate/remote workflows.

**Verification:** Static vCard field mapping, form association, list/detail semantics, and provider labels. Browser fixtures cover local/remote/read-only books, card/table, no result, multiple selection, sparse/complex contacts, invalid edits, mailing lists, duplicate conflicts, and remote errors. Runtime uses synthetic books. Native/manual covers import/export picker, CardDAV/LDAP providers, keyboard/screen reader, and RTL addresses.

**Runtime screenshot matrix:** no books/empty/populated/search-no-result; card/table; single/multiple details; new/edit/invalid; list/duplicate/import progress/error; wide/narrow; light/dark; LTR/RTL.

**Exit criteria:** source, list, detail, and edit responsibilities remain clear at all widths; vCard data round-trips; remote validation is accepted only with evidence.

**Upstream risk:** about:addressbook markup and vCard editor modules are high-churn. **Rollback boundary:** shell/list/detail/editor/workflows can revert independently over unchanged address-book data.

## Phase 11: Settings and Security

**Entry criteria:** settings registry, preference adapters, security dialog bridge, theme compatibility rules, and reusable setting rows pass.

**Surface IDs:** ST-01, ST-02, ST-03, ST-04, ST-05, ST-06, ST-07, ST-08, ST-09.

**Deliverables:** settings shell/find, appearance/language, general/compose, privacy/security, connection/offline/sync, notification/file preferences, add-on host, trust prompts, and extension/theme compatibility boundaries.

**Verification:** Static preference typing, sensitive-value handling, permission copy, extension override zones, localization, and token checks. Browser fixtures cover routing/search, theme transitions, dependent settings, password/cert/permission prompts, proxy/offline/sync errors, notifications/downloads, catalog/install/update/remove, and incompatible themes. Runtime uses disposable preferences and mocked catalogs. Native/manual covers authentication gates, certificate UI, language restart, notification/file permissions, signed add-ons, and Windows theme transitions.

**Runtime screenshot matrix:** each settings category; search result/no result; light/dark/system/high contrast; security prompt/error; offline/sync conflict; add-on discovery/detail/install permission/incompatible; pseudo-expanded/RTL; 200% zoom.

**Exit criteria:** sensitive and destructive settings are unmistakable, extension content cannot erase core semantics, and toolkit/provider-owned regions are explicitly labeled and wrapped.

**Upstream risk:** toolkit settings/add-ons/security UI can change outside comm. **Rollback boundary:** categories and provider hosts migrate independently; stored preferences remain upstream-compatible.

## Phase 12: Secondary Inherited Products

**Entry criteria:** shared shell/list/reader/compose primitives and protocol-specific adapters have deterministic local fixtures.

**Surface IDs:** SF-01, SF-02, SF-03.

**Deliverables:** chat shell/transcript chrome, feed subscription/status UI, and newsgroup subscription/thread/posting UI, with honest provider boundaries.

**Verification:** Static protocol labels, transcript/list semantics, sanitization boundary, and reuse contracts. Browser/local-server fixtures cover connecting, failed send, unread, trust state, valid/invalid/offline feeds, NNTP search/subscription/offline/post failure. Runtime uses local deterministic providers where feasible. Native/manual covers real-provider behavior, trust verification, notifications, and accessibility.

**Runtime screenshot matrix:** chat disconnected/connected/unread/send error; feed discovery/subscribed/article/offline/error; newsgroup account/search/subscribed/thread/post error; light/dark; wide/narrow; keyboard focus.

**Exit criteria:** secondary products are visibly part of Mindy without pretending protocol/provider certainty, and shared components retain product-specific semantics.

**Upstream risk:** protocols and remote services can disappear or change independently. **Rollback boundary:** each product is isolated and can retain inherited rendering without affecting Mail.

## Phase 13: Native and Lifecycle

**Entry criteria:** brand assets, platform adapter contracts, clean Windows validation environment, and retained accepted artifact are available.

**Surface IDs:** SY-01, SY-02, SY-03, SY-04, SY-05, SY-06, SY-07, SY-08, SY-09, SY-10, SY-11.

**Deliverables:** About/update/startup/crash identity, installer and OS integration, notification payloads, print transitions, native picker return contracts, help/privacy/support wrappers, and privileged prompt theme bridge.

**Verification:** Static package strings/assets/manifests/registrations/URLs, update states, prompt contracts, and identity leakage scans. Browser/toolkit fixtures cover About, mocked updates, help/offline, print documents, and prompts. Runtime captures launch/About/help/print and controlled recovery states. Native/manual uses clean VMs for install/upgrade/repair/uninstall/UAC/default-client/protocol/toast/picker/crash/update and checks focus, identity, accessibility, and rollback.

**Runtime screenshot matrix:** About update states; cold/warm/restore/locked-profile launch; crash recovery; installer lifecycle; default-client allowed/denied; toast privacy variants; print preview/error; each picker class; help external/offline; destructive/auth/certificate prompts; Windows normal/high contrast and 100%/200% scale.

**Exit criteria:** every boundary is either Mindy-owned, toolkit-wrapped, provider-labeled, or explicitly native; package identity is namespaced; clean-VM rollback succeeds; unknown OS/provider variants remain documented.

**Upstream risk:** platform and toolkit changes cannot be insulated entirely. **Rollback boundary:** restore the prior signed/accepted artifact, registrations, and source manifest; never roll back user profile data as part of a visual rollback.

## Phase 14: Compatibility Validation

**Entry criteria:** all preceding surface units have accepted static/browser evidence and a candidate runtime artifact.

**Surface IDs:** AX-01, AX-02, AX-03.

**Deliverables:** cross-surface keyboard/screen-reader/focus/reduced-motion/high-contrast report; localization/pseudo-locale/RTL report; zoom/density/reflow/display-scaling report; final surface-to-evidence manifest; unresolved provider/native unknown register.

**Verification:** Static scans cover names/roles contracts, logical properties, Fluent usage, motion gates, and adaptive topology. Browser runs exercise keyboard routes, focus restoration, pseudo-localization, RTL, zoom, and geometry assertions across every major shell. Runtime uses a fresh disposable profile and deterministic populated fixtures. Native/manual uses screen readers, forced colors, IME, Windows scale changes, multi-monitor movement, and provider/native scenarios marked by earlier phases.

**Runtime screenshot matrix:** representative states from every major shell in light/dark/high contrast; LTR/pseudo-expanded/RTL; wide/medium/narrow; default/200% app zoom; 100%/125%/200% OS scale; reduced motion; mouse-rest/keyboard-focus.

**Exit criteria:** every audit ID points to accepted evidence and an independent verifier; blocking accessibility, localization, adaptive, identity, or drift deltas are resolved; remaining provider/native unknowns are explicit and do not masquerade as acceptance.

**Upstream risk:** cross-cutting regressions can emerge only in integrated runtime. **Rollback boundary:** reject the candidate artifact and restore the last accepted source, package, baseline, and artifact manifests.

## Upstream Update Acceptance

After Phase 14, every Mozilla update repeats the source-pin, patch-applicability, contract, forbidden-coupling, screenshot, accessibility, behavior, native-boundary, and clean-update-rehearsal gates in [`VISUAL-OWNERSHIP.md`](VISUAL-OWNERSHIP.md). The practical commitment is detection and fail-closed review before personalization changes reach an accepted build, not a claim that upstream changes are harmless.

The inventory and surface-level evidence requirements are defined in [`VISUAL-AUDIT.md`](VISUAL-AUDIT.md). Visual roles and component principles are defined in [`../DESIGN.md`](../DESIGN.md).
