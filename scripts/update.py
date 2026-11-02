#!/usr/bin/env python3
"""Met à jour data/news.json et data/scores.json (bibliothèque standard uniquement)."""
import json, os, re, sys, urllib.request
from urllib.parse import quote
from xml.etree import ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data")
UA = {"User-Agent": "HAC-Direct/1.0"}
TOKEN = os.environ.get("FOOTBALL_DATA_TOKEN", "").strip()

# Flux d'actualités. Ajoute ici d'autres flux RSS qui autorisent la lecture automatique.
FEEDS = [
    "https://news.google.com/rss/search?q=" + quote('"Havre Athletic Club" when:7d') + "&hl=fr&gl=FR&ceid=FR:fr",
    "https://news.google.com/rss/search?q=" + quote('"Le Havre" HAC Ligue 1 when:7d') + "&hl=fr&gl=FR&ceid=FR:fr",
]
RELEVANT = re.compile(r"\b(havre|HAC)\b", re.I)


def get(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_rss(xml_bytes):
    out = []
    root = ET.fromstring(xml_bytes)
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        src_el = it.find("source")
        source = (src_el.text or "").strip() if src_el is not None else ""
        if source and title.endswith(" - " + source):
            title = title[: -len(source) - 3].strip()
        try:
            date = parsedate_to_datetime(it.findtext("pubDate")).astimezone(timezone.utc).isoformat()
        except Exception:
            continue
        if title and link and RELEVANT.search(title):
            out.append({"title": title, "source": source or "Web", "url": link, "date": date})
    return out


def build_news():
    items, seen = [], set()
    for f in FEEDS:
        try:
            for n in parse_rss(get(f)):
                key = re.sub(r"\W+", "", n["title"].lower())[:80]
                if key not in seen:
                    seen.add(key)
                    items.append(n)
        except Exception as e:
            print("flux ignoré:", f[:60], e, file=sys.stderr)
    items.sort(key=lambda x: x["date"], reverse=True)
    return items[:80]


def is_hac(team):
    return team.get("tla") == "HAC" or "havre" in (team.get("name") or "").lower()


def build_scores():
    def fd(path):
        return json.loads(get("https://api.football-data.org/v4" + path, {"X-Auth-Token": TOKEN}))

    st = fd("/competitions/FL1/standings")["standings"][0]["table"]
    table = [{"pos": r["position"], "team": r["team"].get("shortName") or r["team"]["name"],
              "hac": is_hac(r["team"]), "pts": r["points"], "p": r["playedGames"], "w": r["won"],
              "d": r["draw"], "l": r["lost"], "gf": r["goalsFor"], "ga": r["goalsAgainst"]} for r in st]
    results, fixtures, live = [], [], None
    for m in fd("/competitions/FL1/matches")["matches"]:
        h, a = m["homeTeam"], m["awayTeam"]
        if not (is_hac(h) or is_hac(a)):
            continue
        row = {"date": m["utcDate"], "home": h.get("shortName") or h["name"], "away": a.get("shortName") or a["name"],
               "hs": m["score"]["fullTime"]["home"], "as": m["score"]["fullTime"]["away"], "hacHome": is_hac(h)}
        if m["status"] == "FINISHED":
            results.append(row)
        elif m["status"] in ("IN_PLAY", "PAUSED", "LIVE"):
            live = {**row, "status": m["status"]}
        else:
            fixtures.append(row)
    results.sort(key=lambda r: r["date"])
    fixtures.sort(key=lambda r: r["date"])
    return {"live": live, "results": results, "fixtures": fixtures, "table": table}


def save_if_changed(name, payload):
    path = os.path.join(DATA, name)
    old = None
    try:
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
    except Exception:
        pass
    if old and {k: v for k, v in old.items() if k != "updatedAt"} == payload:
        return
    payload = {"updatedAt": datetime.now(timezone.utc).isoformat(), **payload}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("mis à jour:", name)


if __name__ == "__main__":
    os.makedirs(DATA, exist_ok=True)
    news = build_news()
    if news:
        save_if_changed("news.json", {"items": news})
    if TOKEN:
        try:
            save_if_changed("scores.json", build_scores())
        except Exception as e:
            print("scores ignorés:", e, file=sys.stderr)
    else:
        print("FOOTBALL_DATA_TOKEN absent : scores non mis à jour", file=sys.stderr)
