import csv
import json
import re
import time
from collections import OrderedDict, defaultdict
from datetime import datetime
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

MATRIX_PATH = DOCS / "related_work_matrix.csv"
LOG_PATH = DOCS / "literature_sweep_log.json"

QUERIES = [
    ("hidden goals manipulation", "robotics"),
    ("long horizon manipulation partial observability", "robotics"),
    ("task and motion planning partial observability manipulation", "robotics"),
    ("goal occlusion robot manipulation", "robotics"),
    ("disappearing goal planning", "robotics"),
    ("object permanence robot manipulation", "robotics"),
    ("deictic hidden target manipulation", "robotics"),
    ("contact-rich manipulation planning", "robotics"),
    ("long-horizon robot manipulation planning", "robotics"),
    ("visual servoing occluded target", "robotics"),
    ("closed-loop manipulation world model", "robotics"),
    ("robotic manipulation under partial observability", "robotics"),
    ("latent goal robot planning", "robotics"),
    ("manipulation with hidden target states", "robotics"),
    ("robot action model planning hidden state", "robotics"),
    ("embodied reasoning manipulation", "embodied-ai"),
    ("vision language manipulation planning", "embodied-ai"),
    ("robot foundation model manipulation planning", "embodied-ai"),
    ("tactile manipulation hidden object", "robotics"),
    ("sim2real manipulation planning", "robotics"),
    ("task planning under uncertainty robot", "robotics"),
    ("goal-conditioned manipulation", "robotics"),
    ("active perception manipulation", "robotics"),
    ("robot world models manipulation", "robotics"),
    ("long horizon decision making robotics", "robotics"),
    ("planning with unobserved goals robotics", "robotics"),
]


def crossref_query(query, rows=100, cursor="*"):
    url = "https://api.crossref.org/works"
    params = {
        "query.bibliographic": query,
        "rows": rows,
        "cursor": cursor,
        "select": "DOI,title,author,issued,container-title,URL,type,publisher",
    }
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def normalize_title(title):
    return re.sub(r"\s+", " ", title or "").strip().lower()


def year_from_item(item):
    try:
        return item["issued"]["date-parts"][0][0]
    except Exception:
        return ""


def first_text(value):
    if isinstance(value, list) and value:
        return value[0]
    return value or ""


def main():
    seen = OrderedDict()
    stats = defaultdict(int)
    query_log = []

    for query, tag in QUERIES:
        cursor = "*"
        pages = 0
        while len(seen) < 1200 and pages < 3:
            try:
                data = crossref_query(query, rows=100, cursor=cursor)
            except Exception as e:
                query_log.append({"query": query, "tag": tag, "error": str(e), "cursor": cursor})
                break
            items = data.get("message", {}).get("items", [])
            next_cursor = data.get("message", {}).get("next-cursor", "")
            for item in items:
                title = first_text(item.get("title", []))
                if not title:
                    continue
                key = item.get("DOI") or normalize_title(title)
                if key in seen:
                    seen[key]["query_hits"] += 1
                    seen[key]["queries"].add(query)
                    continue
                container = first_text(item.get("container-title", []))
                year = year_from_item(item)
                seen[key] = {
                    "paper_id": len(seen) + 1,
                    "title": title,
                    "year": year,
                    "venue": container,
                    "doi": item.get("DOI", ""),
                    "url": item.get("URL", ""),
                    "type": item.get("type", ""),
                    "publisher": item.get("publisher", ""),
                    "seed_query": query,
                    "tag": tag,
                    "query_hits": 1,
                    "queries": {query},
                }
                stats[tag] += 1
            if not next_cursor or next_cursor == cursor:
                break
            cursor = next_cursor
            pages += 1
            time.sleep(0.2)

    rows = list(seen.values())
    rows.sort(key=lambda r: (r["year"] if isinstance(r["year"], int) else 9999, r["paper_id"]))
    for i, row in enumerate(rows, 1):
        row["paper_id"] = i
        row["queries"] = "; ".join(sorted(row["queries"]))

    with MATRIX_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["paper_id", "title", "year", "venue", "doi", "url", "type", "publisher", "seed_query", "tag", "query_hits", "queries"],
        )
        writer.writeheader()
        writer.writerows(rows)

    with LOG_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "paper_count": len(rows),
                "query_log": query_log,
                "stats": dict(stats),
            },
            f,
            indent=2,
        )

    print(f"wrote {len(rows)} rows to {MATRIX_PATH}")


if __name__ == "__main__":
    main()
