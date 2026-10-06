#!/usr/bin/env python3
"""Net-proceeds calculator for eBay sales.

Fee schedule: published 2026 eBay rates (verify in Seller Hub before relying on them).
  - Final value fee: 13.6% of total (item + buyer-paid shipping + tax slice) up to
    $7,500/item, 2.35% above. Basic Store subscribers: ~12.7% flat tier.
  - Per-order fee: $0.30 (total <= $10), $0.40 (total > $10).
  - Promoted Listings: seller-chosen ad rate, applied to total, stacks on FVF.

Usage:
  fees.py --price 300 --label 12 --ad-rate 0.02
  fees.py --price 280 --shipping-charged 15 --store
"""
import argparse

FVF_STANDARD = 0.136
FVF_STORE_BASIC = 0.127
FVF_HIGH_TIER = 0.0235
FVF_TIER_CAP = 7500.0


def net_proceeds(price, shipping_charged=0.0, ad_rate=0.0, label_cost=0.0,
                 cogs=0.0, store=False):
    total = price + shipping_charged
    fvf_rate = FVF_STORE_BASIC if store else FVF_STANDARD
    fvf = min(total, FVF_TIER_CAP) * fvf_rate + max(0.0, total - FVF_TIER_CAP) * FVF_HIGH_TIER
    per_order = 0.30 if total <= 10 else 0.40
    ad_fee = ad_rate * total
    net = total - fvf - per_order - ad_fee - label_cost - cogs
    return {
        "total": total, "fvf": fvf, "per_order": per_order,
        "ad_fee": ad_fee, "label_cost": label_cost, "cogs": cogs,
        "net": net, "keep_rate": net / total if total else 0.0,
    }


def main():
    p = argparse.ArgumentParser(description="eBay net-proceeds calculator")
    p.add_argument("--price", type=float, required=True, help="Item sale price")
    p.add_argument("--shipping-charged", type=float, default=0.0)
    p.add_argument("--ad-rate", type=float, default=0.0, help="Promoted-listings rate, e.g. 0.02")
    p.add_argument("--label", type=float, default=0.0, dest="label_cost")
    p.add_argument("--cogs", type=float, default=0.0, help="What you paid for the item")
    p.add_argument("--store", action="store_true", help="Basic Store FVF tier (~12.7%)")
    a = p.parse_args()
    r = net_proceeds(a.price, a.shipping_charged, a.ad_rate, a.label_cost, a.cogs, a.store)
    for k in ("total", "fvf", "per_order", "ad_fee", "label_cost", "cogs"):
        print(f"{k:>14}: ${r[k]:>9.2f}")
    print(f"{'net':>14}: ${r['net']:>9.2f}")
    print(f"{'keep_rate':>14}: {r['keep_rate']*100:>8.1f}%")


if __name__ == "__main__":
    main()
