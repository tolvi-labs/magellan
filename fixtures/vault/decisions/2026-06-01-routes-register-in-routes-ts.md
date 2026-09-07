---
tags: [decision, magellan-fixture]
date: 2026-06-01
repo: magellan-fixture
status: active
ticket: none
user_impact: none
product_area: Fixture
---

# Public routes register in src/routes.ts, not inline in server.ts

**Date:** 2026-06-01
**Repo:** magellan-fixture

## Why
Keeping route registration in one file makes the public surface auditable at a glance instead of scattered across server bootstrap code.

## How
Every public route handler is added to `src/routes.ts`; `server.ts` only imports and mounts that file.

## Outcome
`src/routes.ts` is the single source of truth for what's publicly reachable.
