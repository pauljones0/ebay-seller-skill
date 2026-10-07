# eBay API Notes (for the ebay-seller skill)

Researched Oct 2026 from eBay developer docs + live verification. eBay retires APIs aggressively — re-check `developer.ebay.com` before building on any endpoint.

## Auth (OAuth 2.0)

1. Free signup at the eBay Developers Program → Application Keys → create keysets for **Sandbox** and **Production**. Each keyset: App ID (client_id), Cert ID (client_secret), Dev ID.
2. **User tokens** (required for all Sell APIs) come from the **authorization-code consent flow**: seller opens a consent URL built with the app's RuName + scopes, approves once, agent exchanges the code for tokens.
3. Scopes (prefix `https://api.ebay.com/oauth/api_scope/`): `sell.inventory sell.fulfillment sell.account sell.finances sell.marketing`. (`sell.negotiation` is documented but eBay's authorize endpoint returned `invalid_scope` for it on this keyset — verified 2026-10-06; seller-initiated watcher offers will need revisiting.)
4. Token endpoints: Sandbox `https://api.sandbox.ebay.com/identity/v1/oauth2/token`, Production `https://api.ebay.com/identity/v1/oauth2/token`.
5. **Refresh tokens rotate on every refresh — always persist the newest one.** Do NOT send a `scope` parameter on the refresh grant — eBay rejects it with `invalid_scope`; omit it. Store in `~/.config/ebay-seller/tokens.json`, never in the repo.
6. Rate limits: ~1,000 req/day (app token), ~10,000/day (user token), ~50,000/day (refresh grant).

`bin/ebay.py` implements: `auth-url`, `exchange`, `refresh`.

## Listing flow (Inventory API)

Three dependent steps:
1. `PUT /sell/inventory/v1/inventory_item/{sku}` — createOrReplaceInventoryItem (title, description, imageUrls[], condition, availability). Creates nothing listable yet.
2. `POST /sell/inventory/v1/offer` — createOffer (price, categoryId, listing format/duration, fulfillment/payment/return **policy IDs**, merchantLocationKey). Draft only.
3. `POST /sell/inventory/v1/offer/{offerId}/publish` — returns `listingId`. **Point of no return — human confirms before this call.**

Prerequisites the API can't bootstrap: ≥1 fulfillment policy, ≥1 payment policy, ≥1 return policy, ≥1 inventory location. Create once via Account API (`/sell/account/v1/*_policy`) or in Seller Hub. (Note 2026-10-06: an account without Business Policies opted in gets `20403 "User is not eligible for Business Policy"` — enable Business Policies in Seller Hub first, or create the policies via the API.)

`bin/ebay.py`: `create-item`, `create-offer`, `publish`, `offers`, `suggest-category` (Taxonomy API: category suggestions + item aspects per leaf).

## Orders & fulfillment

- Poll `GET /sell/fulfillment/v1/order` (filter `lastmodifieddate`, 90-day window). **No REST order-notification topic exists** — poll every ~15 min.
- `POST /sell/fulfillment/v1/order/{orderId}/shipping_fulfillment` — marks shipped + attaches tracking. **Does NOT buy a label.**
- `POST /sell/fulfillment/v1/order/{orderId}/issue_refund` — refunds.
- `bin/ebay.py`: `orders`, `fulfill`.

## Labels (no eBay API)

eBay's Logistics (label-buying) API is Limited Release — expect denial. Pirate Ship has **no public API** (verified live Oct 2026). Use:
- **EasyPost** (REST, 100+ carriers, free tier then ~$0.01–0.05/label) or **Shippo** (API on all plans incl. free) → buy label → push tracking to eBay via `fulfill`.
- Carrier-direct: USPS Domestic Labels 2.0, UPS Developer Kit, FedEx API (bring your own accounts).

## Comps (no free eBay sold API)

- Marketplace Insights API: Limited Release, approvals go to large partners — expect 403.
- **SoldComps API** (sold-comps.com): 1 request → up to 240 sold listings, 90-day history, 8 marketplaces. Free tier; $9/$29/$79 mo. Default choice.
- DIY fallback: Browse API `GET /buy/browse/v1/item/{itemId}` on ended items — SOLD ≈ `OUT_OF_STOCK` + soldQuantity ≥ 1. No backfill; best-offer accepted prices never exposed. Label clearly as estimates.
- Terapeak Product Research: free in Seller Hub (avg sold, STR, trends) — **no API**, manual validation for high-value items.
- `bin/comps.py`: SoldComps lookup → `comps-cache/`.

## Best offers / negotiation

Two different things:
- **Buyer-initiated Best Offers** (accept/decline/counter): **no REST endpoint** — handle in Seller Hub UI (or legacy Trading API `RespondToBestOffer`). Set native auto-accept/auto-decline thresholds at list time instead.
- **Seller-initiated offers to watchers** (`GET /sell/negotiation/v1/find_eligible_items`, `POST /sell/negotiation/v1/send_offer_to_interested_buyers`): real REST endpoints, but they need the **`sell.offer`** OAuth scope ("View and manage offers and negotiations for your listings."). Beware: eBay's docs name a `sell.negotiation` scope that does not exist on real keysets — requesting it fails the whole consent with `invalid_scope`. Check the keyset's OAuth Scopes tab for ground truth. `bin/ebay.py find-eligible-items` / `send-offer --json` wrap these calls.

## Photos

- Requirements: ≥500px longest side (1600px recommended), ≤24 free/listing, ≤12MB, JPEG/PNG/GIF/TIFF/BMP/WEBP/HEIC. No text/borders/watermarks. Used items must show the actual item.
- REST Inventory API takes **HTTPS `imageUrls[]` only — no binary upload**. Upload via legacy Trading API `UploadSiteHostedPictures` → eBay Picture Services URL, or self-host.

## ToS boundaries (Feb 2026 User Agreement)

- **Scraping eBay pages is banned** (robots.txt names LLM-driven bots; Akamai-enforced). Never scrape sold-listing pages.
- Ban targets autonomous **buying** ("end-to-end flow that attempts to place orders without human review"). Sell-side automation via official APIs with seller consent is the intended use — but keep the human confirmation gate on `publishOffer` as a safety practice.
- Finances API (`https://apiz.ebay.com/sell/finances/v1`): transactions, payouts, fee breakdowns — use for P&L reconciliation.
- Marketing API (Promoted Listings): needs an active eBay **Store subscription** for production.
