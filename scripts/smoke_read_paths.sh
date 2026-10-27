#!/bin/bash
# CLIX read-path smoke test. Read-only commands only — safe to run any time.
# Usage: bash scripts/smoke_read_paths.sh   (read-only: never posts, likes or follows)
# Exits nonzero if any read command fails.
set -u
fail=0
TWEET_ID="${TWEET_ID:-2111192259073094035}"
run() {
  name="$1"; shift
  out=$(timeout 150 clix -c "$@" 2>/tmp/clix_smoke_err.$$); rc=$?
  if [ "$rc" -ne 0 ] || [ -z "$out" ]; then
    printf '%-16s FAIL rc=%s %s\n' "$name" "$rc" "$(head -c 120 /tmp/clix_smoke_err.$$ | tr '\n' ' ')"
    fail=1
  else
    printf '%-16s ok  %.90s\n' "$name" "$(echo "$out" | tr '\n' ' ')"
  fi
}
run doctor doctor
run feed feed -n 2
run search search "local llm" -t latest -n 2
run tweet tweet "$TWEET_ID"
run tweets_batch tweets "$TWEET_ID"
run user user OpenAI
run user_tweets user OpenAI tweets OpenAI -n 2
run followers user OpenAI followers OpenAI -n 2
run bookmarks bookmarks -n 2
run trending trending
run dm_inbox dm inbox
run jobs jobs search "AI engineer" -l Geneva -n 2
exit $fail
