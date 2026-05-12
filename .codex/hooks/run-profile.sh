#!/usr/bin/env bash
# Dispatch Codex and git hooks by opt-in harness hook profile.

set -euo pipefail

CONTEXT="${1:-codex-pre-tool-use}"
ROOT="${HARNESS_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
PROFILE_FILE="${HARNESS_HOOK_PROFILE_FILE:-$ROOT/.codex/hook-profile.local}"

cd "$ROOT"

resolve_profile() {
  if [ -n "${HARNESS_HOOK_PROFILE:-}" ]; then
    printf '%s\n' "$HARNESS_HOOK_PROFILE"
    return
  fi

  if [ -n "${CODEX_HOOK_PROFILE:-}" ]; then
    printf '%s\n' "$CODEX_HOOK_PROFILE"
    return
  fi

  if [ -f "$PROFILE_FILE" ]; then
    local line
    line="$(sed -n '1p' "$PROFILE_FILE" | sed 's/#.*$//' | tr -d '[:space:]')"
    if [ -n "$line" ]; then
      printf '%s\n' "$line"
      return
    fi
  fi

  printf '%s\n' "minimal"
}

is_known_profile() {
  case "$1" in
    minimal|json-valid|phase-metadata|no-secrets|tdd|strict) return 0 ;;
    *) return 1 ;;
  esac
}

profile_enables_tdd() {
  case "$1" in
    tdd|strict) return 0 ;;
    *) return 1 ;;
  esac
}

profile_enables_phase_metadata() {
  case "$1" in
    phase-metadata|strict) return 0 ;;
    *) return 1 ;;
  esac
}

profile_enables_no_secrets() {
  case "$1" in
    no-secrets|strict) return 0 ;;
    *) return 1 ;;
  esac
}

deny_codex() {
  local reason="$1"
  python3 - "$reason" <<'PY'
import json
import sys

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": sys.argv[1],
    }
}))
PY
}

fail_profile() {
  local message="$1"
  if [ "$CONTEXT" = "codex-pre-tool-use" ]; then
    deny_codex "$message"
  else
    printf 'hook-profile: %s\n' "$message" >&2
  fi
  exit 2
}

run_template_validation() {
  echo "pre-commit: checking harness executor syntax"
  python3 -m py_compile scripts/create_phase.py scripts/execute.py scripts/report_phase.py scripts/validate_phase.py

  echo "pre-commit: running script unit tests"
  python3 -m unittest discover -s scripts -p 'test_*.py'

  echo "pre-commit: validating JSON files"
  find . -path ./.git -prune -o -name '*.json' -type f -print | while IFS= read -r file; do
    python3 -m json.tool "$file" >/dev/null
  done
}

run_phase_metadata_validation() {
  echo "pre-commit: validating registered phase metadata"
  local phase_names
  phase_names="$(python3 - "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
index_file = root / "phases" / "index.json"
data = json.loads(index_file.read_text(encoding="utf-8"))
phases = data.get("phases")
if not isinstance(phases, list):
    raise SystemExit("phases/index.json must contain a phases list")

for entry in phases:
    if isinstance(entry, dict) and isinstance(entry.get("dir"), str):
        print(entry["dir"])
PY
)"

  if [ -z "$phase_names" ]; then
    echo "pre-commit: no registered phases to validate"
    return
  fi

  while IFS= read -r phase_name; do
    [ -z "$phase_name" ] && continue
    python3 scripts/validate_phase.py "$phase_name"
  done <<< "$phase_names"
}

run_secret_scan() {
  echo "pre-commit: scanning tracked text files for obvious secrets"
  python3 - "$ROOT" <<'PY'
import re
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
result = subprocess.run(
    ["git", "ls-files"],
    cwd=root,
    capture_output=True,
    text=True,
)
if result.returncode == 0:
    files = [line for line in result.stdout.splitlines() if line]
else:
    files = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    ]

patterns = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"), "OpenAI-style secret key"),
    (
        re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][^'\"\s]{12,}['\"]"),
        "assigned secret-like value",
    ),
]

issues = []
for rel in files:
    path = root / rel
    if not path.is_file():
        continue
    if path.suffix not in {".md", ".py", ".json", ".toml", ".sh", ".yml", ".yaml", ".txt"}:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for line_num, line in enumerate(text.splitlines(), start=1):
        for pattern, label in patterns:
            if pattern.search(line):
                issues.append(f"{rel}:{line_num}: possible {label}")

if issues:
    print("ERROR: possible secrets found:", file=sys.stderr)
    for issue in issues:
        print(f"- {issue}", file=sys.stderr)
    raise SystemExit(1)
PY
}

run_codex_pre_tool_use() {
  if profile_enables_tdd "$PROFILE"; then
    bash "$ROOT/.codex/hooks/tdd-guard.sh"
    return
  fi

  cat >/dev/null
}

run_pre_commit() {
  echo "pre-commit: hook profile '$PROFILE'"
  run_template_validation

  if profile_enables_phase_metadata "$PROFILE"; then
    run_phase_metadata_validation
  fi

  if profile_enables_no_secrets "$PROFILE"; then
    run_secret_scan
  fi

  echo "pre-commit: template validation passed"
}

PROFILE="$(resolve_profile)"

if ! is_known_profile "$PROFILE"; then
  fail_profile "unknown hook profile: $PROFILE"
fi

case "$CONTEXT" in
  codex-pre-tool-use) run_codex_pre_tool_use ;;
  pre-commit) run_pre_commit ;;
  *) fail_profile "unknown hook context: $CONTEXT" ;;
esac
