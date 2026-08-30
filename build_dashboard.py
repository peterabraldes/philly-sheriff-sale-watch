"""
Render data/listings.json into dashboard.html.

Run this after scrape.py. The data is embedded directly in the page so the
dashboard is a single self-contained file that works offline and can be
published as an Artifact.
"""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "listings.json"
OUT = ROOT / "dashboard.html"

CSS = """
:root {
  --ground: #f2f4f7;
  --surface: #ffffff;
  --surface-2: #f8fafc;
  --ink: #101720;
  --ink-2: #47566b;
  --ink-3: #6b7c93;
  --line: #dee4ec;
  --line-strong: #c6d0dd;
  --accent: #12457a;
  --accent-soft: #e7eff7;
  --brick: #a8492a;
  --brick-soft: #f7eae4;
  --ok: #1e6b4f;
  --ok-soft: #e3f1ea;
  --warn: #8a5a12;
  --warn-soft: #faf0dc;
  --crit: #a32b22;
  --crit-soft: #fbe9e7;
  --shadow: 0 1px 2px rgba(16, 23, 32, .06), 0 4px 14px rgba(16, 23, 32, .05);
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground: #0d1219;
    --surface: #141c26;
    --surface-2: #1b2531;
    --ink: #e8eef5;
    --ink-2: #a2b1c4;
    --ink-3: #7a8aa0;
    --line: #26323f;
    --line-strong: #35455674;
    --accent: #5fa8e8;
    --accent-soft: #16293c;
    --brick: #e08a65;
    --brick-soft: #33211a;
    --ok: #5fcb9b;
    --ok-soft: #12271f;
    --warn: #e0b25f;
    --warn-soft: #2b2314;
    --crit: #f08a80;
    --crit-soft: #33191a;
    --shadow: 0 1px 2px rgba(0, 0, 0, .4), 0 4px 16px rgba(0, 0, 0, .3);
  }
}

:root[data-theme="dark"] {
  --ground: #0d1219;
  --surface: #141c26;
  --surface-2: #1b2531;
  --ink: #e8eef5;
  --ink-2: #a2b1c4;
  --ink-3: #7a8aa0;
  --line: #26323f;
  --line-strong: #354556;
  --accent: #5fa8e8;
  --accent-soft: #16293c;
  --brick: #e08a65;
  --brick-soft: #33211a;
  --ok: #5fcb9b;
  --ok-soft: #12271f;
  --warn: #e0b25f;
  --warn-soft: #2b2314;
  --crit: #f08a80;
  --crit-soft: #33191a;
  --shadow: 0 1px 2px rgba(0, 0, 0, .4), 0 4px 16px rgba(0, 0, 0, .3);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--ground);
  color: var(--ink);
  font-family: "Public Sans", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  font-size: 15px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

.wrap {
  max-width: 1180px;
  margin: 0 auto;
  padding: 40px 24px 72px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* ---------- masthead ---------- */

.masthead { display: flex; flex-direction: column; gap: 6px; }

.eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .13em;
  text-transform: uppercase;
  color: var(--brick);
}

h1 {
  font-family: Newsreader, ui-serif, Georgia, serif;
  font-weight: 600;
  font-size: clamp(30px, 4.4vw, 42px);
  line-height: 1.1;
  letter-spacing: -.015em;
  margin: 0;
  text-wrap: balance;
}

.standfirst {
  color: var(--ink-2);
  max-width: 62ch;
  margin: 0;
}

/* ---------- summary band ---------- */

/* Flex rather than grid so a partial last row stretches to fill instead of
   leaving an empty cell. */
.summary {
  display: flex;
  flex-wrap: wrap;
  gap: 1px;
  margin: 0;
  background: var(--line);
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: var(--shadow);
}

.stat {
  flex: 1 1 165px;
  background: var(--surface);
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.stat dt {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .09em;
  text-transform: uppercase;
  color: var(--ink-3);
  margin: 0;
}

.stat dd {
  margin: 0;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 25px;
  font-weight: 500;
  letter-spacing: -.02em;
  font-variant-numeric: tabular-nums;
}

.stat dd .unit {
  font-size: 13px;
  color: var(--ink-3);
  letter-spacing: 0;
}

.stat.is-urgent dd { color: var(--crit); }
.stat.is-fresh dd { color: var(--brick); }

/* ---------- controls ---------- */

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20px 28px;
  align-items: flex-end;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--line);
}

.field { display: flex; flex-direction: column; gap: 7px; }

.field > span {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .09em;
  text-transform: uppercase;
  color: var(--ink-3);
}

.segmented { display: flex; gap: 0; }

.segmented button {
  font: inherit;
  font-size: 13px;
  font-weight: 500;
  color: var(--ink-2);
  background: var(--surface);
  border: 1px solid var(--line-strong);
  margin-left: -1px;
  padding: 7px 14px;
  cursor: pointer;
  transition: background .12s, color .12s;
}

.segmented button:first-child { margin-left: 0; border-radius: 7px 0 0 7px; }
.segmented button:last-child { border-radius: 0 7px 7px 0; }
.segmented button:hover { background: var(--surface-2); color: var(--ink); }

.segmented button[aria-pressed="true"] {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
  position: relative;
  z-index: 1;
}

:root[data-theme="dark"] .segmented button[aria-pressed="true"],
:root:not([data-theme="light"]) .segmented button[aria-pressed="true"] {
  color: var(--ground);
}

.count-note {
  margin-left: auto;
  font-size: 13px;
  color: var(--ink-3);
  font-variant-numeric: tabular-nums;
}

/* ---------- date groups ---------- */

.groups { display: flex; flex-direction: column; gap: 38px; }

.group { display: flex; flex-direction: column; gap: 14px; }

.group-head {
  display: flex;
  align-items: baseline;
  gap: 14px;
  flex-wrap: wrap;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--ink);
}

.group-date {
  font-family: Newsreader, ui-serif, Georgia, serif;
  font-size: 23px;
  font-weight: 600;
  letter-spacing: -.01em;
}

.countdown {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 999px;
  font-variant-numeric: tabular-nums;
}

.countdown.soon { background: var(--crit-soft); color: var(--crit); }
.countdown.near { background: var(--warn-soft); color: var(--warn); }
.countdown.far  { background: var(--accent-soft); color: var(--accent); }

.group-count {
  margin-left: auto;
  font-size: 12px;
  color: var(--ink-3);
  letter-spacing: .05em;
  text-transform: uppercase;
  font-weight: 600;
}

/* ---------- cards ---------- */

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
  gap: 14px;
}

.card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 18px 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: var(--shadow);
}

.photo {
  display: block;
  position: relative;
  aspect-ratio: 16 / 9;
  border-radius: 7px;
  overflow: hidden;
  background: var(--surface-2);
  border: 1px solid var(--line);
}

.photo img { width: 100%; height: 100%; object-fit: cover; display: block; }

.photo .tag {
  position: absolute;
  left: 8px;
  bottom: 8px;
  background: rgba(0, 0, 0, .66);
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .07em;
  text-transform: uppercase;
  padding: 3px 7px;
  border-radius: 4px;
}

.photo:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

.card-head { display: flex; flex-direction: column; gap: 8px; }

.address {
  font-family: Newsreader, ui-serif, Georgia, serif;
  font-size: 19px;
  font-weight: 600;
  line-height: 1.25;
  letter-spacing: -.008em;
  margin: 0;
  text-wrap: balance;
}

.sub {
  font-size: 12.5px;
  color: var(--ink-3);
  font-variant-numeric: tabular-nums;
}

.chips { display: flex; flex-wrap: wrap; gap: 6px; }

.chip {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .04em;
  padding: 3px 8px;
  border-radius: 5px;
  background: var(--surface-2);
  color: var(--ink-2);
  border: 1px solid var(--line);
}

.chip.center { background: var(--accent-soft); color: var(--accent); border-color: transparent; }
.chip.transit { background: var(--ok-soft); color: var(--ok); border-color: transparent; }
.chip.new { background: var(--brick-soft); color: var(--brick); border-color: transparent; }
.chip.postponed { background: var(--warn-soft); color: var(--warn); border-color: transparent; }

.figures {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 12px 0;
  border-block: 1px solid var(--line);
}

.figure { display: flex; flex-direction: column; gap: 1px; }

.figure .label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--ink-3);
}

.figure .value {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 15px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.bid-line {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  font-size: 13px;
}

.bid-line .k { color: var(--ink-3); }

.bid-line .v {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.bid-line .v.accent { color: var(--brick); }

.geo {
  font-size: 12.5px;
  color: var(--ink-2);
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.geo span { display: block; }

.card-foot {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-top: auto;
  padding-top: 4px;
}

.card-foot a {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid transparent;
}

.card-foot a:hover { border-bottom-color: var(--accent); }
.card-foot a:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px; }

/* ---------- how bidding works ---------- */

.howto {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  box-shadow: var(--shadow);
}

.howto > summary {
  cursor: pointer;
  padding: 15px 20px;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 9px;
  list-style: none;
  border-radius: 10px;
}

.howto > summary::-webkit-details-marker { display: none; }

.howto > summary::before {
  content: "";
  width: 6px;
  height: 6px;
  border-right: 1.6px solid var(--brick);
  border-bottom: 1.6px solid var(--brick);
  transform: rotate(-45deg);
  transition: transform .15s;
}

.howto[open] > summary::before { transform: rotate(45deg); }
.howto > summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

.howto > summary .hint {
  margin-left: auto;
  font-weight: 400;
  font-size: 12.5px;
  color: var(--ink-3);
}

.howto-body {
  padding: 4px 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  border-top: 1px solid var(--line);
  margin-top: -1px;
  padding-top: 18px;
}

/* Numbered because these steps are a real sequence with hard deadlines:
   miss step 4 and the deposit from step 1 is gone. */
.steps {
  list-style: none;
  counter-reset: step;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.steps li {
  counter-increment: step;
  display: grid;
  grid-template-columns: 26px 1fr;
  gap: 12px;
  align-items: start;
}

.steps li::before {
  content: counter(step);
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent);
  background: var(--accent-soft);
  border-radius: 5px;
  width: 26px;
  height: 22px;
  display: grid;
  place-items: center;
}

.steps .t { font-weight: 600; display: block; }
.steps .d { color: var(--ink-2); font-size: 13.5px; }

.deadline {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 12px;
  font-weight: 600;
  color: var(--crit);
  background: var(--crit-soft);
  padding: 1px 6px;
  border-radius: 4px;
  white-space: nowrap;
}

.howto-note {
  font-size: 13px;
  color: var(--ink-2);
  background: var(--warn-soft);
  border-radius: 7px;
  padding: 12px 14px;
}

.howto-note strong { color: var(--warn); }

.howto-links { display: flex; flex-wrap: wrap; gap: 16px; font-size: 13px; font-weight: 600; }
.howto-links a { color: var(--accent); text-decoration: none; border-bottom: 1px solid transparent; }
.howto-links a:hover { border-bottom-color: var(--accent); }

/* ---------- empty + footer ---------- */

.empty {
  background: var(--surface);
  border: 1px dashed var(--line-strong);
  border-radius: 10px;
  padding: 44px 24px;
  text-align: center;
  color: var(--ink-2);
}

footer {
  border-top: 1px solid var(--line);
  padding-top: 20px;
  font-size: 12.5px;
  color: var(--ink-3);
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 78ch;
}

footer strong { color: var(--ink-2); font-weight: 600; }
footer a { color: var(--accent); }

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}

/* ---------- phones ---------- */

@media (max-width: 640px) {
  body { font-size: 14.5px; }
  .wrap { padding: 26px 15px 52px; gap: 24px; }
  .stat { flex-basis: 132px; padding: 13px 15px; }
  .stat dd { font-size: 21px; }
  .controls { gap: 14px 18px; }
  .count-note { margin-left: 0; width: 100%; }
  .segmented button { padding: 7px 11px; font-size: 12.5px; }
  .cards { grid-template-columns: 1fr; }
  .group-head { border-bottom-width: 1.5px; }
  .group-date { font-size: 19px; }
  .group-count { margin-left: 0; width: 100%; }
  .card { padding: 15px 16px 14px; }
  .address { font-size: 17.5px; }
  .figures { grid-template-columns: repeat(3, 1fr); gap: 6px; }
  .figure .value { font-size: 14px; }
}
"""

