---
name: Mindy
description: Precision Workspace visual system for an independent Thunderbird downstream
colors:
  brand-navy-950: "#051B40"
  brand-navy-900: "#061830"
  brand-teal-600: "#0A7F7D"
  brand-teal-500: "#0EA5A4"
  energy-blue-600: "#2563EB"
  warm-canvas: "#FFFDF9"
  warm-surface: "#F7F4ED"
  warm-line: "#D8D2C7"
  ink-900: "#172033"
  ink-600: "#526071"
rounded:
  control-sm: "4px"
  control-md: "6px"
  overlay-lg: "10px"
  pill: "999px"
spacing:
  1: "4px"
  2: "8px"
  3: "12px"
  4: "16px"
  5: "20px"
  6: "24px"
  8: "32px"
components:
  button-primary:
    backgroundColor: "{colors.brand-teal-600}"
    textColor: "{colors.warm-canvas}"
    rounded: "{rounded.control-md}"
    padding: "8px 14px"
  field-default:
    backgroundColor: "{colors.warm-canvas}"
    textColor: "{colors.ink-900}"
    rounded: "{rounded.control-sm}"
    padding: "6px 10px"
  navigation-selected:
    backgroundColor: "{colors.warm-surface}"
    textColor: "{colors.ink-900}"
    rounded: "{rounded.control-sm}"
    padding: "6px 8px"
---

# Mindy Design System

## Overview

**Creative North Star: "Precision Workspace"**

Mindy is an independent Thunderbird downstream, not a theme. It preserves Thunderbird's mature behavior while replacing inherited visual composition with a focused, capable, distinctly Mindy workspace. Density belongs where users scan; space belongs where they read, compose, and make consequential decisions.

The approved direction combines a deep structural shell, warm content surfaces, restrained teal interaction, and rare electric-blue energy. The interface is calm at rest, keyboard-first, direct about trust boundaries, and expressive only when an event deserves attention. Familiar three-pane concepts may remain, but their hierarchy, components, spacing, states, and adaptive behavior must be Mindy-owned.

The provisional identity remains **logo option 01**, represented for production use by [`assets/brand-production/mindy-mark.svg`](assets/brand-production/mindy-mark.svg). The mark may be refined or replaced without invalidating the wider system. Local AI is explicitly deferred and out of scope.

### Authority

| Authority | Role |
|---|---|
| [`assets/design-concepts/mindy-inbox-mockup-v2-navy-teal.png`](assets/design-concepts/mindy-inbox-mockup-v2-navy-teal.png) | Approved visual direction for hierarchy, density, shell character, and palette balance |
| [`assets/brand-production/mindy-mark.svg`](assets/brand-production/mindy-mark.svg) | Production rendition of provisional logo option 01 |
| This document | Normative visual roles and component principles |
| [`docs/VISUAL-AUDIT.md`](docs/VISUAL-AUDIT.md) | Surface inventory, evidence, ownership state, and risk |
| [`docs/VISUAL-OWNERSHIP.md`](docs/VISUAL-OWNERSHIP.md) | Additive package architecture, update safety, and migration rules |
| [`docs/VISUAL-RECONSTRUCTION-PLAN.md`](docs/VISUAL-RECONSTRUCTION-PLAN.md) | Dependency order, implementation work units, and acceptance evidence |

Patches `0002` and `0007`-`0013`, applied Gecko source, and runtime captures are evidence of the rejected partial approach and current behavior. They do not override this document or the approved visual assets.

**Key characteristics:**

- Structural rather than decorative navy.
- Compact, legible scanning surfaces and spacious reading surfaces.
- Restrained interaction color with state meaning reinforced by text, icon, shape, or position.
- Crisp pane relationships instead of floating-card sprawl.
- Owned component composition over inherited recoloring.
- Honest native and provider boundaries.

## Colors

The frontmatter defines the currently approved portable primitives. Semantic roles are the implementation API; components must not consume raw palette values directly.

### Primitive Roles

