import requests
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Constants
USERNAME = "TheM1ddleM1n"
TOKEN = os.getenv("GH_FOLLOW_TOKEN")  # Updated token name
API_URL = f"https://api.github.com/users/{USERNAME}/followers"
README_PATH = "README.md"
START_TAG = "<!-- FOLLOWERS_START -->"
END_TAG = "<!-- FOLLOWERS_END -->"

def fetch_followers(limit=5):
    headers = {"Authorization": f"token {TOKEN}"}
    response = requests.get(API_URL, headers=headers)
    if response.status_code != 200:
        logging.error(f"GitHub API error: {response.status_code}")
        return []
    return response.json()[:limit]

def generate_table(followers):
    table = "| Avatar | Username | Profile |\n|--------|----------|---------|\n"
    for f in followers:
        avatar_md = f"![avatar]({f['avatar_url']}&s=40)"
        table += f"| {avatar_md} | {f['login']} | [Link]({f['html_url']}) |\n"
    return table.strip()

def update_readme(table):
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        start = content.find(START_TAG)
        end = content.find(END_TAG)

        if start == -1 or end == -1:
            logging.warning("Placeholder tags not found in README.")
            return

        new_content = (
            content[:start + len(START_TAG)] + "\n" +
            table + "\n" +
            content[end:]
        )

        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)

        logging.info("README updated successfully.")

    except Exception as e:
        logging.error(f"Error updating README: {e}")

def main():
    if not TOKEN:
        logging.error("GH_FOLLOW_TOKEN environment variable not set.")
        return

    followers = fetch_followers()
    if not followers:
        logging.warning("No followers fetched.")
        return

    table = generate_table(followers)
    update_readme(table)

if __name__ == "__main__":
    main()
