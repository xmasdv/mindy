# Mindy Security Model

Mindy must protect mailbox content, profiles, account credentials, sender identity, and data integrity while processing untrusted inbound email and optional local model output. Security constraints apply before convenience features.

> **Status:** There is no production version or release channel. This document defines pre-release invariants and planned controls; it is not a claim of completed hardening or certification.

## Threat model

### Assets

- Mailbox content, drafts, sent mail, attachments, folders, and local profile data.
- Account credentials and authentication tokens managed through inherited services.
- Identities, aliases, signatures, recipient choices, and message-operation intent.
- Calendar and contact data.
- Application, AI runtime, model, installer, and update trust.
- Consent records and content-free pilot metrics.

### Untrusted inputs and actors

- Every inbound message, header, body, link, attachment, calendar item, and contact payload.
- Remote providers and network responses outside Mindy's control.
- Imported or migrated data and local profile fixtures.
- AI prompts assembled from message content and all generated output.
- Downloaded application, runtime, model, and update artifacts until independently verified.
- A local process attempting to exceed its granted capability.

### Primary failures to prevent

- Credential or mailbox-content disclosure.
- Wrong-account or wrong-identity sending.
- Message, folder, calendar, contact, or profile loss or corruption.
- Inbound content causing privileged execution or policy changes.
- AI output becoming an implicit mailbox command.
- Sandbox escape, network access, tool use, or unauthorized file writes.
- Unsigned, cross-authorized, substituted, or rolled-back artifacts.
- Telemetry capturing message content, personal data, or secrets.

## Non-negotiable invariants

### Mailbox and profile protection

- Inherited Thunderbird profile and security mechanisms remain authoritative unless a reviewed design explicitly changes a seam.
- Mindy must not claim OS-keychain protection or full-profile encryption.
- Credentials and tokens must never enter AI context, instrumentation, logs, fixtures, or crash metadata controlled by Mindy.
- Destructive or irreversible operations require inherited safeguards and explicit user intent.
- Malformed or adversarial content must fail closed without corrupting the profile.

### Identity and data integrity

- Account, sender identity, signature, recipients, and destination state must remain inspectable before send or mutation.
- Unified views must not erase authoritative account and folder boundaries.
- A shell error must not silently select another identity or redirect an operation across accounts.
- Security and regression testing must cover aliases, multiple accounts, offline transitions, restarts, and partial provider failures.

### Untrusted inbound email

- Rendering content does not grant access to privileged application APIs.
- Links, remote resources, attachments, and active content remain governed by inherited security policy and explicit user action.
- Message text included in an AI request remains data, never instructions that can change broker policy or acquire capabilities.
- Migration and import inputs receive the same distrust as network content.

## AI and subprocess invariants

The optional local assistant is disabled unless the user separately downloads an approved runtime and model.

- Inference runs in a sandboxed local process separated from the privileged application process.
- A deterministic broker allowlists request fields, context sources, response shape, and destination.
- Allowed context is only the current thread or selected message and sent exemplars explicitly selected by the user.
- Attachments, credentials, implicit mailbox history, autonomous search, embeddings, knowledge graphs, and continual training are excluded.
- The subprocess receives no network capability, tools, mailbox write APIs, or administrative APIs.
- The only accepted output is plaintext for preview.
- Applying output to the compose editor requires an explicit user action.
- The assistant cannot send, save, schedule, move, delete, label, or administer anything.
- Validation error, process error, unexpected output, or policy ambiguity fails closed and produces no mailbox action.

Generated text may be inaccurate, maliciously influenced, or inappropriate. It is untrusted until the user reviews it, and applying it does not bypass normal compose or send checks.

## Update and download trust

**Planned controls**

- Application, AI runtime, and model artifacts have separate manifests, authorization scopes, and update trust.
- Every distributed artifact is signed and verified before use.
- Version policy prevents rollback to a known older artifact.
- A runtime or model signature cannot authorize an application update, and vice versa.
- Failure to verify identity, integrity, compatibility, or version fails closed.
- Upstream security fixes are evaluated and integrated rapidly while preserving the small patch set.

**Unknown until ownership validation**

- Final application identifiers, domains, endpoints, certificates, key custody, rotation, recovery, and signing infrastructure.

No placeholder domain is authoritative.

## Telemetry and pilot metrics

Instrumentation is optional, consented, content-free, and limited to the [product validation gates](PRODUCT.md#provisional-validation-gates).

It must not collect:

- Message subjects, bodies, quoted text, drafts, generated text, prompts, or attachments.
- Email addresses, contact details, credentials, tokens, signatures, or folder names supplied by users.
- AI exemplar content or model inputs and outputs.
- Persistent identifiers that are unnecessary for the approved pilot analysis.

Metrics schemas, retention, access, deletion, consent withdrawal, and aggregation rules are **Unknown** until a pilot protocol and threat review approve them. No privacy or compliance claim should precede that work.

## Security review checklist

- [ ] Trust boundaries and attacker-controlled inputs are identified.
- [ ] Wrong-identity, cross-account, loss, and corruption cases are tested.
- [ ] Inbound content cannot acquire application or AI broker privileges.
- [ ] AI context and output stay within the explicit boundary.
- [ ] Sandbox network, tool, and write denials are proven.
- [ ] Artifact signature, compatibility, separation, and anti-rollback checks fail closed.
- [ ] Logs, crashes, fixtures, and metrics exclude content and secrets.
- [ ] Upstream security intake remains practical with the downstream patch set.

## Reporting a vulnerability

**Do not file a public issue or discussion for a suspected vulnerability.** Use GitHub's [private vulnerability reporting form](https://github.com/xmasdv/mindy/security/advisories/new) as the primary channel. If GitHub private vulnerability reporting is unavailable or inaccessible, email [christian@becominds.com](mailto:christian@becominds.com) privately. Do not post exploit details, credentials, mailbox data, tokens, or personal information publicly.

Acknowledgement targets, disclosure timelines, and supported versions remain **Unknown** and must be established before pilot distribution.

## Related documents

[Overview](../README.md) | [Product](PRODUCT.md) | [Architecture](ARCHITECTURE.md) | [Roadmap](ROADMAP.md) | [Contributing](../CONTRIBUTING.md)
