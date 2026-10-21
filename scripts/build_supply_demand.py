"""Supply vs. demand-proxy per commune.

Supply  = scheduled stop-visits on a representative weekday (sum of daily_trip_count
          of every stop assigned to the commune).
Demand  = commune population (a PROXY -- real ridership is not open data).
Metric  = scheduled stop-visits per 1,000 residents.

Why here and not in the 15-minute pipeline: the inputs (static GTFS + INSEE
population) only change when SETRAM publishes a new feed, so it runs monthly
with build_static_reference.py.
"""
import json, os
import pandas as pd

def main():
    stops = pd.read_csv("data/gtfs_static/stops_frequency.csv", dtype={"stop_id": str})
    communes = pd.read_csv("data/reference/communes.csv")

    g = stops.groupby("nearest_commune")
    agg = g.agg(
        n_stops=("stop_id", "count"),
        stop_visits=("daily_trip_count", "sum"),
        top_stop_visits=("daily_trip_count", "max"),
    ).reset_index().rename(columns={"nearest_commune": "commune"})
    top_name = (stops.sort_values("daily_trip_count", ascending=False)
                .drop_duplicates("nearest_commune")[["nearest_commune", "stop_name"]]
                .rename(columns={"nearest_commune": "commune", "stop_name": "top_stop_name"}))
    agg = agg.merge(top_name, on="commune", how="left")

    # left join from communes so communes with ZERO stops still appear (supply = 0)
    df = communes.merge(agg, on="commune", how="left")
    for c in ["n_stops", "stop_visits", "top_stop_visits"]:
        df[c] = df[c].fillna(0).astype(int)
    df["top_stop_name"] = df["top_stop_name"].fillna("-")

    df["visits_per_1000"] = (df["stop_visits"] / df["population"] * 1000).round(1)
    # concentration: share of the commune's supply coming from its single busiest stop
    df["top_stop_share"] = (df["top_stop_visits"] / df["stop_visits"].where(df["stop_visits"] > 0)).round(2).fillna(0)
    df["flag_concentrated"] = df["top_stop_share"] >= 0.30   # one stop dominates -> metric suspicious
    df = df.sort_values("visits_per_1000", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1

    cols = ["rank", "commune", "population", "n_stops", "stop_visits",
            "visits_per_1000", "top_stop_name", "top_stop_share", "flag_concentrated"]
    out = df[cols]
    out.to_csv("data/gtfs_static/commune_supply.csv", index=False)
    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/commune_supply.json", "w") as f:
        json.dump({"metric": "scheduled stop-visits per 1,000 residents (weekday)",
                   "communes": out.to_dict("records")}, f, indent=2)
    print(out.to_string(index=False))

if __name__ == "__main__":
    main()
