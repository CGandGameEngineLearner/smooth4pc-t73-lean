#!/usr/bin/env bash

set -u

readonly DEFAULT_SANDBOX_ROOT="/root/autodl-tmp/smooth4pc_t73_lean_build_20260831"
readonly DEFAULT_TOOLCHAIN_BIN="/root/autodl-tmp/lean/elan/toolchains/leanprover--lean4---v4.32.1/bin"
readonly DEFAULT_SYSTEM_PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

readonly SANDBOX_ROOT="${LOCKED_LAKE_SANDBOX_ROOT:-$DEFAULT_SANDBOX_ROOT}"
readonly TOOLCHAIN_BIN="${LOCKED_LAKE_TOOLCHAIN_BIN:-$DEFAULT_TOOLCHAIN_BIN}"
readonly SYSTEM_PATH="${LOCKED_LAKE_SYSTEM_PATH:-$DEFAULT_SYSTEM_PATH}"
readonly LOCKDIR="${LOCKED_LAKE_LOCKDIR:-$SANDBOX_ROOT/.locked_lake.lock}"
readonly AUDIT_LOG="${LOCKED_LAKE_AUDIT_LOG:-$SANDBOX_ROOT/logs/LOCKED_LAKE_AUDIT.log}"
readonly GIT_STUB="$SANDBOX_ROOT/no-git-bin/git"
readonly LAKE_BIN="$TOOLCHAIN_BIN/lake"

if (( $# == 0 )); then
  echo "usage: locked_lake.sh <lake-arguments...>" >&2
  exit 64
fi

if [[ ! -d "$SANDBOX_ROOT" || -L "$SANDBOX_ROOT" ]]; then
  echo "LOCKED_LAKE_BAD_SANDBOX_ROOT path=$SANDBOX_ROOT" >&2
  exit 72
fi

if [[ ! -d "$(dirname "$AUDIT_LOG")" ]]; then
  echo "LOCKED_LAKE_MISSING_AUDIT_DIRECTORY path=$(dirname "$AUDIT_LOG")" >&2
  exit 72
fi

readonly PID="$$"
if ! mkdir -- "$LOCKDIR" 2>/dev/null; then
  printf 'LOCKED_LAKE_CONCURRENT_REFUSAL pid=%s utc=%s lockdir=%s\n' \
    "$PID" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$LOCKDIR" >&2
  exit 73
fi

readonly ACQUIRE_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf 'pid=%s\nacquire_utc=%s\n' "$PID" "$ACQUIRE_UTC" > "$LOCKDIR/owner"

cleanup() {
  local exit_code="$?"
  local release_utc
  local release_failure=0
  trap - EXIT INT TERM
  release_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'event=release pid=%s acquire_utc=%s release_utc=%s exit=%s\n' \
    "$PID" "$ACQUIRE_UTC" "$release_utc" "$exit_code" >> "$AUDIT_LOG"
  rm -f -- "$LOCKDIR/owner"
  if ! rmdir -- "$LOCKDIR"; then
    printf 'event=release_failed pid=%s release_utc=%s lockdir=%s\n' \
      "$PID" "$release_utc" "$LOCKDIR" >> "$AUDIT_LOG"
    release_failure=1
  fi
  if (( release_failure != 0 && exit_code == 0 )); then
    exit_code=74
  fi
  exit "$exit_code"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

export PATH="$SANDBOX_ROOT/no-git-bin:$TOOLCHAIN_BIN:$SYSTEM_PATH"
git_path="$(command -v git 2>/dev/null || true)"
printf 'event=acquire pid=%s acquire_utc=%s lockdir=%s git_path=%s\n' \
  "$PID" "$ACQUIRE_UTC" "$LOCKDIR" "${git_path:-NOT_FOUND}" >> "$AUDIT_LOG"

if [[ ! -x "$GIT_STUB" || "$git_path" != "$GIT_STUB" ]]; then
  printf 'event=git_path_rejected pid=%s expected=%s actual=%s\n' \
    "$PID" "$GIT_STUB" "${git_path:-NOT_FOUND}" >> "$AUDIT_LOG"
  echo "LOCKED_LAKE_GIT_PATH_REJECTED expected=$GIT_STUB actual=${git_path:-NOT_FOUND}" >&2
  exit 78
fi

if [[ ! -x "$LAKE_BIN" ]]; then
  printf 'event=lake_binary_rejected pid=%s lake=%s\n' "$PID" "$LAKE_BIN" >> "$AUDIT_LOG"
  echo "LOCKED_LAKE_LAKE_BINARY_REJECTED path=$LAKE_BIN" >&2
  exit 78
fi

printf 'event=command_start pid=%s lake=%s argc=%s' "$PID" "$LAKE_BIN" "$#" >> "$AUDIT_LOG"
printf ' arg=%q' "$@" >> "$AUDIT_LOG"
printf '\n' >> "$AUDIT_LOG"

"$LAKE_BIN" "$@"
lake_exit="$?"
printf 'event=command_exit pid=%s exit=%s utc=%s\n' \
  "$PID" "$lake_exit" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$AUDIT_LOG"
exit "$lake_exit"
