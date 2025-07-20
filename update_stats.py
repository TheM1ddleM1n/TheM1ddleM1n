import requests
import os

# Config
username = "ModuleMaster64"
readme_path = "README.md"
start_marker = "<!-- STATS-START -->"
end_marker = "<!-- STATS-END -->"

# Fetch user data from GitHub API
response = requests.get(f"https://api.github.com/users/{username}")
data = response.json()

# Extract stats
followers = data.get("followers", 0)
public_repos = data.get("public_repos", 0)
public_gists = data.get("public_gists", 0)

# Format your stats block
stats_block = f"""
**📊 GitHub Stats**

- Followers: `{followers}`
- Public Repositories: `{public_repos}`
- Public Gists: `{public_gists}`
"""

# Read your README.md
with open(readme_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace content between markers
before, middle, after = content.partition(start_marker)
_, _, after = after.partition(end_marker)

new_readme = f"{before}{start_marker}\n{stats_block}\n{end_marker}{after}"

# Save README.md
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(new_readme)

print("✅ GitHub stats updated!")
