import requests
import os
import json
import logging

# Setup
logging.basicConfig(level=logging.INFO)
USERNAME = "TheM1ddleM1n"
TOKEN = os.getenv("GH_FOLLOW_TOKEN")
API_URL = f"https://api.github.com/users/{USERNAME}/followers?per_page=100"
README_PATH = "README.md"
DATA_PATH = "followers.json"
START_TAG = "<!-- FOLLOWERS_START -->"
END_TAG = "<!-- FOLLOWERS_END -->"

def fetch_followers():
    headers = {"Authorization": f"token {TOKEN}"}
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    return response.json()

def load_previous_followers():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_followers(followers):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(followers, f, indent=2)

def find_new_followers(current, previous):
    previous_usernames = [f["login"] for f in previous]
    return [f for f in current if f["login"] not in previous_usernames][:5]

def generate_table(followers):
    table = "| Avatar | Username | Profile |\n|--------|----------|---------|\n"
    for f in followers:
        avatar_md = f"<img src='{f['avatar_url']}' width='24' height='24' />"
        table += f"| {avatar_md} | {f['login']} | [Link]({f['html_url']}) |\n"
    return table.strip()

def update_readme(table):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    start = content.find(START_TAG)
    end = content.find(END_TAG)

    if start == -1 or end == -1:
        logging.warning("Placeholder tags not found.")
        return

    new_content = (
        content[:start + len(START_TAG)] + "\n" +
        table + "\n" +
        content[end:]
    )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    if not TOKEN:
        logging.error("GH_FOLLOW_TOKEN not set.")
        return

    current_followers = fetch_followers()
    previous_followers = load_previous_followers()
    new_followers = find_new_followers(current_followers, previous_followers)

    if new_followers:
        table = generate_table(new_followers)
        update_readme(table)
        logging.info("README updated with new followers.")
    else:
        logging.info("No new followers found.")

    save_followers(current_followers)

if __name__ == "__main__":
    main()
