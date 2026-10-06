# ebay-seller-skill

An AI-agent skill that runs a **fully automated eBay selling pipeline**: you take
photos of your stuff (plus receipts/screenshots showing exact models), and the
agent handles identification, sold-comps research, pricing strategy, listing
writing and publishing, sale tracking, and shipping coordination. The only
things you do physically: take the photos, print the labels, pack the boxes.

## How it works

One `beads` issue per item carries it through ten stages in a private tracking
repo:

`intake → identified → comps_done → decided → drafted → listed → sold → shipped → complete`

- **Intake:** drop photos/receipts into `photos/<item-id>/`.
- **Identify:** the agent determines exact brand, model, MPN, specs, condition —
  and asks you only what the photos can't answer.
- **Comps:** ≥5 recent *sold* listings, median price, sell-through rate.
- **Decide:** `velocity` (sell fast) or `proceeds` (maximize net) mode; lot-vs-individual
  math (components netting under ~$20–25 get bundled); auction vs BIN + Best Offer.
- **Draft:** 80-char Cassini-friendly title, leaf category via eBay's Taxonomy API,
  every item specific filled, honest condition grading, ordered photo set.
- **Publish:** via eBay's official Sell APIs (inventory item → offer → publish),
  behind a review gate by default.
- **Monitor:** scheduled price-drop cadence, watcher offers, relist rules.
- **Ship:** labels via EasyPost/Shippo, tracking pushed back to eBay.

## What's in this repo

| Path | What |
|---|---|
| `SKILL.md` | The skill: setup, workflow, tooling, auth, operating rules |
| `bin/ebay.py` | eBay Sell API helper (OAuth, list/publish, orders, fulfill) |
| `bin/comps.py` | Sold-comps tracker via eBay's Browse API |
| `bin/fees.py` | Net-proceeds calculator |
| `references/` | Pricing strategy, listing craft, eBay API notes |
| `assets/` | Tracking-repo scaffold script + per-stage templates |

## Requirements

- An AI agent that loads skills from a directory (this repo *is* the skill).
- [`beads`](https://github.com/steveyegge/beads) — git-backed issue tracking (`bd init` in your tracking repo).
- A free [eBay Developers Program](https://developer.ebay.com/) app + one click on the
  OAuth consent page (one-time). Test in the sandbox first.
- Optional: [SoldComps](https://sold-comps.com/) API key (true 90-day sold history),
  EasyPost/Shippo account (programmatic shipping labels).

## Quickstart

```bash
# 1. Scaffold your private tracking repo
./assets/repo-scaffold.sh ~/sell-my-stuff && cd ~/sell-my-stuff && bd init

# 2. eBay auth (one-time)
export EBAY_APP_ID=... EBAY_CERT_ID=... EBAY_DEV_ID=... EBAY_RUNAME=...
<path-to-skill>/bin/ebay.py auth-url   # open, approve
<path-to-skill>/bin/ebay.py exchange --code <code>

# 3. Drop photos in photos/<item-id>/ and tell your agent:
#    "Sell everything in photos/ in proceeds mode."
```

## Honest limitations (researched Oct 2026)

- **No label-buying API:** eBay's Logistics API is limited-release and Pirate Ship
  has no public API — labels go through EasyPost/Shippo, tracking via eBay's
  Fulfillment API.
- **No free sold-comps API:** Marketplace Insights is gated to large partners, and
  scraping sold-listing pages violates eBay's User Agreement — use SoldComps,
  the Browse-API DIY tracker in `bin/`, or Terapeak manually.
- **No REST endpoint for Best Offer responses** — handle in Seller Hub; set
  native auto-accept/auto-decline thresholds at list time.
- eBay retires APIs aggressively — re-check `developer.ebay.com` if a call 404s.

## Disclaimer

Original implementation built from eBay's public API documentation and seller
research. Not affiliated with or endorsed by eBay Inc.
