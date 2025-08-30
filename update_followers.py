import requests

USERNAME = "ModuleMaster64"
API_URL = f"https://api.github.com/users/{USERNAME}/followers"
README_PATH = "README.md"

# Fetch followers
response = requests.get(API_URL)
followers = response.json()

# Format Markdown with avatars and links (limit to 5)
follower_md = "\n".join([
    f'[<img src="{user["avatar_url"]}" width="40" height="40" alt="{user["login"]}">](https://github.com/{user["login"]})'
    for user in followers[:5]
])

# Load README and replace section
with open(README_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_tag = "<!--FOLLOWERS_START-->\n"
end_tag = "<!--FOLLOWERS_END-->\n"

try:
    start_index = lines.index(start_tag)
    end_index = lines.index(end_tag)
    new_section = [start_tag, follower_md + "\n", end_tag]
    lines[start_index:end_index + 1] = new_section
except ValueError:
    print("Placeholder tags not found in README.md")

# Save updated README
with open(README_PATH, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("README updated with recent followers.")
