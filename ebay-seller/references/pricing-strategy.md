# Pricing Strategy (eBay used hardware)

Researched Oct 2026. Fee figures reflect published 2026 schedules — verify in Seller Hub before hard-coding.

## Mode switch

Ask once per batch (or default to `proceeds`):

- **velocity**: price at the low end of recent solds; 7-day auctions or promoted BIN at the 2% floor; watcher offers on; 7-day markdown cadence.
- **proceeds**: BIN at upper-median sold + Best Offer (auto-accept 95%, auto-decline 80% of list); 30-day GTC patience windows; no promotion until stale 60 days.

## Format decision

- **Default: Fixed Price (Buy It Now) + Best Offer, Good 'Til Canceled.** BIN dominates used-hardware sales (~80%); GTC accumulates sales history, which boosts Best Match ranking.
- **Auction** only for: liquidate-fast goals, or genuinely rare items with bidder pools. Auction realized ≈ 85–95% of median sold in liquid categories, higher variance.
- **Best Offer on BIN** stays live until purchase; on auctions it dies at the first bid.
- eBay requires any BIN on an auction listing to be ≥30% above the opening bid.

## Starting bid / reserve

- **$0.99 start only if STR ≥ ~60% AND comp price ≥ your floor.** Otherwise start at your floor price. Low starts in thin markets end at the low start.
- **No reserve.** Reserve fees cost extra and suppress bidding; set the opening bid at your true floor instead.
- eBay auto-relists no-bid auctions ~8 times free — intervene after 2 no-sale cycles, drop 10–15%.

## Sell-through rate (STR)

`STR = sold (90d) / (sold + active unsold) × 100`, from eBay sold/completed search.

| STR | Read | Action |
|---|---|---|
| 80–100% | hot | Price at/above median sold, BIN, no discount |
| 50–80% | normal | Median sold, BIN + Best Offer |
| 30–50% | soft | Slightly below median, or auction to liquidate |
| <30% | concern | Don't list alone — lot it or price aggressively low |

STR is the primary list-vs-wait-vs-lot input and the basis for days-to-sell estimates.

## Velocity tactics

- Undercut the bottom decile of *active* BINs (not below recent solds — that leaks money).
- 7-day auctions from a low start in liquid categories = guaranteed sale date.
- **Promoted Listings**: 2% floor, pay only on attributed sale. Start at 2%, ignore eBay's inflated suggested rates. Velocity lever for stale items, not a default.
- **Send offers to watchers**: 5–10% off converts fence-sitters fast.
- **End-and-Sell-Similar** (not blind relist) on dead listings — refreshes "new listing" treatment. Small price tweaks also create account activity.

## Proceeds tactics

- BIN at median-to-upper-quartile + Best Offer with native auto-accept/auto-decline thresholds.
- Give a fairly priced item **2 full 30-day cycles** before markdown (in proceeds mode with STR ≥50%, hold 60 days).
- Hardware seasonality is mild: Q4, January, late-August favor sellers; mid-summer lulls hurt big-ticket GPUs.
- Auction end-times: Sunday evenings for max bidder presence.

## Lots vs individual

**Lot when:** (a) any item's expected individual net < **$20–25** (fixed fees eat small sales); (b) items are complements (GPU + board + RAM = working core); (c) a component's STR <30% but the bundle's is healthy; (d) combined shipping saves real money.

**Rule: bundle any component whose individual net < $20–25 with a higher-value complement; compute both paths, pick the higher net.**

Worked example — RTX 3060 ($280) + B550 ($70) + 16GB DDR4 ($30), ~13.6% FVF + $0.40/order, $8/item or $14 combined shipping, ~$5 labor each:
- Individual nets: $228.50 + $47.10 + $12.50 ≈ **$288** (3 listings, 3 parcels)
- Lot at $380 BIN: 380 − 51.68 − 0.40 − 14 − 6 ≈ **$308** (1 listing, 1 parcel)

The lot wins despite the discount because the small items' individual nets were near-zero after fixed fees.

## Price-drop / relist cadence

- **Stale BIN, 30 days** no watchers/offers → drop 5–10%.
- **60 days** → drop 10–15% or flip to auction.
- **90 days** unsold → lot it or accept mispricing vs comps.
- Proceeds-mode exception: healthy STR (≥50%) → hold list price 60 days before any markdown.

## Net-proceeds formula

```
total = item_price + shipping_charged
net = total − (fvr × total) − per_order_fee − (ad_rate × total) − label_cost − cogs
```

2026 schedule (verify): FVF 13.6% of total (item + buyer shipping + tax slice) up to $7,500/item, 2.35% above; $0.30/order ≤$10, $0.40 above; Store Basic ≈12.7%; insertion 250 free/mo then $0.35 (GTC renewals count); promoted 2–100% seller-chosen, stacks on FVF.

Worked example — $300 GPU, free shipping, $12 label, 2% ad, non-store:
300 − 40.80 − 0.40 − 6.00 − 12.00 = **$240.80 net (80.3% keep)**. Without promotion: $246.80.
