# Inbox Surface Brief

## Scope

- **Surface:** Primary desktop mail workspace.
- **Mode:** Operate.
- **Visual authority:** `assets/design-concepts/mindy-inbox-mockup-v1.png`.
- **Audience:** Independent professionals working across multiple accounts.
- **Primary job:** Process mail quickly without losing account, folder, or sender
  identity context.

## Experience thesis

The inbox is one continuous precision workspace, not a collection of cards.
Navigation becomes more specific from left to right: application, account,
message, content. The selected message is the focal moment. Mindy assistance is
available near the work but never competes with reading, replying, or sending.

## Topology

| Zone | Purpose | Persistent information |
|---|---|---|
| Global rail | Move between mail, calendar, contacts, and settings | Product identity and active space |
| Account pane | Switch between unified and full per-account navigation | Account color, address, folders, counts |
| Message list | Scan and triage the current scope | Sender, subject, snippet, time, state, account |
| Reading pane | Understand and act on the selected conversation | Sender, recipients, identity, content, attachments |
| Title region | Search and global window actions | Search scope and keyboard shortcut |

## Responsive topology

| Width | Behavior |
|---|---|
| Wide, 1280px and above | All four zones visible; user-resizable account and list panes |
| Medium, 960–1279px | Global rail remains; account pane becomes a reversible overlay |
| Narrow, below 960px | One task surface at a time: folders, list, or message; explicit Back restores context |

Mindy targets desktop Windows. Narrow behavior supports resized windows and
split-screen work; it is not a mobile design.

## Core states

| State | Required behavior |
|---|---|
| First account | Explain where unified views will appear; keep Add account visible |
| Multiple accounts | Show account origin on cross-account rows and sender identity before reply |
| Empty folder | Name the folder and account; offer relevant next action without illustration noise |
| Loading | Preserve pane geometry; use quiet skeleton rows after a short delay |
| Offline | Keep cached content usable; state which actions are queued or unavailable |
| Error | Keep prior safe content; explain scope, recovery, and whether data changed |
| No search results | Preserve query and filters; offer clear reset controls |
| Identity ambiguity | Block send until the sender identity is explicit |
| Assistant unavailable | Remove generation affordance or explain local setup; normal compose remains complete |
| Assistant working | Allow cancellation; never lock reading or ordinary reply |
| Assistant failed/cancelled | Preserve the user's draft exactly and return focus predictably |

## Component contracts

### Account tree

- Uses tree semantics with Left/Right collapse and expand, Up/Down movement, and
  type-ahead.
- Unified Inbox and the full tree are peers, not primary/fallback modes.
- Folder depth supports at least five visible nesting levels without ambiguity.
- Counts align independently of folder-name length.

### Message row

- Minimum content: sender and subject.
- Typical content: sender, subject, two-line snippet, time, unread, and account.
- Stress content: 140-character subject, missing avatar, attachment, flag, and
  two status markers without moving the time column.
- Selection, hover, focus, and unread remain visually distinct.

### Reading pane

- Message body measure remains comfortable as the window widens.
- Sender, recipient, timestamp, account, and security state are reachable
  without opening a separate details screen.
- Attachments follow message content and remain operable by keyboard.
- Remote-content, phishing, encryption, and certificate notices keep inherited
  security meaning while adopting Mindy styling.

### Global search

- `Ctrl+K` focuses search without discarding the current view.
- Scope is visible and changeable.
- Loading, partial, offline, empty, and error results are distinct.
- Escape restores the prior focus and view state.

### Draft assistance

- Entry points: reading-pane action and composer action.
- Context is explicit selected plaintext plus user-selected exemplars only.
- Output opens in preview; Apply is a separate explicit action.
- Cancel, timeout, crash, or error never mutate the draft.
- Generated text is announced as untrusted assistance, never as sent content.

## Accessibility and quality gates

- Meet WCAG 2.2 AA contrast for text and meaningful UI boundaries.
- Full mail workflow works without a pointer.
- Focus never disappears behind overlays or pane transitions.
- Windows text scaling to 200% preserves actions and reading order.
- High Contrast mode preserves selection, unread, error, and focus semantics.
- Motion respects reduced-motion settings and is never required to understand state.
- Virtualized lists expose stable accessible names and positions.

## Anti-goals

- No Thunderbird visual leakage on the primary mail surface.
- No copied Outlook ribbon, Gmail layout, or Postbox assets.
- No mobile-first collapse applied to a desktop productivity workflow.
- No assistant-first inbox or autonomous mailbox operation.

## Handoff acceptance

- Implementation references `DESIGN.md` tokens instead of one-off values.
- Every core state above has a deterministic fixture or test scenario.
- Wide, medium, narrow, keyboard, 200% text, and High Contrast are reviewed.
- The approved mockup remains the composition benchmark, not pixel-perfect law.