JS = """
const DATA = __DATA__;
const PHOTO_MODE = "__PHOTO_MODE__";   // 'streetview' when an API key is set, else 'links'
const SV_KEY = "__SV_KEY__";
const listings = DATA.listings;

// The county docket carries no photographs, so the nearest thing to a picture
// of the house is Google Street View at its coordinates.
function streetViewLink(r) {
  return `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${r.lat},${r.lon}`;
}

function photo(r) {
  if (PHOTO_MODE !== 'streetview' || !r.lat) return '';
  const src = `https://maps.googleapis.com/maps/api/streetview`
    + `?size=640x360&fov=80&location=${r.lat},${r.lon}&key=${SV_KEY}`;
  return `<a class="photo" href="${streetViewLink(r)}" target="_blank" rel="noopener">
      <img src="${src}" alt="Street View of ${r.address}" loading="lazy">
      <span class="tag">Street View</span>
    </a>`;
}
let place = 'all';
let order = 'date';

const money = n => n == null ? null : '$' + Math.round(n).toLocaleString('en-US');

function passes(r) {
  if (place === 'center') return r.is_center_city;
  if (place === 'transit') return r.is_center_city || r.is_transit_walkable;
  return true;
}

function sortRows(rows) {
  const by = {
    date: (a, b) => (a.days_until_sale ?? 1e9) - (b.days_until_sale ?? 1e9),
    value: (a, b) => (b.market_value ?? 0) - (a.market_value ?? 0),
    bid: (a, b) => (a.minimum_bid ?? 1e12) - (b.minimum_bid ?? 1e12),
    close: (a, b) => (a.miles_to_city_hall ?? 1e9) - (b.miles_to_city_hall ?? 1e9),
  }[order];
  return rows.slice().sort(by);
}

function chips(r) {
  const out = [];
  if (r.is_new) out.push(['new', 'New']);
  if (r.is_center_city) out.push(['center', 'Center City']);
  else if (r.is_transit_walkable) out.push(['transit', 'Near transit']);
  if (r.postponements > 0) {
    out.push(['postponed', `Postponed ${r.postponements}&times;`]);
  }
  if (r.sale_type && /tax/i.test(r.sale_type)) out.push(['', 'Tax sale']);
  return out.map(([c, t]) => `<span class="chip ${c}">${t}</span>`).join('');
}

function card(r) {
  const beds = r.bedrooms ?? '&mdash;';
  const baths = r.bathrooms ?? '&mdash;';
  const sqft = r.livable_sqft ? Number(r.livable_sqft).toLocaleString('en-US') : '&mdash;';
  const bid = money(r.minimum_bid);
  const debt = money(r.debt_amount);
  const pct = (r.minimum_bid && r.market_value)
    ? ` <span style="color:var(--ink-3)">(${Math.round(r.minimum_bid / r.market_value * 100)}% of value)</span>` : '';
  const station = r.nearest_station
    ? `${r.miles_to_station} mi to ${r.nearest_station} <span style="color:var(--ink-3)">(${r.station_line})</span>` : '';

  return `<article class="card">
    ${photo(r)}
    <div class="card-head">
      <h3 class="address">${r.address.replace(/ PHILADELPHIA PA \\d+$/, '')}</h3>
      <div class="sub">${r.zip_code || ''} &middot; Ward ${String(r.ward || '').replace(/(ST|ND|RD|TH)$/i, '') || '&mdash;'} &middot; ${r.property_type || ''}${r.year_built ? ' &middot; built ' + r.year_built : ''}</div>
      <div class="chips">${chips(r)}</div>
    </div>

    <div class="figures">
      <div class="figure"><span class="label">Assessed</span><span class="value">${money(r.market_value) || '&mdash;'}</span></div>
      <div class="figure"><span class="label">Beds / baths</span><span class="value">${beds} / ${baths}</span></div>
      <div class="figure"><span class="label">Livable</span><span class="value">${sqft}<span style="font-size:11px;color:var(--ink-3)"> sqft</span></span></div>
    </div>

    <div style="display:flex;flex-direction:column;gap:5px">
      <div class="bid-line"><span class="k">Minimum bid</span><span class="v accent">${bid || 'Not yet posted'}${pct}</span></div>
      <div class="bid-line"><span class="k">Debt on judgment</span><span class="v">${debt || '&mdash;'}</span></div>
    </div>

    <div class="geo">
      <span>${r.miles_to_city_hall != null ? r.miles_to_city_hall + ' mi from City Hall' : 'Location unknown'}</span>
      ${station ? `<span>${station}</span>` : ''}
    </div>

    <div class="card-foot">
      <a href="${r.detail_url}" target="_blank" rel="noopener">Official docket &rarr;</a>
      ${r.lat ? `<a href="https://www.google.com/maps/search/?api=1&query=${r.lat},${r.lon}" target="_blank" rel="noopener">Map &rarr;</a>` : ''}
      ${r.lat ? `<a href="${streetViewLink(r)}" target="_blank" rel="noopener">Street View &rarr;</a>` : ''}
      ${r.realtor_url ? `<a href="${r.realtor_url}" target="_blank" rel="noopener">Realtor.com &rarr;</a>` : ''}
    </div>
  </article>`;
}

function render() {
  const rows = sortRows(listings.filter(passes));
  const root = document.getElementById('groups');
  document.getElementById('count-note').textContent =
    `${rows.length} of ${listings.length} shown`;

  if (!rows.length) {
    root.innerHTML = `<div class="empty">No upcoming sales match this filter.
      Try widening the price band in <code>config.json</code> and re-running the scraper.</div>`;
    return;
  }

  // Group by auction date when sorting by date; otherwise show one flat list.
  if (order !== 'date') {
    root.innerHTML = `<div class="group"><div class="cards">${rows.map(card).join('')}</div></div>`;
    return;
  }

  const groups = [];
  for (const r of rows) {
    const last = groups[groups.length - 1];
    if (last && last.date === r.sale_date) last.rows.push(r);
    else groups.push({ date: r.sale_date, iso: r.sale_date_iso, days: r.days_until_sale, rows: [r] });
  }

  root.innerHTML = groups.map(g => {
    const cls = g.days <= 14 ? 'soon' : g.days <= 45 ? 'near' : 'far';
    const when = g.days === 0 ? 'today' : g.days === 1 ? 'tomorrow' : `in ${g.days} days`;
    // Sale dates arrive as M/D/YYYY, which Date() won't parse reliably; the
    // scraper also emits an ISO form, so use that.
    const pretty = g.iso
      ? new Date(g.iso + 'T12:00:00').toLocaleDateString('en-US',
          { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
      : g.date;
    return `<section class="group">
      <div class="group-head">
        <span class="group-date">${pretty}</span>
        <span class="countdown ${cls}">${when}</span>
        <span class="group-count">${g.rows.length} propert${g.rows.length === 1 ? 'y' : 'ies'}</span>
      </div>
      <div class="cards">${g.rows.map(card).join('')}</div>
    </section>`;
  }).join('');
}

for (const group of document.querySelectorAll('.segmented')) {
  group.addEventListener('click', e => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const key = group.dataset.key;
    if (key === 'place') place = btn.dataset.value; else order = btn.dataset.value;
    for (const b of group.querySelectorAll('button')) {
      b.setAttribute('aria-pressed', String(b === btn));
    }
    render();
  });
}

render();
"""


