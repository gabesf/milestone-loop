#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_JSON="$REPO_ROOT/plugins/milestone-loop/.claude-plugin/plugin.json"
MARKETPLACE_JSON="$REPO_ROOT/.claude-plugin/marketplace.json"

if [ $# -lt 1 ]; then
  echo "Usage: scripts/release.sh \"<message>\"" >&2
  exit 1
fi

MESSAGE="$1"

CURRENT=$(jq -r '.version' "$PLUGIN_JSON")
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"
NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"

jq --arg v "$NEW_VERSION" '.version = $v' "$PLUGIN_JSON" > "$PLUGIN_JSON.tmp" && mv "$PLUGIN_JSON.tmp" "$PLUGIN_JSON"
jq --arg v "$NEW_VERSION" '.plugins[0].version = $v' "$MARKETPLACE_JSON" > "$MARKETPLACE_JSON.tmp" && mv "$MARKETPLACE_JSON.tmp" "$MARKETPLACE_JSON"

V_PLUGIN=$(jq -r '.version' "$PLUGIN_JSON")
V_MARKET=$(jq -r '.plugins[0].version' "$MARKETPLACE_JSON")

if [ "$V_PLUGIN" != "$V_MARKET" ]; then
  echo "ERROR: versions diverged — plugin.json=$V_PLUGIN marketplace.json=$V_MARKET" >&2
  exit 1
fi

echo "Bumped $CURRENT → $NEW_VERSION"

cd "$REPO_ROOT"

BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
  echo "WARNING: you are on '$BRANCH', not 'main'." >&2
  printf "Continue? [y/N] " >&2
  read -r REPLY
  [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ] || exit 1
fi

git add .
git commit -m "release: v$NEW_VERSION — $MESSAGE"
git push
echo "Done: v$NEW_VERSION pushed."
