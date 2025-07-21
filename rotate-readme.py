# 2. rotate-readme.py content
rotate_script = '''
import json, random

# Load track list
with open("tracks.json", "r") as file:
    tracks = json.load(file)

track = random.choice(tracks)
badge = f"[![Now Playing](https://readme-spotify-github.vercel.app/api/now-playing?artist=GASPxR&song={track['song'].replace(' ', '%20')})]({track['url']})"

# Update README.md
with open("README.md", "r") as file:
    lines = file.readlines()

start, end = -1, -1
for i, line in enumerate(lines):
    if "NOW PLAYING START" in line:
        start = i
    if "NOW PLAYING END" in line:
        end = i

if start != -1 and end != -1:
    lines[start+1:end] = [badge + "\\n"]

with open("README.md", "w") as file:
    file.writelines(lines)
'''