def build():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    listings = payload["listings"]
    stats = payload["stats"]
    crit = payload["criteria"]

    # Sale dates are the natural unit here: sales cluster on monthly auction days.
    upcoming = [r for r in listings if r.get("days_until_sale") is not None]
    soonest = min((r["days_until_sale"] for r in upcoming), default=None)
    next_date = next((r["sale_date"] for r in upcoming
                      if r["days_until_sale"] == soonest), "&mdash;")
    fresh = stats["new_since_last_run"]
    center = sum(1 for r in listings if r.get("is_center_city"))
    transit = sum(1 for r in listings
                  if r.get("is_transit_walkable") and not r.get("is_center_city"))

    # Build this by hand: the %-d / %-I no-padding flags are glibc-only and
    # blow up on Windows.
    g = datetime.fromisoformat(payload["generated_at"])
    hour = g.hour % 12 or 12
    generated_text = (f"{g.strftime('%B')} {g.day}, {g.year} at "
                      f"{hour}:{g.minute:02d} {g.strftime('%p').lower()}")

    def stat(label, value, unit="", cls=""):
        u = f'<span class="unit">{unit}</span>' if unit else ""
        return (f'<div class="stat {cls}"><dt>{label}</dt>'
                f'<dd>{value}{u}</dd></div>')

    summary = "".join([
        stat("Matching sales", stats["upcoming_sales"]),
        stat("Next auction", next_date, f" &middot; {soonest}d" if soonest is not None else "",
             "is-urgent" if soonest is not None and soonest <= 14 else ""),
        stat("New this run", fresh, "", "is-fresh" if fresh else ""),
        stat("Center City", center),
        stat("Near transit", transit),
    ])

    # The docket is a public legal notice, but the owner names attached to it
    # are people in financial distress. They are not needed to evaluate a house,
    # so they never reach a published page.
    public = dict(payload)
    public["listings"] = [{k: v for k, v in r.items() if k != "owner"}
                          for r in listings]
    data_json = json.dumps(public).replace("</", "<\\/")

    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    sv_key = (cfg.get("google_streetview_api_key") or "").strip()

    head = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Newsreader:opsz,wght@6..72,500;6..72,600&family=Public+Sans:wght@400;500;600;700&display=swap">
