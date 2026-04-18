"""
Timothy Sykes-style penny stock screener.

Fetches live quote data via Yahoo Finance v8 API when available,
otherwise runs in --demo mode with sample data to illustrate the methodology.

Scoring criteria (max = 5.0 pts):
  1. Price  $0.10 – $5.00        (hard filter, unscored)
  2. Relative volume  >=5x avg   → up to 1.5 pts
  3. Day gain  >=10%             → up to 1.5 pts
  4. Float  <10M shares          →      1.0 pt
  5. Market cap  <$300M          →      1.0 pt

Usage:
  python screener.py           # live mode (requires internet)
  python screener.py --demo    # offline demo with sample data
  python screener.py 5         # return top-5 instead of top-3
"""

import sys
import json
import time
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ---------------------------------------------------------------------------
# Screener configuration
# ---------------------------------------------------------------------------

PRICE_MIN = 0.10
PRICE_MAX = 5.00
REL_VOL_THRESHOLD = 5.0    # 5x average volume = strong catalyst signal
DAY_GAIN_THRESHOLD = 0.10  # 10% up on the day = momentum confirmation
FLOAT_MAX = 10_000_000     # <10M float = can move big on moderate volume
MCAP_MAX = 300_000_000     # <$300M market cap = true small-cap territory

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Seed list – historically active OTC/small-cap tickers
CANDIDATES = [
    "MMAT", "CLOV", "SNDL", "NAKD", "EXPR", "KOSS",
    "BBIG", "ATER", "PROG", "GFAI", "MULN", "FFIE",
    "SIGA", "INDO", "NKLA", "XELA", "ILUS", "BFRI",
    "GOVX", "EDSA", "CNTX", "RZLT", "SEEL", "ATNF",
    "MFON", "CODA", "ENSV", "AREB", "CETX", "VERB",
]

# ---------------------------------------------------------------------------
# Demo data: three classic Sykes-style setups (illustrative, not live prices)
# ---------------------------------------------------------------------------
DEMO_DATA = [
    {
        "ticker": "MMAT",
        "price": 0.9800,
        "day_change_pct": 32.4,
        "rel_vol": 12.3,
        "float_shares": 7_500_000,
        "market_cap": 98_000_000,
        "setup": "Low-float OTC with news catalyst (merger rumor). "
                 "Classic Sykes morning spike – high rvol + tight float.",
    },
    {
        "ticker": "GOVX",
        "price": 2.1500,
        "day_change_pct": 18.7,
        "rel_vol": 8.6,
        "float_shares": 9_200_000,
        "market_cap": 52_000_000,
        "setup": "Biotech catalyst play (FDA fast-track designation). "
                 "Low float, sub-$3, breakout above 52-week resistance.",
    },
    {
        "ticker": "CETX",
        "price": 0.6200,
        "day_change_pct": 14.1,
        "rel_vol": 6.9,
        "float_shares": 5_800_000,
        "market_cap": 31_000_000,
        "setup": "Sector rotation into AI-adjacent micro-cap. "
                 "PR-driven spike with ultra-low float – watch for failed breakout short.",
    },
]


# ---------------------------------------------------------------------------
# Live-data helpers
# ---------------------------------------------------------------------------

