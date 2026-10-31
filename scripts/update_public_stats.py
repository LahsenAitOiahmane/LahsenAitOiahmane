"""Fetch only public GitHub counts; no personal profile fields are persisted."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def fetch(path):
    headers = {"User-Agent": "l27sen-profile", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request("https://api.github.com/" + path, headers=headers)
    with urlopen(req, timeout=30) as response:
        return json.load(response)


def update():
    user = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))["github"]
    # This public endpoint cannot enumerate private repositories, even with a token.
    profile = fetch(f"users/{user}")
    repos = []
    page = 1
    while True:
        batch = fetch(f"users/{user}/repos?type=owner&per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    counts = {
        "public_repos": profile["public_repos"],
        "stars": sum(repo["stargazers_count"] for repo in repos),
        "checked_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    destination = ROOT / "data" / "public-github.json"
    destination.parent.mkdir(exist_ok=True)
    # Write only after all API requests succeed; a failed fetch preserves the cache.
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    print(f"Updated public GitHub counts: {counts['public_repos']} repos, {counts['stars']} stars")


if __name__ == "__main__":
    update()
