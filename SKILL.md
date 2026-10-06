---
name: "ebay_seller"
description: "Run a fully automated eBay selling pipeline: photo intake, item identification, sold-comps research, pricing strategy (velocity vs proceeds, lots vs individual), listing drafting and publishing, sale tracking, and shipping. Use when the user wants to sell physical items on eBay with minimal manual effort."
---

# eBay Seller

## Purpose
Take a pile of items from "photos in a folder" to "sold and shipped" with the agent doing everything except the physical acts (photographing, printing labels, packing). State is tracked in a private git repo with `beads` — one bead per item moving through pipeline stages.

## Setup

1. Scaffold the tracking repo (private): `assets/repo-scaffold.sh ~/workspace/sell-my-stuff` — creates `photos/`, `receipts/`, `items/`, `lots/`, `comps-cache/` and runs `bd init`.
2. Confirm the selling mode with the user once per batch: `velocity` (sell fast) or `proceeds` (maximize net). Default: `proceeds`.
3. Confirm the publish gate: `review` (user approves each draft before it goes live — default) or `autopilot` (publish without asking; only on explicit user instruction).
4. Complete eBay API auth (see Auth). Without it, the skill runs through drafting and hands the user ready-to-paste listings.

## Workflow

### 1. Intake
- User drops photos (plus receipts/screenshots showing exact models) into `photos/<item-id>/` and `receipts/<item-id>/`. One `<item-id>` per physical item or natural bundle (e.g. `gpu-rtx3060-01`).
- `bd create "Sell: <nickname>" -t task -p 2 -l intake --description "photos/<item-id>/"`

### 2. Identify
- Examine photos + receipts. Determine exact brand, model, MPN/UPC, specs, condition grade, flaws, inclusions.
- Ask the owner only what the photos can't answer (testing done? original box? known defects?).
- Fill `items/<item-id>/identify.md` (template in `assets/templates/`). Then `bd update <id> -l identified` and comment the exact model.

### 3. Comps
- Find ≥5 recent **sold** listings for the same item/condition (sold comps, never active listings alone). Record median, p25–p75, active competition, and 90-day sell-through rate.
- Sources, in order: **SoldComps API** (sold-comps.com, paid — one call = up to 240 solds, 90-day history); `bin/comps.py track` + `check` (Browse-API DIY: capture active listings now, re-check later for SOLD status — no backfill, best-offer accepted prices never exposed); **Terapeak** in Seller Hub as the manual cross-check for high-value items.
- **Never scrape eBay sold-listing pages** — banned by the Feb 2026 User Agreement and Akamai-enforced. Cache raw pulls in `comps-cache/` to avoid re-querying.
- Fill `items/<item-id>/comps.md`. Then `bd update <id> -l comps_done`.

### 4. Decide (strategy)
Apply `references/pricing-strategy.md`:
- Mode tactics (velocity vs proceeds).
- **Lot vs individual:** compute both nets with `bin/fees.py`. Bundle any component whose individual net < $20–25 with a higher-value complement; pick the higher net. Record the math in the bead comment.
- Choose format (default BIN GTC + Best Offer; auction only per the rules), list price, floor / auto-decline, auto-accept, promoted rate (2% floor, only as a velocity lever).
- Lots become an **epic** bead with member items as children (`bd dep add <child> <epic>`); when the lot sells, close all children with the same reason.
- `bd update <id> -l decided` + comment with the full strategy.

### 5. Draft
- Write `items/<item-id>/listing.md` from the template, following `references/listing-craft.md`: 80-char title (identity in first 55), leaf category via Taxonomy API, every item specific filled, honest condition, 8–12 ordered real photos (serial photographed), mobile-plain bullet description with testing + flaws.
- Run the pre-publish checklist in the template. Verify net with `bin/fees.py` — must clear the floor.
- `bd update <id> -l drafted`.

