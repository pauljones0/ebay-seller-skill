#!/usr/bin/env bash
# Scaffold a private tracking repo for the ebay-seller pipeline.
# Usage: repo-scaffold.sh [repo-dir]   (default: sell-my-stuff)
set -euo pipefail

REPO="${1:-sell-my-stuff}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$REPO"/{photos,receipts,items,lots,comps-cache}
cd "$REPO"

if [ ! -d .git ]; then
  git init -q
fi

if [ ! -f README.md ]; then
  cat > README.md <<'EOF'
# Sell My Stuff — eBay pipeline tracker

Private repo. Each item's `items/<item-id>/status.txt` holds its pipeline stage:

`intake → identified → comps_done → decided → drafted → listed → sold → shipped → complete`

Per-stage artifacts live in `items/<item-id>/` (see the ebay-seller skill's
`assets/templates/`); every decision is logged in the item's `log.md`.
Lots get `lots/<lot-id>/` with a `members.txt` of member item-ids.
EOF
fi

echo "Scaffolded $REPO."
echo "Templates: $SKILL_DIR/assets/templates/"