def fetch_chart(ticker: str) -> dict | None:
    url = (
        "https://query2.finance.yahoo.com/v8/finance/chart/"
        f"{ticker}?interval=1d&range=25d"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        result = data["chart"]["result"]
        return result[0] if result else None
    except Exception:
        return None


def fetch_info(ticker: str) -> dict:
    url = (
        "https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
        f"{ticker}?modules=defaultKeyStatistics,summaryDetail"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return {}
        data = resp.json()
        summary = data.get("quoteSummary", {}).get("result", [{}])[0]
        stats = summary.get("defaultKeyStatistics", {})
        detail = summary.get("summaryDetail", {})
        float_shares = (stats.get("floatShares") or {}).get("raw", 0)
        market_cap = (detail.get("marketCap") or {}).get("raw", 0)
        return {"floatShares": float_shares, "marketCap": market_cap}
    except Exception:
        return {}


def compute_score(rel_vol: float, day_change: float,
                  float_shares: int, market_cap: int) -> float:
    score = 0.0
    score += min(rel_vol / REL_VOL_THRESHOLD, 1.5)
    score += min(day_change / DAY_GAIN_THRESHOLD, 1.5)
    if 0 < float_shares <= FLOAT_MAX:
        score += 1.0
    elif float_shares > 0:
        score += max(0.0, 1.0 - (float_shares - FLOAT_MAX) / FLOAT_MAX * 0.5)
    if 0 < market_cap <= MCAP_MAX:
        score += 1.0
    return round(score, 3)


def score_ticker_live(ticker: str) -> dict | None:
    chart = fetch_chart(ticker)
    if not chart:
        return None
    closes = [c for c in chart["indicators"]["quote"][0].get("close", []) if c is not None]
    volumes = [v for v in chart["indicators"]["quote"][0].get("volume", []) if v is not None]
    if len(closes) < 2 or len(volumes) < 2:
        return None
    price = closes[-1]
    if not (PRICE_MIN <= price <= PRICE_MAX):
        return None
    today_vol = float(volumes[-1])
    avg_vol = sum(volumes[:-1]) / len(volumes[:-1])
    rel_vol = today_vol / avg_vol if avg_vol > 0 else 0
    day_change = (price - closes[-2]) / closes[-2] if closes[-2] > 0 else 0
    info = fetch_info(ticker)
    float_shares = info.get("floatShares", 0)
    market_cap = info.get("marketCap", 0)
    return {
        "ticker": ticker,
        "price": round(price, 4),
        "day_change_pct": round(day_change * 100, 2),
        "rel_vol": round(rel_vol, 2),
        "float_shares": int(float_shares),
        "market_cap": int(market_cap),
        "score": compute_score(rel_vol, day_change, float_shares, market_cap),
        "setup": "",
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_watchlist(watchlist: list[dict], generated: str) -> None:
    print(f"\n{'='*62}")
    print(f"  TOP {len(watchlist)} SYKES-STYLE PENNY STOCK WATCHLIST")
    print(f"  Generated : {generated}")
    print(f"{'='*62}")
    for rank, s in enumerate(watchlist, 1):
        float_m = s["float_shares"] / 1_000_000
        mcap_m = s["market_cap"] / 1_000_000
        print(f"\n#{rank}  {s['ticker']}")
        print(f"    Price       : ${s['price']:.4f}")
        print(f"    Day change  : {s['day_change_pct']:+.2f}%")
        print(f"    Rel volume  : {s['rel_vol']:.1f}x")
        print(f"    Float       : {float_m:.1f}M shares")
        print(f"    Market cap  : ${mcap_m:.1f}M")
        print(f"    Score       : {s['score']:.2f} / 5.00")
        if s.get("setup"):
            print(f"    Setup note  : {s['setup']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(top_n: int = 3, demo: bool = False) -> None:
    generated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    if demo:
        print("Running in DEMO mode (offline sample data)\n")
        watchlist = []
        for d in DEMO_DATA[:top_n]:
            score = compute_score(
                d["rel_vol"],
                d["day_change_pct"] / 100,
                d["float_shares"],
                d["market_cap"],
            )
            watchlist.append({**d, "score": score})
        watchlist.sort(key=lambda x: x["score"], reverse=True)
    else:
        if not HAS_REQUESTS:
            print("requests is not installed. Run: pip install requests", file=sys.stderr)
            sys.exit(1)
        print(f"Screening {len(CANDIDATES)} tickers with Sykes criteria...\n")
        results = []
        for ticker in CANDIDATES:
            r = score_ticker_live(ticker)
            if r:
                results.append(r)
                print(f"  {ticker:6s}  ${r['price']:>7.4f}  "
                      f"{r['day_change_pct']:+6.1f}%  rvol={r['rel_vol']:5.1f}x  "
                      f"score={r['score']:.2f}")
            time.sleep(0.2)
        results.sort(key=lambda x: x["score"], reverse=True)
        watchlist = results[:top_n]

    print_watchlist(watchlist, generated)

    out = {
        "generated_utc": datetime.utcnow().isoformat(),
        "mode": "demo" if demo else "live",
        "sykes_criteria": {
            "price_range": f"${PRICE_MIN}–${PRICE_MAX}",
            "min_rel_vol": f"{REL_VOL_THRESHOLD}x 20-day avg",
            "min_day_gain": f"{DAY_GAIN_THRESHOLD*100:.0f}%",
            "max_float": f"{FLOAT_MAX/1e6:.0f}M shares",
            "max_market_cap": f"${MCAP_MAX/1e6:.0f}M",
        },
        "watchlist": watchlist,
    }
    with open("watchlist.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults saved to watchlist.json")


if __name__ == "__main__":
    args = sys.argv[1:]
    demo_mode = "--demo" in args
    args = [a for a in args if a != "--demo"]
    n = int(args[0]) if args else 3
    main(top_n=n, demo=demo_mode)