| Group | Primitive | Purpose |
|---|---|---|
| Brand | `brand-navy-950` | deepest persistent structure and high-confidence inverse backgrounds |
| Brand | `brand-navy-900` | global rail and adjacent structural differentiation |
| Brand | `brand-teal-600` | primary action, active navigation edge, and meaningful progress |
| Brand | `brand-teal-500` | hover or emphasis where contrast remains sufficient |
| Accent | `energy-blue-600` | rare focus-energy or brand-event accent, never broad surface fill |
| Neutral | `warm-canvas` | primary light reading and composition canvas |
| Neutral | `warm-surface` | secondary pane, selected neutral surface, and grouped control background |
| Neutral | `warm-line` | quiet separators and field boundaries |
| Ink | `ink-900` | primary light-theme text and icons |
| Ink | `ink-600` | secondary text that still meets required contrast in context |

Additional dark and status primitives must be derived and measured during implementation. They become normative only after contrast, Windows rendering, high-contrast behavior, and screenshot review pass.

### Semantic Roles

| Role family | Required roles | Usage rule |
|---|---|---|
| Canvas | `canvas-app`, `canvas-content`, `canvas-inverse` | application background, reading canvas, inverse structural region |
| Surface | `surface-base`, `surface-subtle`, `surface-raised`, `surface-sunken`, `surface-overlay` | adjacent hierarchy and true elevation; never arbitrary cards |
| Text | `text-primary`, `text-secondary`, `text-disabled`, `text-inverse`, `text-link` | hierarchy must remain legible without relying on hue alone |
| Border | `border-subtle`, `border-default`, `border-strong`, `border-focus` | pane separation, control definition, high-emphasis focus |
| Action | `action-primary`, `action-primary-hover`, `action-secondary`, `action-quiet` | one primary action per decision region when practical |
| Selection | `selection-rest`, `selection-hover`, `selection-active`, `selection-focus` | hover, selection, and keyboard focus remain distinct |
| Status | `status-info`, `status-success`, `status-warning`, `status-danger`, `status-offline` with foreground/background/border variants | pair color with icon and text; danger never aliases brand teal |
| Data | `data-unread`, `data-flagged`, `data-junk`, `data-encrypted`, `data-signed` | preserve semantic distinction in all themes and forced colors |
| Overlay | `overlay-scrim`, `overlay-shadow`, `overlay-highlight` | transient layering only |

### Theme Mapping

- **Light:** warm canvases and surfaces carry reading regions; navy remains structural; teal marks action and selection edges.
- **Dark:** use near-navy neutral canvases with independently measured text, border, selection, and status roles. Do not invert light values mechanically.
- **System:** resolve to the current operating-system preference and update without leaving mixed-theme regions.
- **High contrast:** allow system colors and forced-color adjustments to replace decorative assignments. Preserve borders, focus, selection, status icons, and text meaning.
- **Provider/extension content:** receive only a restricted theme bridge. They cannot redefine core focus, danger, warning, or selection roles.

**The Rarity Rule.** Electric blue signals focus or energy; scarcity prevents a generic corporate-blue interface.

**The Semantic Boundary Rule.** A surface may request a role, never a raw hue. If a needed role does not exist, define and validate the role centrally rather than creating a local value.

## Typography

Mindy requires a contemporary, highly legible UI sans with platform-appropriate fallbacks. The final family is intentionally unresolved until evidence supports it.

### Decision Process

1. Confirm desktop and redistribution licensing.
2. Compare candidate families on Windows at 100%, 125%, and 200% display scale with grayscale and ClearType rendering.
3. Test compact folder/message rows, long subjects, email addresses, mixed scripts, tabular times/counts, and bold unread states.
4. Test pseudo-localization, Arabic or Hebrew directionality, CJK fallback, diacritics, emoji, and missing-glyph behavior.
5. Measure layout shifts and startup/package cost against the system stack.
6. Have an independent visual and accessibility reviewer approve the result before adding typography tokens to frontmatter.

Until then, use the platform UI sans stack and inherit user-selected message fonts only inside content contexts where Thunderbird behavior already supports them.

### Role Scale

| Role | Character | Intended use |
|---|---|---|
| Display | restrained, semibold, tight but not compressed | rare onboarding or empty-workspace statement |
| Heading | semibold with clear line-height | surface and dialog titles |
| Title | medium/semibold | panes, message subjects, grouped settings |
| Body | regular, comfortable measure | reading, explanations, form help |
| Compact body | regular/medium with tabular numerals where useful | folder rows, message rows, metadata, agenda |
| Label | medium, sentence case | controls, field labels, menu items |
| Caption | regular with sufficient contrast | secondary timestamps, hints, provenance |
| Monospace | platform mono | code, raw headers, addresses, and technical diagnostics only |

