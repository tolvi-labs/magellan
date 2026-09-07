---
tags: [decision, magellan-fixture]
date: 2025-01-01
repo: magellan-fixture
status: superseded
ticket: none
user_impact: none
product_area: Fixture
---

# Health checks require an API key

**Date:** 2025-01-01
**Repo:** magellan-fixture

## Why
Early concern that an open /healthz endpoint could leak deploy topology to scanners.

## How
`/healthz` checked a static API key header before responding.

## Outcome
Superseded — orchestrator health probes can't carry secrets, so the API-key gate was dropped; health checks are public by design.
