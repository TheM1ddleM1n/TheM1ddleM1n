import json
import random

# Load track list
with open("tracks.json", "r", encoding="utf-8") as f:
    tracks = json.load(f)

# Pick a random track
track = random.choice(tracks)

# Build markdown block
track_block = f"""
## 🎧 Featured Track

[![{track['title']} by {track['artist']}]({track['thumbnail']})]({track['url']})
> *"{track['quote']}"* — {track['version']}

A {track['style']} rework, perfect for {track['vibe']}.  
🔗 [Listen on YouTube]({track['url']})  
🔗 [Stream on SoundCloud]({track['soundcloud']})
"""

# Update README.md between markers
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

start_marker = "<!-- TRACK-START -->"
end_marker = "<!-- TRACK-END -->"

before, _, rest = readme.partition(start_marker)
_, _, after = rest.partition(end_marker)

new_readme = f"{before}{start_marker}\n{track_block}\n{end_marker}{after}"

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)

print("✅ Featured track rotated successfully.")
