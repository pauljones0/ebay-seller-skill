# selling-skills

Two AI-agent skills for selling physical items online with minimal manual
effort. Photos in, the agent handles identification, comp research, pricing,
listing drafting, publishing (after your approval), and sale tracking.

| Skill | Dir | Channel | How it lists |
|---|---|---|---|
| **ebay-seller** | `ebay-seller/` | eBay | eBay Sell APIs (OAuth) — auctions or fixed price, ships anywhere |
| **fbm-seller** | `fbm-seller/` | Facebook Marketplace | `facebook-cli` — local pickup / meetup, no fees |

## The deal (both skills)

- **You do:** drop photos in a folder, answer the agent's questions, approve
  each listing before it goes live, meet the buyer / ship the item.
- **The agent does:** identify the item, research comps, recommend a price,
  draft the listing, publish it after approval, monitor it (price drops,
  relists), track everything per-item in a private `beads` repo.
- **Never:** the agent won't message buyers on your behalf or publish
  without your say-so (review gate is on by default).

## Layout

Each skill is self-contained:

```
ebay-seller/
  SKILL.md            # the workflow
  bin/                # ebay.py (Sell API helper), comps.py, fees.py
  references/         # pricing strategy, listing craft, API notes
  assets/             # tracking-repo scaffold + per-stage templates
fbm-seller/
  SKILL.md            # the workflow
  bin/                # comps.py (active-listing comp aggregator)
  references/         # FBM listing craft + pricing
  assets/             # per-stage templates
```

## Requirements

- **ebay-seller:** an eBay developer keyset + OAuth user token (see
  `ebay-seller/references/ebay-api-notes.md`). CI secrets `EBAY_APP_ID` /
  `EBAY_CERT_ID` are the intended home for the keyset.
- **fbm-seller:** `facebook-cli` with a linked Facebook account (Marketplace listing write scope), and
  optionally Messenger Companion for buyer-message monitoring.

## Notes

- FBM has no sold-data API — the fbm-seller prices from *active* listings
  and says so. eBay sold comps are the cross-check when FBM comps are thin.
- Both skills keep per-item state in a private tracking repo (never in this
  public repo): photos, receipts, `identify.md` / `comps.md` / `listing.md`
  per item, one `beads` issue per item.

MIT licensed. Built from public API docs and first-hand usage, not from any
paid product.
