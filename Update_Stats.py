# GitHub-Stats-Auto-Update
# by Volkan S. Kücükbudak
# https://github.com/VolkanSah/
import requests
import os
import re

# GitHub Username - ENTER YOUR USERNAME HERE!
username = "ModuleMaster64"

# Get Token
token = os.getenv("GITHUB_TOKEN")
if not token:
    print("❌ GITHUB_TOKEN not found!")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# API Calls with Error Handling
try:
    user_url = f"https://api.github.com/users/{username}"
    
    print("🔍 Fetching user data...")
    user_response = requests.get(user_url, headers=headers)
    user_response.raise_for_status()
    user_data = user_response.json()
    
    print("🔍 Fetching repo data...")
    repos_data = []
    page = 1
    while True:
        repos_url_page = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        repos_response = requests.get(repos_url_page, headers=headers)
        repos_response.raise_for_status()
        page_data = repos_response.json()
        if not page_data:  # No more repos
            break
        repos_data.extend(page_data)
        page += 1
    
    # Debug: Check type
    print(f"📊 Repositories found: {len(repos_data)}")
    
    # Calculate stats (public repos only)
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos_data)
    total_forks = sum(repo.get("forks_count", 0) for repo in repos_data)
    public_repos = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)
    
    print(f"⭐ Stars: {total_stars}, 🍴 Forks: {total_forks}, 📁 Repos: {public_repos}, 👥 Followers: {followers}")
    
except requests.exceptions.RequestException as e:
    print(f"❌ API Error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Markdown content
stats_md = f"""<!-- STATS-START -->
# 📊 GitHub Stats
- **Public Repositories:** {public_repos}
- **Total Stars:** {total_stars}
- **Total Forks:** {total_forks}
- **Followers:** {followers}

*Last updated automatically via GitHub Actions.*
<!-- STATS-END -->"""

# Load README
try:
    with open("README.md", "r", encoding="utf-8") as f:
        readme_content = f.read()
except FileNotFoundError:
    print("❌ README.md not found!")
    exit(1)

# Replace or insert block
pattern = r"<!-- STATS-START -->.*?<!-- STATS-END -->"
if re.search(pattern, readme_content, re.DOTALL):
    new_readme = re.sub(pattern, stats_md, readme_content, flags=re.DOTALL)
    print("✅ Stats section in README.md updated.")
else:
    new_readme = readme_content.strip() + "\n\n" + stats_md
    print("✅ Stats section added to README.md.")

# Save
with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)

print("🎉 Done!")
