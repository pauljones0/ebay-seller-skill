# Listing Craft (eBay used computer hardware)

Researched Oct 2026. Sources: eBay seller guides, Taxonomy API docs, reseller/SEO guides.

## Titles (80 chars — Cassini's #1 signal)

- Keyword order: **Brand → Model → Key spec → Condition**.
- Fill all 80 chars; never repeat a word. Capitalize each word; **no ALL CAPS, no symbols** — eBay says both can lower ranking.
- Gallery view truncates at ~55 chars — item identity must land in the first 50–55.
- Include condition for used gear (`Used`, `TESTED WORKING`).
- No other brands' names ("fits like NVIDIA…") — search manipulation, removable offense.
- No filler ("L@@K", "rare", "must see"), no keyword stuffing, no misspellings.
- Mine sold listings for the exact phrasing top sellers use.

**GPU title formula:** `[AIB brand] [GeForce/Radeon] [Model] [VRAM] [VRAM type] [Series] [Graphics Card] [TESTED]`
Example: `ASUS GeForce RTX 3060 12GB GDDR6 ROG Strix Gaming Graphics Card TESTED`
Model number and VRAM size are non-negotiable (1060 3GB vs 6GB are different markets).

## Category & item specifics

- Always the **deepest leaf category that genuinely fits** — it sets the specifics eBay asks for and the filters you appear under.
- Don't hardcode IDs: use the **Taxonomy API** (`get_category_suggestions`, then `getItemAspectsForCategory`) — IDs are marketplace-specific.
- Reference: GPUs = Computers/Tablets & Networking (58058) → Components & Parts (175673) → **Graphics/Video Cards (27386)** on eBay US. Siblings: RAM 170083, Motherboards 1244, CPUs 164, PSUs 42017.
- **Fill every specific.** Blank specifics = invisible to filtered searches. For a GPU: Condition + Seller Notes, Brand (AIB), Chipset Manufacturer, Chipset/GPU Model, Memory Size, MPN/UPC (or "Does not apply"). Brand+MPN or UPC lets eBay match its product catalog.

## Photos

Hard specs: ≥500px longest side, **~1600×1600 recommended** (buyer zoom), up to 24, JPEG/PNG/GIF/TIFF/HEIC/BMP. **No borders, text, artwork, watermarks** — hurts search placement.

**Shot list (in order):**
1. Hero: full card face-on, cleanest angle, plain bright background.
2. Front (fans/shroud) and back (backplate) straight-on.
3. Sides / top edge with power connectors visible.
4. I/O bracket close-up (ports = condition evidence).
5. **Label/sticker close-up** — model, serial, VRAM. Buyer authenticity check AND your anti-scam record (photograph the serial; switched-card return scams are real).
6. Fan close-ups (dust/wear = honest-used signal).
7. Every flaw, close and lit.
8. **Proof-of-work:** GPU-Z/monitoring screenshot with taskbar date visible.
9. Box/accessories — only if included.

Killers: stock photos (scam signal), dark/blurry/tiny-in-frame, cluttered background, accessories in frame that aren't included, photos embedded in the description (breaks mobile — use the uploader).

## Description (mobile-first, bullets, plain)

eBay: HTML won't render on the first mobile view-item page; keep it plain, white bg, black font, bullets. Shipping/payment/returns go in listing fields, not the body. No active content.

**Template for used GPU:**
1. Condition statement first, honestly graded: "Used. Fully tested and working. Light dust on fans, no damage."
2. What's included — exact list. Card-only? Say so.
3. Testing performed: "Ran FurMark 15 min, max 74°C, no artifacts; GPU-Z verified 12GB VRAM" (+ screenshot in photos).
4. Known flaws — enumerate all.
5. Specs recap: model, VRAM, power connectors, length, outputs.
6. Compatibility: PCIe version, PSU requirement.

**Returns:** 30-day free returns earns the badge, better rank, and is required for Top Rated Seller. **Top Rated Plus** (1-day handling + 30-day free returns) = 10% FVF discount + badge.

## Condition (use honestly)

| eBay condition | Use when |
|---|---|
| New | Unused, unopened, original packaging |
| Open box | Unused/tested-once, pristine, opened or missing packaging |
| Seller refurbished | You restored it (repaste/recap/repair), excellent condition |
| **Used** | **Default for working garage hardware** — previously used, fully operational |
| For parts or not working | Defective / needs repair. Never label a dead card "Used" — INAD returns are automatic |

## Common mistakes

Stock photos · wrong/shallow category · blank specifics · vague condition with no test detail · missing model/serial · misleading titles · ALL-CAPS/symbols · accessories pictured but not included · photos inside description · heavy HTML templates · set-and-forget pricing (check *sold* comps, not active listings) · trusting eBay's "Magical Listing" AI autofill (2026 seller reports: routinely wrong on category/condition/price — verify before publishing).

## 2026 ranking notes

Cassini weights: listing freshness (recent edits rank better), engagement (CTR, watchers, conversion/STR), seller performance (defects, tracking speed, response time). Keyword stuffing now hurts. GTC listings rank better than 30-day (less expiry churn). ~71% of purchases include free shipping — bake shipping into the BIN price.
