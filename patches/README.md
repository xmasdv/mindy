# Upstream patch contract

`series` is ordered. Each non-comment line names one patch below this directory;
patch paths inside each file are relative to the Gecko root (`comm/` prefixes
Thunderbird files). Bootstrap rejects absolute paths, traversal, duplicates, or
missing patches before applying the full series with `git apply`.

## Pinned `about:3pane` seams

Inspected at comm revision `faf78db7dfb184002adc6b859c8ad395ff216239`
(Thunderbird 140.13.0esr):

| Seam | Role |
|---|---|
| `comm/mail/base/content/about3Pane.xhtml` | Stable structural surface: `paneLayout`, `folderPane`, `folderTree`, `threadPane`, splitters, templates, and `messagePane`. |
| `comm/mail/base/content/about3Pane.js` | Folder modes/selection, thread view, commands, and pane coordination. Prefer adapters and narrow event seams over replacing inherited services. |
| `comm/mail/base/content/widgets/{pane-layout,message-pane,folder-tree-row}.mjs` | Existing custom-element boundaries for layout, reading, and account/folder rows. |
| `comm/mail/base/content/modules/ThreadPaneColumns.mjs` | Column contract paired with the row template in `about3Pane.xhtml`. |
| `comm/mail/themes/shared/mail/about3Pane.css` | Shared visual/layout seam; pilot styling should remain isolated here or in an added Mindy sheet. |

Manifest parents are `comm/mail/base/moz.build` → `comm/mail/base/jar.mn`
(`about3Pane.xhtml`, `about3Pane.js`, widgets/modules) and
`comm/mail/themes/windows/moz.build` → `comm/mail/themes/windows/jar.mn` →
`comm/mail/themes/shared/jar.inc.mn` (`about3Pane.css`). These are the narrow
parents overlay patches must update; do not create a parallel mail engine.
