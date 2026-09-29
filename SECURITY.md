# Security policy

## Reporting a vulnerability

If you discover a security vulnerability in Magellan, please **do not** open a public GitHub issue.

Instead, report it privately by [opening a security advisory](https://github.com/tolvi-labs/magellan/security/advisories/new) in this repository, or by emailing `security@tolvilabs.com`. We will acknowledge within 48 hours.

## Scope

The following are in scope:

- The installer (`install.sh`) and the plugin manifests
- Skill instructions that could lead an agent to run destructive commands, send vault or repository content off your machine, or write outside the paths the skill documents
- A compiled task graph that carries commands an executor would run without the brief asking for them

The following are out of scope (please file them as regular issues):

- Theoretical vulnerabilities without a proof of concept
- Issues in third-party dependencies (please report them upstream)
- Issues in your own deployment or configuration

## Supported versions

| Version | Supported |
|---|---|
| pre-1.0 | Best-effort; security fixes land on `main` |

A formal supported-versions policy will be published when 1.0 ships.
