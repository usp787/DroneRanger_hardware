"""Download recent San Jose wind data from public sources and save it as tidy CSV files.

Sources (all free, no API key):
  iem-1min    ASOS 1-minute data from the Iowa Environmental Mesonet (IEM) archive: 2-minute mean wind and the
              peak 5-second gust of each minute. Only ASOS sites have it; near San Jose that is SJC.
  iem-metar   Hourly METAR reports (plus specials) from IEM for SJC, RHV, NUQ and PAO.
  open-meteo  Hourly gridded reanalysis (Open-Meteo archive API, ERA5 family) at a chosen point,
              default the NU Silicon Valley campus. Use it for a site without a station.

Usage:
  python wind/tools/fetch_wind.py --start 2026-07-01 --end 2026-10-18
  python wind/tools/fetch_wind.py --start 2025-11-01 --end 2025-12-31 --sources iem-1min

Every output CSV has the columns  time_utc, station, speed_ms, dir_deg, gust_ms
(dir_deg = direction the wind blows FROM, degrees true; gust_ms empty when not reported).
"""
import argparse
import datetime as dt
import io
import pathlib
import time

import pandas as pd
import requests

KT = 0.514444  # m/s per knot
UA = {"User-Agent": "DroneRanger-research/0.1 (Northeastern University capstone)"}
REPO = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "reference" / "08_wind_simulation" / "data"
CAMPUS = (37.3377, -121.8898)  # NU Silicon Valley campus; replace with the garden once it is known


def month_chunks(start, end):
    """Yield (chunk_start, chunk_end) dates, at most one calendar month each."""
    s = start
    while s <= end:
        nxt = (s.replace(day=1) + dt.timedelta(days=32)).replace(day=1)
        yield s, min(end, nxt - dt.timedelta(days=1))
        s = nxt


def get(url, params, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=180)
            r.raise_for_status()
            return r
        except requests.RequestException:
            if i == retries - 1:
                raise
            time.sleep(5 * (i + 1))


def fetch_iem_1min(station, start, end):
    frames = []
    for s, e in month_chunks(start, end):
        r = get("https://mesonet.agron.iastate.edu/cgi-bin/request/asos1min.py", {
            "station": station, "vars": ["sknt", "drct", "gust_sknt"],
            "sts": f"{s}T00:00Z", "ets": f"{e + dt.timedelta(days=1)}T00:00Z",
            "sample": "1min", "what": "download", "delim": "comma", "gis": "no"})
        df = pd.read_csv(io.StringIO(r.text), na_values=["M", ""])
        frames.append(df)
        print(f"  iem-1min {station} {s}..{e}: {len(df)} rows")
        time.sleep(1)
    df = pd.concat(frames, ignore_index=True)
    return pd.DataFrame({
        "time_utc": pd.to_datetime(df["valid(UTC)"], utc=True),
        "station": station,
        "speed_ms": df["sknt"] * KT,
        "dir_deg": df["drct"],
        "gust_ms": df["gust_sknt"] * KT,
    }).drop_duplicates("time_utc").sort_values("time_utc")


def fetch_iem_metar(station, start, end):
    e = end + dt.timedelta(days=1)
    r = get("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py", {
        "station": station, "data": ["sknt", "drct", "gust"],
        "year1": start.year, "month1": start.month, "day1": start.day,
        "year2": e.year, "month2": e.month, "day2": e.day,
        "tz": "Etc/UTC", "format": "onlycomma", "latlon": "no", "missing": "M", "trace": "T",
        "direct": "no", "report_type": [3, 4]})
    df = pd.read_csv(io.StringIO(r.text), na_values=["M", ""])
    print(f"  iem-metar {station} {start}..{end}: {len(df)} rows")
    return pd.DataFrame({
        "time_utc": pd.to_datetime(df["valid"], utc=True),
        "station": station,
        "speed_ms": df["sknt"] * KT,
        "dir_deg": df["drct"],
        "gust_ms": df["gust"] * KT,
    }).drop_duplicates("time_utc").sort_values("time_utc")


def fetch_open_meteo(lat, lon, start, end):
    r = get("https://archive-api.open-meteo.com/v1/archive", {
        "latitude": lat, "longitude": lon, "start_date": str(start), "end_date": str(end),
        "hourly": "wind_speed_10m,wind_direction_10m,wind_gusts_10m", "wind_speed_unit": "ms",
        "timezone": "UTC"})
    h = r.json()["hourly"]
    df = pd.DataFrame({
        "time_utc": pd.to_datetime(h["time"], utc=True),
        "station": f"openmeteo_{lat:.4f}_{lon:.4f}",
        "speed_ms": h["wind_speed_10m"],
        "dir_deg": h["wind_direction_10m"],
        "gust_ms": h["wind_gusts_10m"],
    }).dropna(subset=["speed_ms"])
    print(f"  open-meteo {lat},{lon} {start}..{end}: {len(df)} rows (last {df.time_utc.max()})")
    return df


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--end", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--sources", nargs="+", default=["iem-1min", "iem-metar", "open-meteo"])
    ap.add_argument("--stations", nargs="+", default=["SJC", "RHV", "NUQ", "PAO"], help="for iem-metar")
    ap.add_argument("--latlon", nargs=2, type=float, default=CAMPUS, help="for open-meteo")
    ap.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    tag = f"{a.start:%Y%m%d}_{a.end:%Y%m%d}"

    if "iem-1min" in a.sources:
        fetch_iem_1min("SJC", a.start, a.end).to_csv(a.out / f"iem_1min_SJC_{tag}.csv", index=False)
    if "iem-metar" in a.sources:
        for st in a.stations:
            fetch_iem_metar(st, a.start, a.end).to_csv(a.out / f"iem_metar_{st}_{tag}.csv", index=False)
            time.sleep(1)
    if "open-meteo" in a.sources:
        fetch_open_meteo(*a.latlon, a.start, a.end).to_csv(a.out / f"openmeteo_campus_{tag}.csv", index=False)
    print(f"saved to {a.out}")


if __name__ == "__main__":
    main()
