---
name: fbm_seller
description: Sell items on Facebook Marketplace with minimal effort. Use when the user wants to list physical items for sale on Facebook Marketplace (FBM) — photos in, the agent handles identification (asking the owner only what's missing), active-listing comp pricing, listing drafting, and publishing via facebook-cli, with per-item tracking in a private repo. Supports local-pickup/meetup sales; never messages buyers without explicit say-so.
---

# FBM Seller

Turn photos of an item into a live Facebook Marketplace listing, track it to
sold, and hand the owner only the decisions that need a human.

## The deal

- **Input:** photos (one folder per item), plus anything the owner tells you.
- **You do:** identify the item, ask the owner only what the photos can't
  answer, research active-listing comps, recommend a price, draft the listing,
  publish it after approval, monitor it, and report buyer inquiries.
- **Owner does:** answer your questions, approve the listing (review gate),
  meet the buyer / hand over the item, mark it sold in the Facebook app.
- **Never:** invent description or condition details, message a buyer without
  the owner's explicit say-so on the exact message, or retry a failed
  Marketplace write without surfacing the error first.

## Tracking

No issue tracker — per-item files in the private tracking repo:

- `items/<item-id>/status.txt` — one word, the current stage:
  `intake → identified → comps_done → decided → drafted → listed → sold → complete`
- `items/<item-id>/log.md` — append-only dated log of every decision and
  change. Never act silently; if it isn't in the log, it didn't happen.

## Setup (first run)

1. **Tracking repo.** Reuse the shared selling repo (scaffolded by
   ebay-seller): `~/workspace/sell-my-stuff`. Save the repo path in memory.
2. **Check Facebook is connected:** `facebook-cli me` should return the
   owner's name. If not linked, run `facebook-cli connect-url` and give the
   owner the connect link.
3. **Defaults** (confirm once, then reuse): location Saskatoon, SK
   (`--latitude 52.1332 --longitude=-106.6700`), currency `CAD`, delivery
   types `public_meetup,door_pickup`. Save in memory.
4. **Publish gate.** Default: `review` — a listing goes live only after the
   owner approves the draft. `autopilot` only on a standing instruction.

## Workflow

### 1. Intake
Photos land in `photos/<item-id>/` (one item per folder; use a short slug).
Create `items/<item-id>/`, write `intake` to `status.txt`, and note the photo
paths in `log.md`. If the owner sent context (where it came from, known
flaws), file it in `items/<item-id>/identify.md` later — don't lose it.

### 2. Identify — ask questions here
Examine the photos and identify the item as precisely as possible (brand,
model, variant, what's included). Then **ask the owner** for what the photos
can't settle — typically:
- exact condition (you may NOT infer it — see rule 2),
- what's included vs missing (cables, box, manual, accessories),
- known flaws or repairs,
- anything that changes value (receipts, warranty, serial).

Keep it to one short round of questions. Fill `items/<item-id>/identify.md`
from `assets/templates/identify.md`, write `identified` to `status.txt`.
Don't proceed to comps until the identification is solid — a wrong identity
means wrong comps.

### 3. Comps
FBM has **no sold-data API** — price from *active* listings, and say so.
Run `bin/comps.py "<search terms>"` (wraps `facebook-cli marketplace search`
with the owner's location/radius; obeys the CLI quirks in the Operating
Rules). Fill `items/<item-id>/comps.md` from the template: n listings,
price min/median/max, condition mix, and how your item compares. If comps are
thin (<5), widen the query before widening the radius. Write `comps_done` to
`status.txt`.

### 4. Decide
Recommend a price using `references/fbm-listing-craft.md` §Pricing: list
~10–15% above the walk-away price to leave haggle room, unless the owner
wants it firm. Set delivery types (meetup / door pickup) and whether shipping
is offered at all (default: local only). Record the decision and the
walk-away floor in `log.md`; write `decided` to `status.txt`.

### 5. Draft
Write `items/<item-id>/listing.md` from `assets/templates/listing.md`:
title, price (CAD), description (grounded facts only), condition
(owner-confirmed), category, photo list, location, delivery types. Run the
pre-publish checklist in the template — all four Facebook publish-gate
fields (photos, condition, category, location) must be present for it to go
live on create. Write `drafted` to `status.txt`.

### 6. Review gate
Present the draft exactly as it will appear (title, price, description,
condition, category, photos, delivery) plus the comp basis for the price.
Publish only on explicit approval. Default is review; autopilot needs a
standing instruction.

### 7. Publish
After approval:
```sh
facebook-cli marketplace listing create \
  --title "<title>" --price <price> --currency CAD \
  --description "<description>" --condition <cond> --category <cat> \
  --photo <p1> --photo <p2> \
  --latitude 52.1332 --longitude="-106.6700" \
  --delivery-type public_meetup --delivery-type door_pickup
```
**Read the response `message` and report the true status** — `"Listing
published successfully"` means live; `"Listing created as draft"` means a
publish-gate field was missing (fix via `listing edit`, then `listing
publish`). Record `listing_id` + `product_url` in `log.md` and write `listed`
to `status.txt`. Then check buyer-message readiness once:
`hatch_messenger_cli check` — if Messenger Companion isn't connected, offer
the connect link; don't start monitoring unless asked.

### 8. Monitor
- `facebook-cli marketplace my-listings --status active` — the inventory.
- **Price drops:** if no serious inquiries in 7–14 days, propose a 5–10%
  cut (edit needs owner confirmation, like create).
- **Stale listings:** FBM buries old listings; after ~3–4 weeks with no
  action, propose delete + re-create (fresh `creation_date`).
- Log every check and change in `log.md`. Ping the owner only when a
  decision is needed.

### 9. Inquiries & sold
- **Report buyer inquiries; never reply without the owner's explicit say-so**
  on the exact message. (Standing rule — no exceptions.)
- When the owner confirms the sale: they mark it **sold in the Facebook
  app** (no CLI mark-sold exists), you write `sold` to `status.txt`, then
  `complete` after handoff, and file any receipt in `receipts/`.

## Auth & accounts

- Facebook: `facebook-cli` (Account Center link flow). Re-check with
  `facebook-cli me` after any auth error.
- Messenger Companion (buyer messages): `hatch_messenger_cli` — separate
  connection, separate consent.
- No API keys, no secrets, nothing to store.

## Output contract (per item)

- `items/<item-id>/identify.md`, `comps.md`, `listing.md`
- `status.txt` carried through
  `intake → identified → comps_done → decided → drafted → listed → sold → complete`
- `log.md` with every decision
- live listing URL recorded in `log.md`

## Operating rules

1. **Photos in, questions out.** The owner gives photos; you do everything
   else and ask only what the photos can't answer. Never pad the listing
   with invented specs, history, accessories, flaws, or measurements.
2. **Condition is owner-confirmed, never inferred.** Don't guess condition
   from photos or item type — ask. An unconfirmed listing stays a draft.
3. **Price from active comps; say there's no sold data.** FBM exposes no
   sold prices — the comp basis is live listings, and the owner should know
   that's a ceiling-biased sample.
4. **Review gate default.** Nothing goes live without approval unless the
   owner gave a standing autopilot instruction.
5. **Never message buyers on the owner's behalf** without their explicit
   say-so on the exact message. Report inquiries; draft replies only when
   asked.
6. **Never silently retry a failed write.** Surface the attempt, the exact
   error, your diagnosis, and the proposed fix — then wait.
7. **facebook-cli quirks** (from hard experience): don't combine `--sort-by`
   with `--latitude/--longitude/--radius-in-miles` (returns empty); the
   `distance` field is bogus — verify locality from `location`; page 2 of
   search often returns empty while page 3 has results — always fetch page 3
   before concluding. Negative longitude needs `--longitude="-106.6700"`.
8. **Draft before create/edit, confirm before delete.** Show the owner what
   will be posted or changed; deletion is permanent.
9. **Rate limits:** sequential searches, ~30s between requests; on a 429 or
   empty-data page, stop the run immediately — no retries.
