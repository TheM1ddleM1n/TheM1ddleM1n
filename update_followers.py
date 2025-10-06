import requests
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Constants
USERNAME = "TheM1ddleM1n"
TOKEN = os.getenv("GH_FOLLOW_TOKEN")
API_URL = "https://api.github.com/graphql"
README_PATH = "README.md"
START_TAG = "<!-- FOLLOWERS_START -->"
END_TAG = "<!-- FOLLOWERS_END -->"

def fetch_recent_followers(limit=5):
    """Fetch the most recent followers using GitHub GraphQL API."""
    query = f"""
    {{
      user(login: "{USERNAME}") {{
        followers(last: {limit}) {{
          nodes {{
            login
            avatarUrl
            url
          }}
        }}
      }}
    }}
    """
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(API_URL, json={"query": query}, headers=headers)
    if response.status_code != 200:
        logging.error(f"GraphQL API error: {response.status_code}")
        return []
    try:
        return response.json()["data"]["user"]["followers"]["nodes"]
    except Exception as e:
        logging.error(f"Error parsing response: {e}")
        return []

def generate_table(followers):
    """Generate markdown table with avatars, usernames, and profile links."""
    table = "| Avatar | Username | Profile |\n|--------|----------|---------|\n"
    for f in followers:
        avatar_md = f"![avatar]({f['avatarUrl']}&s=40)"
        table += f"| {avatar_md} | {f['login']} | [Link]({f['url']}) |\n"
    return table.strip()

def update_readme(table):
    """Replace the follower section in README with the new table."""
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

    followers = fetch_recent_followers()
    if not followers:
        logging.warning("No followers fetched.")
        return

    table = generate_table(followers)
    update_readme(table)

if __name__ == "__main__":
    main()
