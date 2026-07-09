#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.classify_v1_1_workspace_inventory import inspect_main_boundary
from tools.verify_v1_1_manifest_dry_run import discover_manifest_paths


DECISION = "continue_excluding_main"


def _git_status(path: str) -> str:
    try:
        return subprocess.check_output(["git", "-C", path, "status", "--short", "--branch"], text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unavailable"


def _write_adr(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# ADR-004: Nested main Repository Boundary",
        "",
        "Status: Accepted for V1.1",
        "Date: 2026-07-09",
        "",
        "## Context",
        "",
        "`main/` is a nested Git repository inside the top-level OGK release workspace. Blindly staging it would blur release ownership and can accidentally import an unrelated repository history into the OGK release line.",
        "",
        "## Decision",
        "",
        "Continue excluding `main/` from OGK-Final V1.1 release manifests and staging operations.",
        "",
        "## Consequences",
        "",
        "- V1.1 release evidence stays scoped to the top-level OGK hardening line.",
        "- `main/` can be handled later as a submodule, archive, migration, or separate release line.",
        "- Any future inclusion requires a dedicated ADR and explicit approval.",
        "",
        "## Verification",
        "",
        f"- Boundary status: `{result['main_boundary']['status']}`",
        f"- Manifest includes main paths: `{result['manifest_includes_main']}`",
        f"- Recommended decision: `{result['decision']}`",
    ]
    (output / "main_governance_adr.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_main_governance_boundary(output_dir: str | Path = "reports/v1_1/phase_04") -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    boundary = inspect_main_boundary()
    manifest = discover_manifest_paths()
    main_manifest_paths = [path for path in manifest if path.startswith("main/")]
    status = _git_status("main") if Path("main").exists() else "absent"
    ok = boundary["status"] in {"nested_git_repository", "gitfile_boundary", "absent"} and not main_manifest_paths

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.main_governance_boundary.v1",
        "ok": ok,
        "decision": DECISION,
        "main_boundary": boundary,
        "main_git_status": status,
        "manifest_includes_main": bool(main_manifest_paths),
        "main_manifest_paths": main_manifest_paths,
        "explicit_approval_required_for_future_inclusion": True,
        "destructive_action_taken": False,
    }
    (output / "main_governance_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    _write_adr(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify V1.1 nested main/ governance boundary.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_04")
    args = parser.parse_args()
    result = verify_main_governance_boundary(args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
