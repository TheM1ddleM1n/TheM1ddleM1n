import requests, json, os
from datetime import datetime

USERNAME = "ModuleMaster64"  # ← Your GitHub username
README_PATH = "README.md"
FOLLOWERS_FILE = "followers.json"
RECENT_FILE = "recent_followers.json"

def fetch_followers():
    url = f"https://api.github.com/users/{USERNAME}/followers"
    followers = []
    page = 1
    while True:
        res = requests.get(url + f"?page={page}&per_page=100")
        data = res.json()
        if not data:
            break
        for f in data:
            followers.append({
                "login": f["login"],
                "avatar_url": f["avatar_url"],
                "html_url": f["html_url"]
            })
        page += 1
    return followers

def enrich_user(user):
    res = requests.get(f"https://api.github.com/users/{user['login']}")
    data = res.json()
    user["bio"] = data.get("bio", "")
    return user

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def update_readme(recent):
    section = "\n".join([
        f'<a href="{u["html_url"]}"><img src="{u["avatar_url"]}" width="40" title="{u["login"]}"/></a> {u["login"]} — {u.get("bio", "")}'
        for u in recent[:5]
    ])
    with open(README_PATH, "r") as f:
        content = f.read()

    updated = content.split("<!-- FOLLOWERS_START -->")[0] + \
              "<!-- FOLLOWERS_START -->\n" + section + "\n<!-- FOLLOWERS_END -->"

    with open(README_PATH, "w") as f:
        f.write(updated)

def main():
    current = fetch_followers()
    previous = load_json(FOLLOWERS_FILE)
    recent = load_json(RECENT_FILE)

    prev_usernames = {u["login"] for u in previous}
    new_users = [u for u in current if u["login"] not in prev_usernames]

    timestamp = datetime.utcnow().isoformat()
    for user in new_users:
        enriched = enrich_user(user)
        enriched["time"] = timestamp
        recent.insert(0, enriched)

    save_json(FOLLOWERS_FILE, current)
    save_json(RECENT_FILE, recent[:20])
    update_readme(recent)

if __name__ == "__main__":
    main()