### 6. Review gate
- `review` mode: present the draft (title, price, photos, net) and publish only on explicit approval.
- `autopilot` mode: publish directly (requires the user's standing instruction).

### 7. Publish
- Create inventory item → offer → publish via the eBay Sell API (see Tooling). Fall back to browser automation only if the API path is unavailable.
- Record listing ID + URL in a bead comment and `items/<item-id>/live.json`. `bd update <id> -l listed --status in_progress`.

### 8. Monitor (scheduled)
- Poll `bin/ebay.py orders --since <last check>` every ~15 min (REST has no order-notification topic). Per `bd list -l listed` item, check days-since-listed and watcher/offer activity against the price-drop cadence in `references/pricing-strategy.md`.
- Apply markdowns, send watcher offers (`Negotiation API` via Seller Hub or `sendOfferToInterestedBuyers`), or end-and-sell-similar via the API. Log every change with `bd comment` — never silently.
- Buyer Best Offers have **no REST accept/decline/counter endpoint** — handle in Seller Hub UI (or legacy Trading API). Rely on the native auto-accept/auto-decline thresholds set at list time.

### 9. Sold → ship
- Update `live.json` (sale price, buyer ship-to). Compute expected net.
- **Labels:** eBay offers no label API to third-party apps — buy via **EasyPost** or **Shippo** API, then `ebay.py fulfill --order-id ... --tracking ... --carrier ...` to attach tracking on eBay. If no label automation is configured, tell the user exactly which label to buy/print. The user prints, packs, ships.
- On shipment: tracking number into `live.json` + bead comment. `bd update <id> -l shipped`.

### 10. Complete
- Write final P&L to `items/<item-id>/pnl.md`. `bd close <id> --reason "net $X in Y days"`.
- `bd sync` at the end of every session.

## Tooling

- `bin/fees.py` — net-proceeds calculator. `fees.py --price 300 --label 12 --ad-rate 0.02 [--store] [--shipping-charged 15] [--cogs 50]`
- `bin/ebay.py` — eBay Sell API helper. `auth-url` → `exchange --code` (one-time consent) → `create-item --sku --json` → `create-offer --json` → `publish --offer-id`; also `offers`, `withdraw`, `orders --since`, `fulfill --order-id --tracking --carrier`, `suggest-category --query`, `policies`. Config via `EBAY_APP_ID/CERT_ID/DEV_ID/RUNAME`, `EBAY_ENV=sandbox|production`. Test in sandbox first.
- `bin/comps.py` — Browse-API comps tracker. `track --query ... --out comps-cache/x.json`, later `check --cache comps-cache/x.json` → SOLD/ENDED_UNSOLD/ACTIVE + price summary.
- `assets/repo-scaffold.sh` — new tracking repo scaffold.
- `assets/templates/` — `identify.md`, `comps.md`, `listing.md`, `pnl.md`.

## Auth

1. Free eBay Developers Program signup → Application Keys → create **Sandbox** and **Production** keysets (App ID, Cert ID, Dev ID). Set the env vars above.
2. Run `bin/ebay.py auth-url`, open the URL as the seller, approve the scopes once, then `bin/ebay.py exchange --code <code>`. Tokens save to `~/.config/ebay-seller/tokens.json` (mode 600); **refresh tokens rotate on every refresh — the helper persists the newest automatically.**
3. Prerequisites (one-time): ≥1 fulfillment, payment, and return policy + ≥1 inventory location — via `bin/ebay.py policies` (read) then Account API or Seller Hub (write).
4. Photo upload: REST takes HTTPS `imageUrls[]` only — upload via legacy Trading API `UploadSiteHostedPictures` (→ eBay Picture Services) or self-host. Full detail: `references/ebay-api-notes.md`.

## Output Contract

Per item: `identify.md`, `comps.md`, `listing.md`, `live.json`, `pnl.md`; bead carried through all ten stages with decisions in comments; a batch summary (listed / sold / net / pending actions). Human touches required: photos in, labels printed, parcels shipped.

## Operating Rules

1. Price from **sold** comps, never active listings alone.
2. Never publish a listing in `review` mode without explicit approval; `autopilot` only on standing instruction. The `publishOffer` call is the point of no return — human confirmation stays the default (also a ToS safety practice: no end-to-end flow without human review).
3. Never message buyers or any third party on the user's behalf — report, don't send.
4. Never scrape eBay pages — banned by the User Agreement, Akamai-enforced. Use the APIs.
5. Treat eBay's AI listing autofill as an unverified draft, never ground truth.
6. Grade condition honestly; a dead card is "For parts or not working", never "Used".
7. Photograph serial/model labels — authenticity proof and return-scam defense.
8. `bd sync` at session end; keep credentials out of the repo.
9. Fee/STR figures: verify against Seller Hub before treating as current; never hard-code stale rates into listings.