- Establish hierarchy with weight, size, line-height, and space before adding color.
- Avoid all-caps as a default label style; use it only for established short technical abbreviations.
- Reading measures should remain comfortable rather than stretching across the available pane.
- Unread emphasis must not cause row geometry to jump.

**The Rendering Evidence Rule.** A fashionable font name is not a typography decision. Licensing, script coverage, Windows rendering, density, and performance evidence decide.

## Layout

Mindy's desktop workspace uses cooperating structural regions: global rail, account/folder navigation, compact message list, and spacious reading pane. Persistent search belongs to the shell. Unified views and the account tree are equal navigation modes, with account and sender identity retained.

### Spacing and Density

- Use the 4px base spacing scale in frontmatter. Prefer `2`, `3`, `4`, `5`, `6`, and `8` for component rhythm; use `1` for tightly related icon/text corrections, not arbitrary nudges.
- **Compact density** serves folders, message rows, agenda, contact tables, and menus while preserving visible focus and comprehensible targets.
- **Comfortable density** serves forms, settings, event/contact editing, and dialogs.
- **Reading density** serves message bodies, long explanations, and composition with wider measure and line-height.
- User density settings change approved token assignments; they do not apply a global scale transform.

### Adaptive Topology

- **Wide:** show the cooperating workspace regions; prioritize reader width after scanning regions remain usable.
- **Medium:** collapse the folder region to a deliberate compact or overlay state while preserving rail, list, reader, selection, and focus.
- **Narrow:** show one primary task region at a time with predictable back navigation and retained account/identity context.
- **Zoom and display scaling:** test 80-200% app zoom and representative Windows scales. Reflow, do not merely shrink fonts or clip controls.
- **Pane persistence:** resizing, collapse, restore, display migration, and session restore must preserve user intent without trapping focus offscreen.

### Localization and Direction

- Use logical properties and direction-aware icons. Back/forward and pane order mirror only when meaning requires it.
- Allow 30-50% text expansion in navigation, controls, and dialogs without truncating essential actions.
- Email addresses, URLs, code, and mixed-direction metadata require isolation so surrounding RTL text does not reorder them misleadingly.
- Dates, times, numbers, names, sorting, and week conventions use locale-aware formatting rather than visual hard-coding.

**The Task Topology Rule.** Adapt by preserving the current task and context, not by compressing every pane until it becomes unusable.

## Elevation & Depth

Mindy is flat by default. Tonal layering, dividers, adjacency, and controlled insets establish persistent structure. Shadows indicate a real temporary layer, never a desire to make the interface feel modern.

| Level | Treatment | Uses |
|---|---|---|
| Base | canvas and structural surface contrast | application shell and content canvas |
| Inset | subtle tone or divider | folder/list panes, grouped controls, editor chrome |
| Raised | restrained border and low ambient shadow | menus, popovers, drag previews |
| Modal | scrim, strong boundary, focused shadow | dialogs requiring a blocking decision |
| Native/provider | inherited boundary | operating-system and remote content; do not counterfeit it |

Elevation tokens must define light and dark values separately and disappear or map to system boundaries in forced-colors mode.

**The Structural Surface Rule.** Persistent panes are architecture, not cards. Do not wrap every region in rounded containers or ambient shadows.

## Shapes

The form language is crisp, compact, and restrained. Major panes remain rectilinear structural surfaces. Small controls use modest corners; pills are reserved for chips, recipients, counts, or status objects whose semantics justify a capsule.

- Compact controls: `control-sm`.
- Primary fields and buttons: `control-md`.
- Menus, popovers, and modal overlays: `overlay-lg` only where the larger silhouette aids separation.
- Focus rings follow the component shape without reducing visible area.
- Splitters, dividers, selected edges, and progress tracks remain straight and precise.
- The M-envelope silhouette is brand geometry, not a motif to repeat across ordinary controls.

Icons use one coherent optical family, consistent stroke/fill logic, and platform-tested alignment. Prefer symbols over labels only when meaning is established and an accessible name remains. Destructive, security, provider, and offline icons cannot differ by color alone. Do not reuse Thunderbird brand artwork or Microsoft-like ribbon icon grammar.

