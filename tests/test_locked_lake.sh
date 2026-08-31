#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/locked_lake.sh"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf -- "$TMP_ROOT"' EXIT

make_sandbox() {
  local root="$1"
  mkdir -p "$root/logs" "$root/no-git-bin" "$root/toolchain-bin" "$root/system-bin"
  cat > "$root/no-git-bin/git" <<'EOF'
#!/usr/bin/env bash
exit 97
EOF
  cat > "$root/system-bin/git" <<'EOF'
#!/usr/bin/env bash
exit 96
EOF
  cat > "$root/toolchain-bin/lake" <<'EOF'
#!/usr/bin/env bash
if [[ -n "${FAKE_LAKE_MARKER:-}" ]]; then
  printf 'invoked\n' >> "$FAKE_LAKE_MARKER"
fi
sleep "${FAKE_LAKE_SLEEP:-0}"
exit "${FAKE_LAKE_EXIT:-0}"
EOF
  chmod +x "$root/no-git-bin/git" "$root/system-bin/git" "$root/toolchain-bin/lake"
}

run_wrapper() {
  local root="$1"
  shift
  env \
    LOCKED_LAKE_SANDBOX_ROOT="$root" \
    LOCKED_LAKE_TOOLCHAIN_BIN="$root/toolchain-bin" \
    LOCKED_LAKE_SYSTEM_PATH="$root/system-bin:/usr/bin:/bin" \
    "$WRAPPER" "$@"
}

test_concurrent_refusal() {
  local root="$TMP_ROOT/concurrent"
  local second_exit
  make_sandbox "$root"
  FAKE_LAKE_SLEEP=2 run_wrapper "$root" env lean Smoke.lean > "$root/first.out" 2> "$root/first.err" &
  local first_pid="$!"
  for _ in $(seq 1 100); do
    [[ -d "$root/.locked_lake.lock" ]] && break
    sleep 0.02
  done
  [[ -d "$root/.locked_lake.lock" ]]
  set +e
  run_wrapper "$root" env lean Smoke.lean > "$root/second.out" 2> "$root/second.err"
  second_exit="$?"
  set -e
  [[ "$second_exit" -eq 73 ]]
  grep -q '^LOCKED_LAKE_CONCURRENT_REFUSAL ' "$root/second.err"
  wait "$first_pid"
  [[ ! -e "$root/.locked_lake.lock" ]]
  [[ "$(grep -c '^event=acquire ' "$root/logs/LOCKED_LAKE_AUDIT.log")" -eq 1 ]]
  [[ "$(grep -c '^event=release ' "$root/logs/LOCKED_LAKE_AUDIT.log")" -eq 1 ]]
}

test_wrong_git_path_refusal() {
  local root="$TMP_ROOT/wrong-git"
  local marker="$root/lake.marker"
  local exit_code
  make_sandbox "$root"
  rm -- "$root/no-git-bin/git"
  set +e
  FAKE_LAKE_MARKER="$marker" run_wrapper "$root" env lean Smoke.lean > "$root/run.out" 2> "$root/run.err"
  exit_code="$?"
  set -e
  [[ "$exit_code" -eq 78 ]]
  [[ ! -e "$marker" ]]
  [[ ! -e "$root/.locked_lake.lock" ]]
  grep -q '^LOCKED_LAKE_GIT_PATH_REJECTED ' "$root/run.err"
  grep -q "event=git_path_rejected .*expected=$root/no-git-bin/git actual=$root/system-bin/git" \
    "$root/logs/LOCKED_LAKE_AUDIT.log"
  grep -q '^event=release .* exit=78$' "$root/logs/LOCKED_LAKE_AUDIT.log"
}

test_concurrent_refusal
test_wrong_git_path_refusal
printf 'locked_lake tests: PASS\n'
