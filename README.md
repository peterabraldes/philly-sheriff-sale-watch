# Philadelphia Sheriff Sale Watch

A small dashboard that watches the Philadelphia sheriff sale docket and surfaces
only the homes worth a second look: 3+ bedrooms, a chosen price band, and a note
on whether each one sits in Center City or within walking distance of SEPTA rail.

**Live dashboard:** see the GitHub Pages link in the repository description.

## Why only Philadelphia

This started as a three-city tool (Phoenix, Philadelphia, Santa Fe). The other
two turned out not to have the data:

- **Phoenix / Maricopa County** publishes a real sheriff sale feed, and it is
  live and updated daily, but it is essentially always empty. Arizona
  foreclosures are *non-judicial trustee sales*, so almost nothing reaches a
  sheriff's auction. The equivalent pipeline is Notice of Trustee Sale filings
  at the County Recorder, which blocks scripted access.
- **Santa Fe County** runs judicial foreclosures sold by court-appointed special
  masters. Notices are published in newspaper legal ads, not online in any
  structured form.

Philadelphia, by contrast, publishes a full docket with an OPA parcel number on
every row, which joins cleanly to the city's open property database. That join is
what makes bedroom and price filtering possible at all.

## How it works

1. `scrape.py` pulls the open docket from the county's CivilView portal
   (~1,500 rows) in a single request.
2. Every parcel is enriched from the City of Philadelphia OPA property API
   (bedrooms, assessed value, coordinates) in a handful of bulk queries.
3. Only the rows that survive your filters get a per-property detail fetch,
   which is where the sale date, minimum bid and postponement history live.
   Filtering first keeps this to a couple of dozen polite requests instead of
   1,500.
4. Each survivor is scored on distance to City Hall and to the nearest SEPTA
   rail station.
5. `build_dashboard.py` renders the results into a self-contained page.

## Usage

```bash
pip install requests
python scrape.py            # refresh the data
python build_dashboard.py   # rebuild the page
```

`scrape.py` writes `data/listings.json` and remembers what it has seen before, so
anything new since your last run is flagged on the dashboard.

## Tuning

Edit `config.json`:

| Setting | What it does |
| --- | --- |
| `market_value_min` / `market_value_max` | Price band, against the city's assessed value |
| `min_bedrooms` | Minimum bedroom count |
| `residential_category_codes` | `1` single family, `2` multi family; add `3` for mixed use |
| `center_city_max_miles` | Radius from City Hall that counts as "center of the city" |
| `transit_walk_max_miles` | Distance to SEPTA rail that counts as walkable |
| `include_only_upcoming_sales` | Hide sales whose date has passed |
| `google_streetview_api_key` | Optional; adds a Street View photo to each card |

Assessed value runs **below** true resale price in Philadelphia, so a
$600k-$1M band is narrower than it sounds. Widening the floor is the fastest way
to see more inventory.

### Photos

The county docket contains no photographs. Without a key, every card links out
to Street View at the property's coordinates. Add a Google **Street View Static
API** key to `config.json` and each card renders a Street View thumbnail
instead. Restrict the key by HTTP referrer to your Pages domain before using it
on a public page.

## Reading the numbers

- **Assessed value** is the city's OPA figure, not a listing price.
- **Minimum bid** is an opening figure. Bidding routinely closes far above it,
  and the winner takes the property subject to any surviving liens.
- **Postponements are normal.** A property postponed five times may well be
  postponed a sixth. Always confirm against the
  [official docket](https://salesweb.civilview.com/Sales/SalesSearch?countyId=60)
  before acting.

This tool is a filter over public records, not advice. Verify everything.

## Data sources

- [Philadelphia County sheriff sale docket](https://salesweb.civilview.com/Sales/SalesSearch?countyId=60) (Tyler Technologies CivilView)
- [City of Philadelphia OPA property assessments](https://phl.carto.com/api/v2/sql) (OpenDataPhilly)

Owner names are deliberately excluded from anything the dashboard publishes.
