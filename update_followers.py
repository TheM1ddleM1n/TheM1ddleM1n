import os
import requests

username = os.getenv("GH_USERNAME")
token = os.getenv("GH_TOKEN")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

url = f"https://api.github.com/users/{username}/followers"
response = requests.get(url, headers=headers)
followers = response.json()

# Build markdown table with avatars
table = "| Avatar | Username |\n|--------|----------|\n"
for user in followers[:10]:  # Limit to top 10
    avatar_md = f"<img src='{user['avatar_url']}' width='30' height='30'>"
    username_md = f"[{user['login']}](https://github.com/{user['login']})"
    table += f"| {avatar_md} | {username_md} |\n"

# Inject into README
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

start = "<!--ACTION_START_FLAG:github-followers-->"
end = "<!--ACTION_END_FLAG:github-followers-->"
pre = content.split(start)[0] + start + "\n"
post = "\n" + end + content.split(end)[1]
updated = pre + table + post

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated)
