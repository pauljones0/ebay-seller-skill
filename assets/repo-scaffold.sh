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

if command -v bd >/dev/null 2>&1; then
  bd init >/dev/null 2>&1 || true
  echo "beads initialized."
else
  echo "NOTE: 'bd' (beads) not found. Install it, then run 'bd init' here:"
  echo "  curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash"
fi

if [ ! -f README.md ]; then
  cat > README.md <<'EOF'
# Sell My Stuff — eBay pipeline tracker

Private repo. One bead per item carries it through the pipeline:

`intake → identified → comps_done → decided → drafted → listed → sold → shipped → complete`

Per-stage artifacts live in `items/<item-id>/` (see the ebay-seller skill's
`assets/templates/`). Lots are epic beads with member items as children.

Agent loop: `bd ready --json` → do the stage's work → write artifacts →
`bd update <id> --label <next-stage>` → `bd comment <id> "decision"` → `bd sync`.
EOF
fi

echo "Scaffolded $REPO."
echo "Templates: $SKILL_DIR/assets/templates/"
