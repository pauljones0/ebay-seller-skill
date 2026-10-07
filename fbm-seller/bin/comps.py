#!/usr/bin/env python3
"""FBM active-listing comp checker.

Wraps `facebook-cli marketplace search` with the owner's location/radius and
summarizes active-listing prices (FBM exposes no sold data).

Usage:
    bin/comps.py "sony wh-1000xm5" [--radius 62] [--pages 3] [--min 0] [--max 0]

Respects the facebook-cli quirks: no --sort-by with location params,
page 2 often returns empty while page 3 has results, ~30s between requests.
"""
import json
import re
import statistics
import subprocess
import sys
import tempfile
import time

LAT, LNG = 52.1332, -106.6700  # Saskatoon, SK default


def parse_price(s):
    if not s:
        return None
    m = re.search(r"[\d,]+(?:\.\d+)?", str(s))
    return float(m.group(0).replace(",", "")) if m else None


def search(query, radius, pages, min_price, max_price):
    listings = []
    after = None
    for page in range(pages):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            out = f.name
        cmd = [
            "facebook-cli", "marketplace", "search", "--query", query,
            "--latitude", str(LAT), f"--longitude={LNG}",
            "--radius-in-miles", str(radius), "--limit", "20",
            "--out", out,
        ]
        if min_price:
            cmd += ["--min-price", str(min_price)]
        if max_price:
            cmd += ["--max-price", str(max_price)]
        if after:
            cmd += ["--after", after]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            print(f"search failed (page {page + 1}): {r.stderr.strip()[:200]}",
                  file=sys.stderr)
            break
        try:
            data = json.load(open(out))
        except Exception as e:
            print(f"unparseable output (page {page + 1}): {e}", file=sys.stderr)
            break
        items = data.get("data", [])
        if not items:
            print(f"page {page + 1}: empty", file=sys.stderr)
        listings.extend(items)
        after = (data.get("paging") or {}).get("cursors", {}).get("after")
        if not after:
            break
        time.sleep(30)
    return listings


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--radius", type=int, default=62)
    ap.add_argument("--pages", type=int, default=3)
    ap.add_argument("--min", type=float, default=0)
    ap.add_argument("--max", type=float, default=0)
    a = ap.parse_args()

    listings = search(a.query, a.radius, a.pages, a.min, a.max)
    rows = []
    for it in listings:
        p = parse_price(it.get("price"))
        if p is None:
            continue
        rows.append({
            "price": p,
            "title": (it.get("title") or "")[:70],
            "condition": it.get("condition") or "?",
            "location": it.get("location") or "?",
            "url": it.get("product_url") or "",
        })
    if not rows:
        print("no priced listings found")
        return
    prices = sorted(r["price"] for r in rows)
    print(f"query: {a.query!r}  n={len(rows)} active listings")
    print(f"min ${prices[0]:,.0f}  median ${statistics.median(prices):,.0f}  "
          f"max ${prices[-1]:,.0f}")
    print("\ncheapest 5:")
    for r in sorted(rows, key=lambda r: r["price"])[:5]:
        print(f"  ${r['price']:,.0f}  [{r['condition']}] {r['title']} "
              f"({r['location']})")
    print("\npriciest 5:")
    for r in sorted(rows, key=lambda r: r["price"], reverse=True)[:5]:
        print(f"  ${r['price']:,.0f}  [{r['condition']}] {r['title']} "
              f"({r['location']})")
    json.dump(rows, open("comps-cache.json", "w"), indent=1)
    print(f"\nfull table saved to comps-cache.json "
          f"(copy into the item's comps.md)")


if __name__ == "__main__":
    main()
