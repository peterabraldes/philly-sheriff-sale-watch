"""
Philadelphia sheriff sale scraper.

Pipeline:
  1. Pull the open sheriff sale docket from the county's CivilView portal.
  2. Bulk-enrich every parcel from the City of Philadelphia OPA property API
     (bedrooms, assessed market value, coordinates) using the OPA number that
     the docket conveniently publishes.
  3. Filter down to what you actually care about, from config.json.
  4. Only then fetch the per-property detail pages, which is where the sale
     date and minimum bid live. Filtering first keeps this from being ~1,500
     requests against a county server.
  5. Score each survivor on distance to City Hall and to SEPTA rail.
  6. Write data/listings.json and flag anything new since the last run.

Run:  python scrape.py
"""

import json
import math
import re
import sys
import time
from datetime import date, datetime
from html import unescape
from pathlib import Path

import requests

from septa_stations import CITY_HALL, STATIONS

ROOT = Path(__file__).parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

COUNTY_ID = 60  # Philadelphia County, PA on the CivilView portal
BASE = "https://salesweb.civilview.com"
CARTO = "https://phl.carto.com/api/v2/sql"

# A descriptive agent so the county can see who is hitting them and why.
USER_AGENT = (
    "SheriffSaleDashboard/1.0 (personal property-search tool; "
    "low-volume, cached, rate-limited)"
)


# --------------------------------------------------------------------------
# Step 1: the sheriff sale docket
# --------------------------------------------------------------------------

def fetch_docket(session):
    """Return the full list of open sheriff sales as dicts."""
    url = f"{BASE}/Sales/SalesSearch?countyId={COUNTY_ID}"
    resp = session.get(url, timeout=90)
    resp.raise_for_status()

    rows = []
    # Each row: [View Details link] [Book & Writ] [OPA #] [Address] [Plaintiff]
    row_re = re.compile(r"<tr>\s*<td[^>]*>\s*<a href=\"(/Sales/SaleDetails\?PropertyId=(\d+))\".*?</tr>", re.S)
    cell_re = re.compile(r"<td[^>]*>(.*?)</td>", re.S)

    for match in row_re.finditer(resp.text):
        detail_path, property_id = match.group(1), match.group(2)
        cells = [clean(c) for c in cell_re.findall(match.group(0))]
        if len(cells) < 5:
            continue
        rows.append({
            "property_id": property_id,
            "detail_url": BASE + detail_path,
            "book_and_writ": cells[1],
            "opa_number": cells[2],
            "address": cells[3],
            "plaintiff": cells[4],
        })
    return rows