<style>""" + CSS + "</style>"

    body = f"""<div class="wrap">
  <header class="masthead">
    <p class="eyebrow">Sheriff's Office docket &middot; Philadelphia County</p>
    <h1>Sheriff Sale Watch</h1>
    <p class="standfirst">
      Homes on the Philadelphia sheriff sale docket with
      {crit['min_bedrooms']}+ bedrooms and a city-assessed value between
      ${crit['market_value_min']:,} and ${crit['market_value_max']:,},
      ranked by how soon they go to auction.
    </p>
  </header>

  <dl class="summary">{summary}</dl>

  <details class="howto">
    <summary>How to bid on one of these
      <span class="hint">Deposit is due before the auction opens</span>
    </summary>
    <div class="howto-body">
      <ol class="steps">
        <li><span><span class="t">Register with Bid4Assets</span>
          <span class="d">Philadelphia runs its sheriff sales through Bid4Assets,
          not in a courtroom. Create an account and complete registration ahead of
          the sale date. Bidders must be 18 or older.</span></span></li>

        <li><span><span class="t">Post the bidding deposit</span>
          <span class="d">$10,000 plus a $35 non-refundable processing fee, and it
          must clear <span class="deadline">before the auction opens</span>.
          One deposit qualifies you for every property selling that day, so you do
          not pay per house. Losing bidders are refunded within about ten business
          days.</span></span></li>

        <li><span><span class="t">Do your diligence first &mdash; this is the step that costs people money</span>
          <span class="d">Properties sell <strong>as is</strong>, with no warranty and
          usually no interior inspection. Some liens and mortgages survive the sale
          rather than being cleared by the court's distribution, and the property may
          still be occupied. Order a title search before you bid, not after.</span></span></li>

        <li><span><span class="t">Bid on the auction date</span>
          <span class="d">Bidding runs online. The minimum bid shown on each card is
          the opening figure only &mdash; set your own ceiling in advance and hold to
          it.</span></span></li>

        <li><span><span class="t">If you win, pay the down payment immediately</span>
          <span class="d">10% of the purchase price plus a 1.5% buyer's premium, due
          <span class="deadline">close of the next business day</span>.</span></span></li>

        <li><span><span class="t">Settle the balance</span>
          <span class="d">The remaining 90% plus the $35 fee is due
          <span class="deadline">5:00 PM ET on the 15th calendar day</span>
          after the auction.</span></span></li>

        <li><span><span class="t">Take the deed</span>
          <span class="d">The Sheriff's Deed is issued and recorded, and you become
          the owner of record. Getting <em>possession</em> can be a separate matter if
          someone is living there.</span></span></li>
      </ol>

      <p class="howto-note" style="margin:0">
        <strong>Miss a deadline and you lose the deposit.</strong> Failure to meet the
        conditions of sale forfeits your down payment and can bar you from future
        Philadelphia sheriff sales. Figures above are the mortgage foreclosure terms,
        which cover most listings here; tax sales run on slightly different terms.
        This is a summary &mdash; read the full conditions of sale before you bid.
      </p>

      <div class="howto-links">
        <a href="https://phillysheriff.com/philadelphia-county-mortgage-foreclosure-conditions-of-sale/" target="_blank" rel="noopener">Mortgage foreclosure conditions of sale &rarr;</a>
        <a href="https://www.bid4assets.com/philaforeclosures" target="_blank" rel="noopener">Bid4Assets auction portal &rarr;</a>
        <a href="https://phillysheriff.com/property-listing/" target="_blank" rel="noopener">Sheriff's Office bidding info &rarr;</a>
      </div>
    </div>
  </details>

  <div class="controls">
    <label class="field">
      <span>Location</span>
      <div class="segmented" data-key="place">
        <button data-value="all" aria-pressed="true">All</button>
        <button data-value="transit" aria-pressed="false">Center or transit</button>
        <button data-value="center" aria-pressed="false">Center City only</button>
      </div>
    </label>
    <label class="field">
      <span>Sort by</span>
      <div class="segmented" data-key="order">
        <button data-value="date" aria-pressed="true">Sale date</button>
        <button data-value="value" aria-pressed="false">Value</button>
        <button data-value="bid" aria-pressed="false">Minimum bid</button>
        <button data-value="close" aria-pressed="false">Closest in</button>
      </div>
    </label>
    <span class="count-note" id="count-note"></span>
  </div>

  <div class="groups" id="groups"></div>

  <footer>
    <p style="margin:0">
      <strong>Read the numbers carefully.</strong> Assessed value is the City's OPA
      figure, not a listing price, and it usually runs below resale value.
      The minimum bid is an opening figure, not a purchase price &mdash;
      bidding routinely closes far above it, and the winner takes the property
      subject to any surviving liens.
    </p>
    <p style="margin:0">
      <strong>Postponements are normal.</strong> A property marked postponed has
      already been pulled from the calendar at least once and may move again.
      Confirm every sale against the
      <a href="https://salesweb.civilview.com/Sales/SalesSearch?countyId=60" target="_blank" rel="noopener">official docket</a>
      before you act on it.
    </p>
    <p style="margin:0">
      Docket of {stats['docket_size']:,} open sales &middot;
      {stats['criteria_matches']} matched your criteria &middot;
      {stats['upcoming_sales']} still upcoming.
      Data pulled {generated_text}
      from the Philadelphia Sheriff's Office and the City property database.
    </p>
  </footer>