## Components

Components are assembled from semantic tokens and shared primitives, then connected to Thunderbird behavior through Mindy adapters. Surface-specific CSS is not a component system.

### State Contract

Every interactive component defines relevant default, hover, active, selected, focus-visible, disabled, loading, success, warning, error, offline, and unavailable states. Hover never substitutes for selection; focus remains visible over selection; disabled content remains legible and explains dependencies where needed.

### Buttons and Actions

- Use a restrained teal primary action with measured inverse contrast.
- Secondary actions use neutral boundaries; quiet actions remain visible on hover and focus without becoming primary.
- Destructive actions use danger semantics, explicit wording, and safe default focus.
- Toolbars prioritize command grouping and overflow consistency over decorative separation.

### Fields, Search, and Recipient Inputs

- Labels remain persistent when the value or placeholder could be ambiguous.
- Focus uses the semantic focus border/ring; invalid state adds error text and icon rather than replacing focus.
- Persistent global search is available without dominating title structure.
- Recipient tokens expose address, validity, selection, removal, and keyboard order to assistive technology.

### Navigation, Tabs, and Lists

- Active destination, selected item, hover, unread, and keyboard focus are visually distinct.
- Dense rows preserve sender/title, subject/summary, account/source, status, and time hierarchy.
- Counts use tabular numerals and do not move row labels as values change.
- Tab and pane restoration return focus to a meaningful owned control.

### Banners, Dialogs, and Progress

- Banners identify severity, consequence, and recovery; status changes use appropriate live-region behavior without excessive announcements.
- Dialogs state the decision, preserve focus, support Escape only when cancellation is safe, and return focus to their invoker.
- Progress distinguishes determinate, indeterminate, paused, failed, and cancellable work. Animation is not the sole status carrier.

### Motion

- Motion is brief, purposeful, and event-driven. Avoid constant loops and ornamental workspace transitions.
- Prefer opacity and transform for transient feedback; avoid layout animation across dense lists.
- Reduced-motion mode removes nonessential movement while preserving status through static changes.
- The mark's upper curves may move vertically like expressive eyebrows for launch, sync, or new-mail activation only after performance and reduced-motion validation. A static fallback is mandatory.

### Accessibility

- Meet WCAG AA contrast: at least 4.5:1 for normal text and 3:1 for large text and meaningful UI boundaries.
- Preserve logical focus order, visible focus, keyboard operation, names/roles/states, screen-reader reading order, high contrast, reduced motion, zoom, and text reflow.
- Do not use color, animation, position, or sound as the only carrier of status.
- Compact density cannot cause overlap, hidden labels, or ambiguous targets at increased text size.

## Do's and Don'ts

### Do

- **Do** reconstruct composition through Mindy-owned adapters, components, primitives, and semantic tokens.
- **Do** use navy for structure, teal for primary interaction, and electric blue sparingly.
- **Do** keep scanning surfaces compact and reading or composition surfaces spacious.
- **Do** retain Thunderbird's mature behavior and semantics where they are sound.
- **Do** treat native, toolkit, extension, and provider surfaces as explicit inherited or wrapped boundaries.
- **Do** validate themes, high contrast, localization, RTL, zoom, display scaling, keyboard use, and screen readers with runtime evidence.
- **Do** fail closed when an upstream change produces an unexplained visual or contract delta.

### Don't

- **Don't** resemble Outlook: no dominant corporate blue, blue title bar, ribbon grammar, broad flat-blue fields, or Microsoft-like selection treatment.
- **Don't** look like stock Thunderbird with a navy/teal recolor. Reusing inherited hierarchy, spacing, controls, and default states without an ownership decision is not reconstruction.
- **Don't** copy proprietary assets or interaction chrome from another mail client.
- **Don't** scatter surface-local palettes, type scales, radii, focus rules, or motion values.
- **Don't** turn every pane into a rounded floating card.
- **Don't** hide inherited behavior without an owned, accessible route to the same job.
- **Don't** style remote or native content as though Mindy controls it.
- **Don't** animate the mark continuously or require motion to understand state.
- **Don't** treat provisional logo option 01 as immune to refinement.