def clean(html_fragment):
    """Strip tags, decode entities, collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", html_fragment)
    text = unescape(unescape(text))          # portal double-encodes some entities
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------------------------------
# Step 2: enrich from the city property database
# --------------------------------------------------------------------------

def fetch_property_data(opa_numbers):
    """Look up bedrooms / value / coordinates for a batch of OPA numbers."""
    found = {}
    numbers = [n for n in opa_numbers if n and n.isdigit()]

    for chunk in chunks(numbers, 400):
        quoted = ",".join(f"'{n}'" for n in chunk)
        query = f"""
            SELECT parcel_number, location, market_value, number_of_bedrooms,
                   number_of_bathrooms, total_livable_area, total_area,
                   year_built, zip_code, zoning, category_code,
                   category_code_description, building_code_description,
                   owner_1, geographic_ward,
                   ST_Y(the_geom) AS lat, ST_X(the_geom) AS lon
            FROM opa_properties_public
            WHERE parcel_number IN ({quoted})
        """
        resp = requests.post(
            CARTO, data={"q": query},
            headers={"User-Agent": USER_AGENT}, timeout=120,
        )
        resp.raise_for_status()
        for row in resp.json().get("rows", []):
            found[row["parcel_number"]] = row

    return found


def chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


# --------------------------------------------------------------------------
# Step 3: filter to the criteria in config.json
# --------------------------------------------------------------------------

def matches_criteria(prop, cfg):
    """Return None if the property qualifies, else a string saying why not."""
    if prop is None:
        return "no city property record"

    value = prop.get("market_value")
    if value is None:
        return "no assessed value"
    if not (cfg["market_value_min"] <= value <= cfg["market_value_max"]):
        return f"value ${value:,.0f} outside range"

    beds = prop.get("number_of_bedrooms")
    if beds is None:
        return "bedroom count unknown"
    if beds < cfg["min_bedrooms"]:
        return f"{beds} bedrooms"

    # The API returns category_code as a string on some rows and a number on
    # others, so normalise before comparing.
    try:
        category = int(prop.get("category_code"))
    except (TypeError, ValueError):
        return "unknown property category"
    if category not in cfg["residential_category_codes"]:
        return f"not residential ({prop.get('category_code_description')})"

    return None


# --------------------------------------------------------------------------
# Step 4: per-property detail (sale date, minimum bid, postponement history)
# --------------------------------------------------------------------------

def fetch_detail(session, listing, cache, delay):
    """Fetch and parse one sale detail page, using the on-disk cache."""
    key = listing["property_id"]
    if key in cache:
        return cache[key]

    time.sleep(delay)
    resp = session.get(listing["detail_url"], timeout=60)
    resp.raise_for_status()
    detail = parse_detail(resp.text)
    cache[key] = detail
    return detail


DETAIL_FIELD_RE = re.compile(
    r'<div class="sale-detail-label">(.*?)</div>\s*'
    r'<div class="sale-detail-value">(.*?)</div>',
    re.S,
)


def parse_detail(html):
    """Pull the labelled fields and the status history off a detail page."""
    body = re.sub(r"(?s)<script.*?</script>", "", html)

    # The summary fields are label/value div pairs, not a table.
    fields = {}
    for raw_label, raw_value in DETAIL_FIELD_RE.findall(body):
        label = clean(raw_label).rstrip(":").strip()
        if label:
            fields[label] = clean(raw_value)

    # The status history below them *is* a table of (status, date) pairs.
    # The first dated entry is the current / next scheduled sale.
    cells = [clean(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", body, re.S)]
    history = []
    for status, when in zip(cells, cells[1:]):
        if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", when) and status and not status.endswith(":"):
            history.append({"status": status, "date": when})

    # Prefer the stated sale date; fall back to the newest status-history entry.
    sale_date = fields.get("Sales Date", "").strip()
    if not sale_date and history:
        sale_date = history[0]["date"]

    return {
        "sheriff_number": fields.get("Sheriff #", ""),
        "court_case": fields.get("Court Case #", ""),
        "sale_date": sale_date,
        "attorney": fields.get("Attorney", ""),
        "ward": fields.get("Ward", ""),
        "debt_amount": parse_money(fields.get("Debt Amount", "")),
        "minimum_bid": parse_money(fields.get("Minimum Bid", "")),
        "sale_type": fields.get("Sale Type", ""),
        "status_history": history,
        "postponements": sum(1 for h in history if "postpon" in h["status"].lower()),
        "current_status": history[0]["status"] if history else "",
    }


def parse_money(text):
    digits = re.sub(r"[^\d.]", "", text or "")
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


# --------------------------------------------------------------------------
# Step 5: location scoring
# --------------------------------------------------------------------------

def miles_between(a_lat, a_lon, b_lat, b_lon):
    """Great-circle distance in miles."""
    radius = 3958.8
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp = p2 - p1
    dl = math.radians(b_lon - a_lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(h))


def score_location(lat, lon, cfg):
    if lat is None or lon is None:
        return {
            "miles_to_city_hall": None, "nearest_station": None,
            "miles_to_station": None, "station_line": None,
            "is_center_city": False, "is_transit_walkable": False,
            "location_label": "Location unknown",
        }

    to_center = miles_between(lat, lon, *CITY_HALL)

    nearest, best = None, float("inf")
    for name, line, s_lat, s_lon in STATIONS:
        d = miles_between(lat, lon, s_lat, s_lon)
        if d < best:
            nearest, best = (name, line), d

    center = to_center <= cfg["center_city_max_miles"]
    walkable = best <= cfg["transit_walk_max_miles"]

    if center:
        label = "Center City"
    elif walkable:
        label = "Transit-accessible"
    else:
        label = "Outside preferences"

    return {
        "miles_to_city_hall": round(to_center, 2),
        "nearest_station": nearest[0],
        "station_line": nearest[1],
        "miles_to_station": round(best, 2),
        "is_center_city": center,
        "is_transit_walkable": walkable,
        "location_label": label,
    }


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def parse_sale_date(text):
    try:
        return datetime.strptime(text, "%m/%d/%Y").date()
    except (ValueError, TypeError):
        return None


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return default
    return default


def main():
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    delay = max(0.25, cfg.get("request_delay_seconds", 0.4))

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    print("Fetching Philadelphia sheriff sale docket...")
    docket = fetch_docket(session)
    if not docket:
        sys.exit("No rows returned from the county portal. The page layout may have changed.")
    print(f"  {len(docket)} open sale records")

    print("Looking up city property records...")
    properties = fetch_property_data([d["opa_number"] for d in docket])
    print(f"  matched {len(properties)} of {len(docket)} parcels")

    candidates, rejected = [], {}
    for row in docket:
        prop = properties.get(row["opa_number"])
        reason = matches_criteria(prop, cfg)
        if reason is None:
            candidates.append((row, prop))
        else:
            rejected[reason.split(" ")[0]] = rejected.get(reason.split(" ")[0], 0) + 1

    print(f"  {len(candidates)} match your criteria "
          f"({cfg['min_bedrooms']}+ beds, "
          f"${cfg['market_value_min']:,}-${cfg['market_value_max']:,})")

    print(f"Fetching sale details for {len(candidates)} properties...")
    cache_path = DATA / "detail_cache.json"
    cache = load_json(cache_path, {})

    results = []
    for i, (row, prop) in enumerate(candidates, 1):
        try:
            detail = fetch_detail(session, row, cache, delay)
        except requests.RequestException as exc:
            print(f"  [{i}/{len(candidates)}] failed {row['address']}: {exc}")
            continue

        sale_date = parse_sale_date(detail["sale_date"])
        if cfg.get("include_only_upcoming_sales", True):
            if sale_date is None or sale_date < date.today():
                continue

        location = score_location(prop.get("lat"), prop.get("lon"), cfg)
        results.append({
            **row,
            **detail,
            "sale_date_iso": sale_date.isoformat() if sale_date else None,
            "days_until_sale": (sale_date - date.today()).days if sale_date else None,
            "market_value": prop.get("market_value"),
            "bedrooms": prop.get("number_of_bedrooms"),
            "bathrooms": prop.get("number_of_bathrooms"),
            "livable_sqft": prop.get("total_livable_area"),
            "lot_sqft": prop.get("total_area"),
            "year_built": prop.get("year_built"),
            "zip_code": prop.get("zip_code"),
            "zoning": prop.get("zoning"),
            "property_type": prop.get("category_code_description"),
            "building_description": prop.get("building_code_description"),
            "owner": prop.get("owner_1"),
            "lat": prop.get("lat"),
            "lon": prop.get("lon"),
            **location,
        })
        if i % 25 == 0:
            print(f"  [{i}/{len(candidates)}]")

    cache_path.write_text(json.dumps(cache), encoding="utf-8")

    # Flag anything that wasn't in the previous run. The very first run has
    # nothing to compare against, so it records a baseline rather than
    # announcing every listing as new.
    seen_path = DATA / "seen.json"
    first_run = not seen_path.exists()
    seen = set(load_json(seen_path, []))
    for item in results:
        item["is_new"] = (not first_run) and item["property_id"] not in seen
    if results:
        seen_path.write_text(
            json.dumps(sorted(seen | {r["property_id"] for r in results})),
            encoding="utf-8",
        )

    results.sort(key=lambda r: (r["days_until_sale"] is None, r["days_until_sale"] or 0))

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "criteria": {
            "market_value_min": cfg["market_value_min"],
            "market_value_max": cfg["market_value_max"],
            "min_bedrooms": cfg["min_bedrooms"],
            "center_city_max_miles": cfg["center_city_max_miles"],
            "transit_walk_max_miles": cfg["transit_walk_max_miles"],
        },
        "stats": {
            "docket_size": len(docket),
            "parcels_matched": len(properties),
            "criteria_matches": len(candidates),
            "upcoming_sales": len(results),
            "new_since_last_run": sum(1 for r in results if r["is_new"]),
        },
        "listings": results,
    }
    (DATA / "listings.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"\n{len(results)} upcoming sales match "
          f"({payload['stats']['new_since_last_run']} new since last run)")
    print(f"Wrote {DATA / 'listings.json'}")
    return payload


if __name__ == "__main__":
    main()
