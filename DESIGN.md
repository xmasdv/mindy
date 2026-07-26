---
name: Mindy Precision Workspace
description: A focused multi-account desktop mail workspace that feels modern, familiar, and unmistakably Mindy.
colors:
  accent: "#6750A4"
  accent-hover: "#57428F"
  accent-soft: "#EEE9F8"
  rail: "#29213D"
  surface: "#FFFFFF"
  surface-muted: "#F7F5FA"
  surface-selected: "#F0ECF8"
  text: "#24212A"
  text-muted: "#6F6A76"
  border: "#E4E0E8"
  focus: "#8069C3"
  success: "#2E7D5B"
  warning: "#A96514"
  error: "#B3261E"
typography:
  headline:
    fontFamily: "Segoe UI Variable Display, Segoe UI, sans-serif"
    fontSize: "24px"
    fontWeight: 600
    lineHeight: 1.25
  title:
    fontFamily: "Segoe UI Variable Text, Segoe UI, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.35
  body:
    fontFamily: "Segoe UI Variable Text, Segoe UI, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Segoe UI Variable Text, Segoe UI, sans-serif"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: 1.35
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  pill: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  xxl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "10px 16px"
    height: "36px"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
  search-field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: "8px 14px"
    height: "40px"
  message-row-selected:
    backgroundColor: "{colors.surface-selected}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
---

# Design System: Mindy Precision Workspace

## Overview

**Creative North Star: "Precision Workspace"**

Mindy is an operating surface for people who process mail across several
identities. It combines professional information density with calm hierarchy:
the user sees enough context to move quickly, but never fights visual noise.
Brand appears through proportion, typography, aubergine navigation, and precise
violet state cues rather than decoration.

The system is structurally original. It may inherit mail services, but its
primary chrome must not resemble Thunderbird, clone Outlook's ribbon, or copy
Gmail's composition. The approved inbox mockup is visual authority.

**Key characteristics:**
- Dense, legible, keyboard-first desktop operation.
- Equal access to Unified Inbox and the complete account tree.
- Persistent account and sender-identity context.
- Tonal layering instead of card-heavy decoration.
- Optional assistance remains visibly subordinate to mail.

## Colors

The palette is restrained: warm light neutrals carry the workspace, deep
aubergine anchors global navigation, and violet communicates selection, focus,
and Mindy-owned actions.

- **Mindy Violet** (`#6750A4`): primary actions and selected-state emphasis.
- **Deep Aubergine** (`#29213D`): global app rail only.
- **Quiet Lavender** (`#EEE9F8`): assistant and low-emphasis accent surfaces.
- **Warm Canvas** (`#FFFFFF`): reading and composition.
- **Soft Workspace** (`#F7F5FA`): secondary panels and grouped regions.
- **Selected Mist** (`#F0ECF8`): active folders and messages.
- **Graphite** (`#24212A`): primary text.
- **Muted Graphite** (`#6F6A76`): metadata and secondary text.
- **Soft Divider** (`#E4E0E8`): pane boundaries and separators.

**The One Accent Rule.** Violet occupies less than ten percent of a normal
mail screen. It identifies action or state; it never becomes decoration.

Semantic colors communicate status without replacing text or icon meaning.
Never use provider colors as Mindy's primary identity.

## Typography

Mindy uses the Windows-native Segoe UI Variable families. Display cuts serve
screen headings; text cuts serve dense lists and reading. This keeps the app
fast, familiar, and crisp without looking like a web dashboard.

- **Headline:** 24px/1.25, weight 600; message and major view titles.
- **Title:** 16px/1.35, weight 600; senders, subjects, and panel headings.
- **Body:** 14px/1.5, weight 400; messages, snippets, and controls.
- **Label:** 12px/1.35, weight 500; metadata, counts, and compact status.

Unread state uses weight and a restrained marker together. Do not encode it
with color alone. Uppercase is reserved for external acronyms.

## Layout

The wide desktop topology is a four-zone workspace: 64px global rail, flexible
account/folder pane, message list, and reading pane. Global search remains
centered in the title region and is available from every mail context.

Pane widths may be resized within safe minimums. Reading content owns remaining
space and does not collapse below a readable measure. At medium widths, the
account pane becomes a reversible overlay. At narrow desktop widths, the app
uses one task surface at a time with explicit Back navigation; it never
compresses all panes into unusable columns.

Spacing follows a 4px base rhythm. Dense rows use 8–12px internal gaps; control
groups use 16px; pane content uses 24–32px where reading comfort matters.

## Elevation & Depth

Mindy is flat by default. Pane hierarchy comes from tonal surfaces and 1px
dividers. Shadows are reserved for transient overlays, menus, and dialogs.
Hover never causes layout movement.

## Shapes

Controls use 8px corners; prominent search and assistant surfaces may use 12px.
Compact rows and selections use 4px. Pills are limited to tags, counts, and
identity indicators. Large rounded cards are prohibited in the core mail grid.

## Components

- **App rail:** aubergine field, 24px line icons, one selected tonal tile.
- **Account tree:** compact hierarchy with explicit provider/account identity,
  disclosure state, counts, and keyboard tree semantics.
- **Message row:** sender, subject, snippet, time, account marker, unread,
  flagged, and attachment states without horizontal jitter.
- **Search:** global, prominent, command-accessible, and honest about scope.
- **Command bar:** contextual actions in stable order; overflow holds rare
  actions rather than hiding core mail commands.
- **Reading pane:** generous text measure, persistent sender/account context,
  compact reply actions, and attachments grouped after content.
- **Assistant action:** outlined or quiet-lavender treatment. It never resembles
  Send, never blocks normal reply, and disappears cleanly when unavailable.

Every interactive component requires default, hover, focus-visible, active,
disabled, loading where applicable, error, and high-contrast behavior.

## Do's and Don'ts

### Do
- **Do** keep account and sender identity visible at decision points.
- **Do** preserve stable geometry while counts, flags, and loading states change.
- **Do** support complete keyboard operation and a visible 2px focus indicator.
- **Do** prefer progressive disclosure over removing professional capability.
- **Do** use realistic long subjects, deep folders, and multiple accounts in QA.

### Don't
- **Don't** expose Thunderbird logos, blue chrome, toolbar styling, tab shapes,
  default folder-tree visuals, or Mozilla iconography on primary surfaces.
- **Don't** reproduce Outlook's ribbon or Gmail's exact layout.
- **Don't** create a dashboard of independent cards.
- **Don't** make local assistance visually louder than reply or compose.
- **Don't** use animation as decoration or hide state behind color alone.
