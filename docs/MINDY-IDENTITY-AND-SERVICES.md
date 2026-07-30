# Mindy Identity and Service Policy

This policy defines the development baseline for Mindy identity and service ownership. It prevents inherited Thunderbird compatibility from being presented as Mindy release ownership.

## Scope and status

This is a policy document, not an implementation, legal, publishing, signing, support, or endpoint decision.

| Context | Position |
|---|---|
| Development baseline | Separate Mindy application identity while retaining only the compatibility exceptions named here. |
| Supported distribution | Requires its own approved release policy and the evidence listed below before it changes or retains a compatibility exception. |
| Local AI | Out of scope. |

## Development identity

- The visible product name is **Mindy**.
- `Mindy Project` is a development vendor string only. It is not a legal publisher, trademark assertion, signing identity, support organization, or release owner.
- The development namespace uses a separate Mindy application name, basename, profile, remoting name, and Windows product identity.
- Thunderbird's application GUID is a **temporary compatibility exception** for inherited add-on compatibility. It is not a Mindy identity decision.

Before a supported distribution changes or retains the Thunderbird application GUID, an approved release work unit must explicitly establish:

1. The target GUID and compatibility rationale.
2. Add-on compatibility and migration evidence for the target GUID.
3. Profile, remoting, update, installer, and rollback behavior on supported Windows configurations.
4. The accountable release owner and the applicable signing, support, privacy, and service policies.

Until then, no artifact using the Thunderbird application GUID may be described as a supported Mindy distribution.

## Service policy

Mindy must not point a Mindy updater or channel endpoint, telemetry submission, crash-report submission, donation, support, privacy, region, notification, or remote-settings endpoint to Mozilla or Thunderbird. Mindy must not invent replacement endpoints.

Each such service requires an explicit approved policy before release. That policy must name its owner, purpose, destination, user-facing disclosure, data handling, failure behavior, and release evidence. This policy does not implement or promise any endpoint.

This restriction does not disable inherited user-initiated networking. Account mail servers, provider OAuth, and account configuration flows remain available through inherited Thunderbird behavior. Branding and privacy checks must not globally disable networking in place of a service policy.

## Windows baseline

The initial Windows development baseline covers executable identity, icon, and About presentation only.

The following are deferred until separate approved policy and work units:

- Installer associations, protocol and file ownership, and default-app takeover.
- Maintenance service, MSIX, signing, publisher identity, and uninstall migration.

Deferred work must not be implied by the development baseline or treated as a supported-installation claim.

## Canonical artifact evidence

A canonical Mindy artifact requires a recorded Git commit, source pins, patch-series hash, mozconfig hash, clean tree status, configuration identity, executable hash, and explicit evidence for every service policy it uses. The receipt [schema and template](../contracts/provenance/) are checked by `tools/validate-artifact-receipt.py`; the template is not artifact evidence.

Development artifacts that lack this evidence are not release evidence. Inherited Thunderbird behavior remains subject to the boundaries in [Architecture](ARCHITECTURE.md), [Product](PRODUCT.md), [Security](SECURITY.md), [Roadmap](ROADMAP.md), and [Visual Ownership](VISUAL-OWNERSHIP.md).

## Review checklist

- [ ] Product presentation says `Mindy`; any development vendor string is limited to `Mindy Project`.
- [ ] Separate Mindy namespace values are used except for the documented temporary Thunderbird GUID exception.
- [ ] No unapproved Mozilla, Thunderbird, or invented Mindy service endpoint is configured or claimed.
- [ ] Account mail, provider OAuth, and account setup networking remain user-initiated inherited behavior.
- [ ] Windows changes remain within the development baseline or have a separately approved policy.
- [ ] Artifact evidence includes every required identity and service record.
