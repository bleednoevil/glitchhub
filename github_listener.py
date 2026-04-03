import requests
import time

GITHUB_URL = "https://api.github.com/events"

class GitHubListener:
    def __init__(self, token=None):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "GlitchHub"
        }

        if token:
            self.headers["Authorization"] = f"Bearer {token}"

        self.recent = {}

    def fetch_events(self):
        try:
            r = requests.get(GITHUB_URL, headers=self.headers, timeout=10)
            if r.status_code != 200:
                return []
            return r.json()
        except:
            return []

    def filter_push_events(self, events, dedup_seconds):
        now = time.time()
        results = []

        for e in events:
            if not isinstance(e, dict):
                continue

            if e.get("type") != "PushEvent":
                continue

            repo = e.get("repo", {}).get("name")
            if not repo:
                continue

            if repo in self.recent and now - self.recent[repo] < dedup_seconds:
                continue

            self.recent[repo] = now
            results.append((repo, e))

        return results
