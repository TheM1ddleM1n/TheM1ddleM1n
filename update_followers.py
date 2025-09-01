import os
import requests

username = os.getenv("GH_USERNAME")
token = os.getenv("GH_TOKEN")

query = """
{
  user(login: "%s") {
    followers(last: 5) {
      nodes {
        login
        avatarUrl
        url
      }
    }
  }
}
""" % username

headers = {
    "Authorization": f"Bearer %s" % token,
    "Content-Type": "application/json"
}

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query},
    headers=headers
)

if response.status_code != 200:
    print(f"❌ GraphQL request failed with status {response.status_code}")
    print(response.text)
    exit(1)

data = response.json()
followers = data.get("data", {}).get("user", {}).get("followers", {}).get("nodes", [])

if not followers:
    print("⚠️ No followers found or API returned empty list.")
    exit(0)

# Build markdown table with avatars
table = "| Avatar | Username |\n|--------|----------|\n"
for user in followers:
    avatar_md = f"<img src='{user['avatarUrl']}' width='30' height='30'>"
    username_md = f"[{user['login']}]({user['url']})"
    table += f"| {avatar_md} | {username_md} |\n"

# Inject into README
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

start = "<!--ACTION_START_FLAG:github-followers-->"
end = "<!--ACTION_END_FLAG:github-followers-->"
if start not in content or end not in content:
    print("❌ Injection markers not found in README.md")
    exit(1)

pre = content.split(start)[0] + start + "\n"
post = "\n" + end + content.split(end)[1]
updated = pre + table + post

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated)

print("✅ Injected recent followers into README")
