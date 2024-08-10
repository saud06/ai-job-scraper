import requests
from datetime import datetime, timezone

def _iso(dt_str):
    # Attempts to normalize various datetime strings
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
    except Exception:
        return None

def fetch_arbeitnow(limit=50):
    """Fetch jobs from Arbeitnow public API.
    Docs: https://www.arbeitnow.com/api/job-board-api
    """
    url = "https://www.arbeitnow.com/api/job-board-api"
    out = []
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
        for item in data.get("data", [])[:limit]:
            out.append({
                "source": "arbeitnow",
                "source_id": str(item.get("slug") or item.get("id") or item.get("url")),
                "title": item.get("title"),
                "company": item.get("company_name"),
                "location": item.get("location"),
                "remote": bool(item.get("remote")),
                "url": item.get("url"),
                "description": item.get("description"),
                "published_at": _iso(item.get("created_at") or item.get("date")),
            })
    except Exception as e:
        print("Arbeitnow fetch error:", e)
    return out

def fetch_remoteok(limit=50):
    """Fetch jobs from RemoteOK public API.
    Docs: https://remoteok.com/api
    """
    url = "https://remoteok.com/api"
    out = []
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        r.raise_for_status()
        data = r.json()
        for item in data:
            # First element may be metadata
            if not isinstance(item, dict) or "id" not in item:
                continue
            out.append({
                "source": "remoteok",
                "source_id": str(item.get("id")),
                "title": item.get("position") or item.get("title"),
                "company": item.get("company"),
                "location": item.get("location"),
                "remote": True,
                "url": item.get("url") or item.get("apply_url"),
                "description": item.get("description") or "",
                "published_at": _iso(item.get("date")),
            })
            if len(out) >= limit:
                break
    except Exception as e:
        print("RemoteOK fetch error:", e)
    return out

def fetch_all(limit_per_source=50):
    jobs = []
    jobs += fetch_arbeitnow(limit=limit_per_source)
    jobs += fetch_remoteok(limit=limit_per_source)
    # Normalize: fill missing fields
    for j in jobs:
        j.setdefault("description", "")
        j.setdefault("location", "N/A")
        j.setdefault("remote", False)
        j.setdefault("published_at", None)
    return jobs