#!/usr/bin/env python3
"""
Real, runnable check that Magellan's output schema is a strict superset of
Forge's actual tasks.json validator. Run with Forge's own venv so the exact
`jsonschema` version and `forge.plan.manifest` module Forge ships are what's
being checked against — not a reimplementation.

Usage:
    /Users/alantorres/tolvi-labs/forge/.venv/bin/python3 tests/forge_compat_check.py

Forge's source tree is located automatically as a sibling checkout (tolvi-labs/forge
next to tolvi-labs/magellan). Override it with FORGE_SRC if it lives elsewhere:
    FORGE_SRC=/path/to/forge/src python3 tests/forge_compat_check.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema


def _resolve_forge_src() -> str:
    env = os.environ.get("FORGE_SRC")
    if env:
        return env
    try:
        script_dir = Path(__file__).resolve().parent
        common_dir = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=script_dir,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        # git prints an ABSOLUTE path only from a linked worktree; from a normal
        # clone it prints one RELATIVE to the cwd we ran it from (script_dir).
        # `script_dir / common_dir` resolves correctly either way, since
        # pathlib's `/` short-circuits to the right operand when it's already
        # absolute.
        main_repo_root = (script_dir / common_dir).resolve().parent
        candidate = main_repo_root.parent / "forge" / "src"
        if (candidate / "forge" / "plan" / "manifest.py").is_file():
            return str(candidate)
    except Exception:
        pass
    print(
        "ERROR: could not locate Forge's source tree. Set FORGE_SRC to the "
        "path of forge/src, or check out the 'forge' repo as a sibling of "
        "this one (tolvi-labs/forge next to tolvi-labs/magellan)."
    )
    sys.exit(1)


sys.path.insert(0, _resolve_forge_src())
from forge.plan.manifest import (  # noqa: E402
    TASKS_SCHEMA,
    Manifest,
    ManifestError,
    load_manifest,
)

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

# --- Forge's FULL load path: `load_manifest` does jsonschema.validate AND a
#     referential-integrity pass (every `dependencies` entry must name a task id
#     that exists in the same file). Exercise both halves against real files. ---
DANGLING_DEPENDENCY_OUTPUT = json.loads(json.dumps(VALID_MAGELLAN_OUTPUT))
DANGLING_DEPENDENCY_OUTPUT["tasks"].append(
    {
        "id": "t3",
        "title": "Log /healthz hits",
        "files": ["src/healthz.ts"],
        "dependencies": ["nonexistent-task"],
        "acceptance_criteria": ["Every /healthz request emits one structured log line"],
        "context": {"decisions": [], "refs": [], "interfaces": {"consumes": [], "produces": []}},
    }
)

with tempfile.TemporaryDirectory() as tmpdir:
    valid_path = Path(tmpdir) / "tasks.json"
    valid_path.write_text(json.dumps(VALID_MAGELLAN_OUTPUT), encoding="utf-8")
    loaded = load_manifest(valid_path)
    assert loaded.feature == "Healthz"
    assert len(loaded.tasks) == 2
    print("OK: load_manifest() accepts a Magellan-shaped file through Forge's full validation path, not just the schema layer")

    dangling_path = Path(tmpdir) / "tasks-dangling.json"
    dangling_path.write_text(json.dumps(DANGLING_DEPENDENCY_OUTPUT), encoding="utf-8")
    try:
        load_manifest(dangling_path)
        print("FAIL: expected ManifestError on a dangling dependency reference, got none")
        sys.exit(1)
    except ManifestError as exc:
        assert "depends on unknown task" in str(exc), f"unexpected ManifestError message: {exc}"
        assert "nonexistent-task" in str(exc), f"unexpected ManifestError message: {exc}"
        print(f"OK: load_manifest() rejects a dangling dependency reference with ManifestError ({exc}) — Magellan's Phase 2 self-check must catch this before emitting")

print("\nAll Forge-compatibility checks passed.")