</div>
"""

    def script(photo_mode):
        js = (JS.replace("__DATA__", data_json)
                .replace("__PHOTO_MODE__", photo_mode)
                .replace("__SV_KEY__", sv_key if photo_mode == "streetview" else ""))
        return f"<script>{js}</script>"

    # 1. Artifact fragment. The Artifact CSP allows no external images at all,
    #    so Street View can only ever be a link here.
    OUT.write_text(
        f"<title>Philadelphia Sheriff Sale Watch</title>\n{head}\n{body}\n{script('links')}\n",
        encoding="utf-8",
    )

    # 2. Standalone page for GitHub Pages: full document, viewport meta for
    #    phones, and real Street View thumbnails when a key is configured.
    pages_dir = ROOT / "docs"
    pages_dir.mkdir(exist_ok=True)
    mode = "streetview" if sv_key else "links"
    (pages_dir / "index.html").write_text(
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<meta name=\"color-scheme\" content=\"light dark\">\n"
        "<meta name=\"description\" content=\"Upcoming Philadelphia sheriff sales "
        "filtered to 3+ bedroom homes in a chosen price band.\">\n"
        "<title>Philadelphia Sheriff Sale Watch</title>\n"
        f"{head}\n</head>\n<body>\n{body}\n{script(mode)}\n</body>\n</html>\n",
        encoding="utf-8",
    )

    print(f"Wrote {OUT.name} (artifact) and docs/index.html (GitHub Pages, photos: {mode})")
    print(f"  {len(listings)} listings, owner names excluded from both")


if __name__ == "__main__":
    build()
