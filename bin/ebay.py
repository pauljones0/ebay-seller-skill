#!/usr/bin/env python3
"""eBay Sell API helper for the ebay-seller skill.

Scaffolded from eBay's REST Sell API docs (Oct 2026) — test in the sandbox
before trusting it with real listings. eBay retires APIs aggressively; if a
call 404s, check developer.ebay.com for the current path.

Config (environment):
  EBAY_APP_ID, EBAY_CERT_ID, EBAY_DEV_ID, EBAY_RUNAME
  EBAY_ENV=sandbox|production   (default: sandbox)
  EBAY_MARKETPLACE=EBAY_US      (default)

Tokens live in ~/.config/ebay-seller/tokens.json (created by `exchange`).
NEVER commit tokens or keys to a repo.

Examples:
  ebay.py auth-url
  ebay.py exchange --code <code-from-consent-redirect>
  ebay.py suggest-category --query "RTX 3060 graphics card"
  ebay.py create-item --sku gpu-rtx3060-01 --json items/gpu-rtx3060-01/inventory.json
  ebay.py create-offer --json items/gpu-rtx3060-01/offer.json
  ebay.py publish --offer-id 1234567890
  ebay.py orders --since 2026-10-01T00:00:00Z
  ebay.py fulfill --order-id 12-12345-67890 --tracking 1Z999 --carrier UPS
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

SCOPES = [
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
    "https://api.ebay.com/oauth/api_scope/sell.account",
    "https://api.ebay.com/oauth/api_scope/sell.finances",
    "https://api.ebay.com/oauth/api_scope/sell.marketing",
    "https://api.ebay.com/oauth/api_scope/sell.negotiation",
]

HOSTS = {
    "sandbox": "https://api.sandbox.ebay.com",
    "production": "https://api.ebay.com",
}
AUTHZ_HOSTS = {
    "sandbox": "https://auth.sandbox.ebay.com/oauth2/authorize",
    "production": "https://auth.ebay.com/oauth2/authorize",
}
TOKEN_DIR = Path.home() / ".config" / "ebay-seller"


def env(name, default=None, required=False):
    v = os.environ.get(name, default)
    if required and not v:
        sys.exit(f"error: {name} is not set")
    return v


def api_base():
    return HOSTS[env("EBAY_ENV", "sandbox")]


def token_path():
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    return TOKEN_DIR / "tokens.json"


def save_tokens(data):
    p = token_path()
    p.write_text(json.dumps(data, indent=2))
    os.chmod(p, 0o600)


def load_tokens():
    p = token_path()
    if not p.exists():
        sys.exit("error: no tokens saved — run `ebay.py exchange --code ...` first")
    return json.loads(p.read_text())


def basic_auth():
    app_id = env("EBAY_APP_ID", required=True)
    cert_id = env("EBAY_CERT_ID", required=True)
    raw = f"{app_id}:{cert_id}".encode()
    return "Basic " + base64.b64encode(raw).decode()


def token_request(data):
    req = urllib.request.Request(
        f"{api_base()}/identity/v1/oauth2/token",
        data=urllib.parse.urlencode(data).encode(),
        headers={"Authorization": basic_auth(),
                 "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def cmd_auth_url(_a):
    runame = env("EBAY_RUNAME", required=True)
    app_id = env("EBAY_APP_ID", required=True)
    q = urllib.parse.urlencode({
        "client_id": app_id,
        "response_type": "code",
        "redirect_uri": runame,
        "scope": " ".join(SCOPES),
    })
    print(f"{AUTHZ_HOSTS[env('EBAY_ENV', 'sandbox')]}?{q}")
    print("\nOpen the URL, approve, then run:")
    print("  ebay.py exchange --code <code-from-redirect>")


def cmd_exchange(a):
    tok = token_request({
        "grant_type": "authorization_code",
        "code": a.code,
        "redirect_uri": env("EBAY_RUNAME", required=True),
    })
    save_tokens(tok)
    print("tokens saved (access + refresh).")


def get_access_token():
    toks = load_tokens()
    # eBay access tokens last ~2h; refresh proactively using expires_in if present.
    # Simple approach: always refresh when `refresh` was never run this session is
    # overkill — instead refresh if the stored token is older than expires_in.
    issued = toks.get("_issued_at")
    expires_in = toks.get("expires_in", 7200)
    now = datetime.now(timezone.utc).timestamp()
    if issued and now - issued < expires_in - 300:
        return toks["access_token"]
    new = token_request({
        "grant_type": "refresh_token",
        "refresh_token": toks["refresh_token"],
        "scope": " ".join(SCOPES),
    })
    new["_issued_at"] = now
    # eBay rotates refresh tokens — persist whatever came back.
    if "refresh_token" not in new:
        new["refresh_token"] = toks["refresh_token"]
    save_tokens(new)
    return new["access_token"]


def api(method, path, body=None, params=None):
    url = api_base() + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": "Bearer " + get_access_token(),
                 "Content-Type": "application/json",
                 "Content-Language": "en-US",
                 "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:2000]
        sys.exit(f"error: HTTP {e.code} on {method} {path}\n{detail}")


def cmd_create_item(a):
    body = json.loads(Path(a.json).read_text())
    print(json.dumps(api("PUT", f"/sell/inventory/v1/inventory_item/{a.sku}", body), indent=2))


def cmd_create_offer(a):
    body = json.loads(Path(a.json).read_text())
    print(json.dumps(api("POST", "/sell/inventory/v1/offer", body), indent=2))


def cmd_publish(a):
    print(json.dumps(api("POST", f"/sell/inventory/v1/offer/{a.offer_id}/publish"), indent=2))


def cmd_offers(a):
    print(json.dumps(api("GET", "/sell/inventory/v1/offer", params={"sku": a.sku} if a.sku else None), indent=2))


def cmd_withdraw(a):
    print(json.dumps(api("POST", f"/sell/inventory/v1/offer/{a.offer_id}/withdraw"), indent=2))


def cmd_orders(a):
    filt = f"lastmodifieddate:[{a.since}..]"
    out, offset, limit = {"orders": []}, 0, 50
    while True:
        page = api("GET", "/sell/fulfillment/v1/order",
                   params={"filter": filt, "limit": limit, "offset": offset})
        batch = page.get("orders", [])
        out["orders"].extend(batch)
        if len(batch) < limit or (a.max and len(out["orders"]) >= a.max):
            break
        offset += limit
    if a.max:
        out["orders"] = out["orders"][:a.max]
    print(json.dumps(out, indent=2))


def cmd_fulfill(a):
    body = {
        "lineItems": [{"lineItemId": li} for li in a.line_items] or None,
        "shippedDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "shippingCarrierCode": a.carrier,
        "trackingNumber": a.tracking,
    }
    body = {k: v for k, v in body.items() if v is not None}
    print(json.dumps(api("POST", f"/sell/fulfillment/v1/order/{a.order_id}/shipping_fulfillment", body), indent=2))


def cmd_suggest_category(a):
    mkt = env("EBAY_MARKETPLACE", "EBAY_US")
    tree = api("GET", f"/commerce/taxonomy/v1/category_tree/default",
               params={"marketplace_id": mkt})["categoryTreeId"]
    print(json.dumps(
        api("GET", f"/commerce/taxonomy/v1/category_tree/{tree}/get_category_suggestions",
            params={"q": a.query}), indent=2))


def cmd_policies(a):
    mkt = env("EBAY_MARKETPLACE", "EBAY_US")
    for kind in ("fulfillment_policy", "payment_policy", "return_policy"):
        print(f"=== {kind} ===")
        print(json.dumps(
            api("GET", f"/sell/account/v1/{kind}", params={"marketplace_id": mkt}), indent=2))


def main():
    p = argparse.ArgumentParser(description="eBay Sell API helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("auth-url")
    e = sub.add_parser("exchange"); e.add_argument("--code", required=True)
    sub.add_parser("refresh")

    c = sub.add_parser("create-item"); c.add_argument("--sku", required=True); c.add_argument("--json", required=True)
    c = sub.add_parser("create-offer"); c.add_argument("--json", required=True)
    c = sub.add_parser("publish"); c.add_argument("--offer-id", required=True)
    c = sub.add_parser("offers"); c.add_argument("--sku", default=None)
    c = sub.add_parser("withdraw"); c.add_argument("--offer-id", required=True)
    c = sub.add_parser("orders"); c.add_argument("--since", required=True,
        help="e.g. 2026-10-01T00:00:00Z"); c.add_argument("--max", type=int, default=0)
    c = sub.add_parser("fulfill"); c.add_argument("--order-id", required=True)
    c.add_argument("--tracking", required=True); c.add_argument("--carrier", required=True,
        help="e.g. UPS, USPS, FEDEX"); c.add_argument("--line-items", nargs="*", default=[])
    c = sub.add_parser("suggest-category"); c.add_argument("--query", required=True)
    sub.add_parser("policies")

    a = p.parse_args()
    {"auth-url": cmd_auth_url, "exchange": cmd_exchange,
     "refresh": lambda _: print(get_access_token()[:12] + "..."),
     "create-item": cmd_create_item, "create-offer": cmd_create_offer,
     "publish": cmd_publish, "offers": cmd_offers, "withdraw": cmd_withdraw,
     "orders": cmd_orders, "fulfill": cmd_fulfill,
     "suggest-category": cmd_suggest_category, "policies": cmd_policies}[a.cmd](a)


if __name__ == "__main__":
    main()
