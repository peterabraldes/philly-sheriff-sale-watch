"""
One command to refresh everything: re-scrape, rebuild the page, and publish.

    python refresh.py           # scrape, rebuild, push if anything changed
    python refresh.py --local   # scrape and rebuild only, don't touch git

Anything new since the previous run is listed in the output and flagged on the
dashboard itself.
"""

import subprocess
import sys

import build_dashboard
import scrape


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()


def main():
    payload = scrape.main()
    build_dashboard.build()

    new = [r for r in payload["listings"] if r.get("is_new")]
    if new:
        print(f"\n{len(new)} new since last run:")
        for r in new:
            value = f"${r['market_value']:,.0f}" if r.get("market_value") else "value unknown"
            print(f"  {r['sale_date']:>10}  {value:>10}  {r['bedrooms']}bd  "
                  f"{r['address']}  [{r['location_label']}]")
    else:
        print("\nNothing new since the last run.")

    if "--local" in sys.argv:
        return

    if not git("status", "--porcelain", "docs"):
        print("\nPublished page unchanged; nothing to push.")
        return

    subprocess.run(["git", "add", "docs"], check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m",
         f"Refresh dashboard: {payload['stats']['upcoming_sales']} upcoming, "
         f"{len(new)} new"],
        check=True,
    )
    subprocess.run(["git", "push", "-q"], check=True)
    print("\nPushed. GitHub Pages usually redeploys within a minute.")


if __name__ == "__main__":
    main()
