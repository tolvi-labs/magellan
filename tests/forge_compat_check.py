#!/usr/bin/env python3
"""
Real, runnable check that Magellan's output schema is a strict superset of
Forge's actual tasks.json validator. Run with Forge's own venv so the exact
`jsonschema` version and `forge.plan.manifest` module Forge ships are what's
being checked against — not a reimplementation.

Usage:
    /Users/alantorres/tolvi-labs/forge/.venv/bin/python3 tests/forge_compat_check.py
"""
import sys

import jsonschema

sys.path.insert(0, "/Users/alantorres/tolvi-labs/forge/src")
from forge.plan.manifest import TASKS_SCHEMA, Manifest  # noqa: E402

# --- Red: a deliberately non-compliant example should fail validation ---
INVALID = {
    "feature": "Healthz",
    "stack": "node",
    "tasks": [
        {"id": "t1", "title": "Add /healthz endpoint", "files": ["src/healthz.ts"]},
        # missing required "acceptance_criteria" on t1
    ],
}
try:
    jsonschema.validate(INVALID, TASKS_SCHEMA)
    print("FAIL: expected ValidationError on a task missing acceptance_criteria, got none")
    sys.exit(1)
except jsonschema.ValidationError:
    print("OK: invalid fixture (missing acceptance_criteria) correctly rejected")

# --- Green: a Magellan-shaped output, including the extra `context` field,
#     must validate cleanly. ---
VALID_MAGELLAN_OUTPUT = {
    "feature": "Healthz",
    "stack": "node",
    "tasks": [
        {
            "id": "t1",
            "title": "Add /healthz endpoint",
            "files": ["src/healthz.ts", "src/routes.ts"],
            "dependencies": [],
            "acceptance_criteria": ["GET /healthz returns 200 with a JSON status body"],
            "context": {
                "decisions": [
                    {
                        "path": "vault/decisions/2026-06-01-routes-register-in-routes-ts.md",
                        "title": "Public routes register in src/routes.ts, not inline in server.ts",
                        "rationale": "keeps the public surface auditable in one file",
                    }
                ],
                "refs": [],
                "interfaces": {"consumes": [], "produces": ["GET /healthz -> 200 {status: 'ok'}"]},
            },
        },
        {
            "id": "t2",
            "title": "Add rate-limit guard on /healthz",
            "files": ["src/healthz.ts"],
            "dependencies": ["t1"],
            "acceptance_criteria": ["A burst of requests past the configured limit gets a 429"],
            "context": {
                "decisions": [],
                "refs": [{"file": "fixtures/toy-repo/src/rateLimiter.ts", "line": 2, "symbol": "RateLimiter"}],
                "interfaces": {"consumes": ["GET /healthz -> 200 {status: 'ok'}"], "produces": []},
            },
        },
    ],
}

jsonschema.validate(VALID_MAGELLAN_OUTPUT, TASKS_SCHEMA)
print("OK: Magellan-shaped output (with per-task `context`) validates against Forge's real TASKS_SCHEMA")

manifest = Manifest.from_dict(VALID_MAGELLAN_OUTPUT)
assert manifest.feature == "Healthz"
assert len(manifest.tasks) == 2
assert not hasattr(manifest.tasks[0], "context"), "Forge's Task dataclass must not carry `context`"
print("OK: Manifest.from_dict() parses the file without erroring and silently drops `context`, as expected")

print("\nAll Forge-compatibility checks passed.")
