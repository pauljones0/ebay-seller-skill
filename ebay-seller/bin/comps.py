#!/usr/bin/env python3
"""Sold-comps tracker using eBay's Browse API (no scraping).

Two-phase flow (the Browse API has no sold-history backfill, so you capture
active listings first, then re-check them later):

  comps.py track --query "RTX 3060 12GB" --out comps-cache/rtx3060.json
  ... days later ...
  comps.py check --cache comps-cache/rtx3060.json

`check` classifies each tracked listing: SOLD (OUT_OF_STOCK / soldQuantity>=1
after endDate), ENDED_UNSOLD, or still ACTIVE, and prints a price summary.
Best-offer accepted prices are never exposed by eBay — treat those as estimates.

For true 90-day sold history with one call, use the SoldComps API
(sold-comps.com, paid) — see references/ebay-api-notes.md. Terapeak in Seller
Hub (no API) is the manual cross-check for high-value items.

Config: EBAY_APP_ID, EBAY_CERT_ID, EBAY_ENV=sandbox|production,
          EBAY_MARKETPLACE=EBAY_US
"""
import argparse
import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

HOSTS = {"sandbox": "https://api.sandbox.ebay.com",
         "production": "https://api.ebay.com"}
BROWSE_SCOPE = "https://api.ebay.com/oauth/api_scope"
_app_token = None


def api_base():
    return HOSTS[os.environ.get("EBAY_ENV", "sandbox")]


def app_token():
    global _app_token
    if _app_token:
        return _app_token
    app_id = os.environ.get("EBAY_APP_ID") or sys.exit("error: EBAY_APP_ID not set")
    cert_id = os.environ.get("EBAY_CERT_ID") or sys.exit("error: EBAY_CERT_ID not set")
    basic = base64.b64encode(f"{app_id}:{cert_id}".encode()).decode()
    req = urllib.request.Request(
        f"{api_base()}/identity/v1/oauth2/token",
        data=urllib.parse.urlencode(
            {"grant_type": "client_credentials", "scope": BROWSE_SCOPE}).encode(),
        headers={"Authorization": "Basic " + basic,
                 "Content-Type": "application/x-www-form-urlencoded"},
        method="POST")
    with urllib.request.urlopen(req) as r:
        _app_token = json.load(r)["access_token"]
    return _app_token


def browse(path, params=None):
    url = api_base() + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url, headers={"Authorization": "Bearer " + app_token(),
                      "X-EBAY-C-MARKETPLACE-ID": os.environ.get("EBAY_MARKETPLACE", "EBAY_US")})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"error: HTTP {e.code} on {path}\n{e.read().decode()[:1500]}")


def cmd_track(a):
    res = browse("/buy/browse/v1/item_summary/search",
                 {"q": a.query, "limit": a.limit or 50,
                  "filter": "buyingOptions:{FIXED_PRICE|AUCTION}"})
    items = [{"itemId": s.get("itemId"), "title": s.get("title"),
              "price": (s.get("price") or {}).get("value"),
              "currency": (s.get("price") or {}).get("currency"),
              "buyingOptions": s.get("buyingOptions"),
              "itemEndDate": s.get("itemEndDate"),
              "tracked_at": datetime.now(timezone.utc).isoformat()}
             for s in res.get("itemSummaries", [])]
    out = {"query": a.query, "items": items}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=2))
    print(f"tracked {len(items)} listings -> {a.out}")


def classify(item_id):
    d = browse(f"/buy/browse/v1/item/{urllib.parse.quote(item_id, safe='')}")
    price = (d.get("price") or {}).get("value")
    try:
        price = float(price) if price else None
    except (TypeError, ValueError):
        price = None
    sold_qty = d.get("estimatedSoldQuantity") or 0
    avail = d.get("estimatedAvailableQuantity")
    end = d.get("itemEndDate")
    ended = False
    if end:
        try:
            ended = datetime.fromisoformat(end.replace("Z", "+00:00")) < datetime.now(timezone.utc)
        except ValueError:
            pass
    if sold_qty and sold_qty >= 1 and (d.get("estimatedAvailabilityStatus") == "OUT_OF_STOCK" or ended):
        return "SOLD", price
    if ended:
        return "ENDED_UNSOLD", price
    return "ACTIVE", price


def cmd_check(a):
    cache = json.loads(Path(a.cache).read_text())
    sold_prices, rows = [], []
    for it in cache["items"]:
        try:
            status, price = classify(it["itemId"])
        except SystemExit as e:
            rows.append((it["itemId"], f"ERROR {e}", None))
            continue
        rows.append((it["itemId"], status, price))
        if status == "SOLD" and price:
            sold_prices.append(price)
    for item_id, status, price in rows:
        print(f"{status:>13}  ${price if price else '?':>9}  {item_id}")
    if sold_prices:
        sold_prices.sort()
        print(f"\nsold: {len(sold_prices)}  median ${median(sold_prices):.2f}  "
              f"min ${sold_prices[0]:.2f}  max ${sold_prices[-1]:.2f}")
    else:
        print("\nno confirmed solds yet — re-run check later.")


def main():
    p = argparse.ArgumentParser(description="eBay sold-comps tracker (Browse API)")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("track")
    t.add_argument("--query", required=True); t.add_argument("--out", required=True)
    t.add_argument("--limit", type=int, default=50)
    c = sub.add_parser("check"); c.add_argument("--cache", required=True)
    a = p.parse_args()
    {"track": cmd_track, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    main()
