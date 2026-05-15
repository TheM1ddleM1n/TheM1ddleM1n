import urllib.request
import json
import re
from datetime import date, datetime

API_URL = "https://endoflife.date/api/python.json"
README_PATH = "README.md"
TABLE_START = "<!-- PYTHON_VERSIONS_START -->"
TABLE_END = "<!-- PYTHON_VERSIONS_END -->"

def fetch_versions():
    with urllib.request.urlopen(API_URL) as response:
        return json.loads(response.read().decode())

def sort_key(entry):
    try:
        return tuple(int(x) for x in entry["cycle"].split("."))
    except Exception:
        return (0,)

def parse_eol(entry):
    eol = entry.get("eol")
    if isinstance(eol, bool):
        return None, eol
    eol_date = datetime.strptime(eol, "%Y-%m-%d").date()
    return eol_date, eol_date <= date.today()

def parse_support_end(entry):
    support = entry.get("support")
    if not support or isinstance(support, bool):
        return None
    return datetime.strptime(support, "%Y-%m-%d").date()

def eol_display(entry):
    eol_date, is_eol = parse_eol(entry)
    if eol_date is None:
        return "~~EOL~~" if is_eol else "Unknown"
    if is_eol:
        return f"~~{eol_date}~~"
    return str(eol_date)

def status_label(entry, is_recommended, is_latest):
    today = date.today()
    eol_date, is_eol = parse_eol(entry)

    if is_eol:
        return "🔴 EOL — stop using this"

    if is_recommended:
        return "✅ **This is recommended**"

    if is_latest:
        return "🟢 Latest"

    support_end = parse_support_end(entry)
    security_only = support_end is not None and support_end <= today

    if security_only:
        if eol_date is not None and (eol_date - today).days < 180:
            return "🟠 Security-only — migrate soon"
        return "🟡 Security-only"

    return "🟢 Active support"

def build_table(versions):
    today = date.today()
    all_sorted = sorted(versions, key=sort_key)

    active = [e for e in all_sorted if not parse_eol(e)[1]]

    recommended = active[-2] if len(active) >= 2 else (active[-1] if active else None)
    latest = active[-1] if active else None

    recommended_cycle = recommended["cycle"] if recommended else "?"
    latest_cycle = latest["cycle"] if latest else "?"

    eol_entries = [e for e in all_sorted if parse_eol(e)[1]]
    upcoming_eol = next(
        (e for e in all_sorted if not parse_eol(e)[1] and parse_support_end(e) and parse_support_end(e) <= today),
        None
    )

    lines = []
    lines.append(
        f"> **Recommended: Python {recommended_cycle}** — stable, fully supported, and widely compatible with modern libraries. "
        f"**{latest_cycle}** is available if you want the latest but may have rough edges in some packages. "
        f"And it might not work on all computers"
    )
    lines.append("")
    lines.append("Each Python version gets ~2 years of full bug-fix releases, then ~3 years of security-only patches, for a total of 5 years of support. After that it's EOL — no more patches, ever.")
    lines.append("")
    lines.append("| Version | Released | EOL Date | Status |")
    lines.append("|---------|----------|----------|--------|")

    for entry in all_sorted:
        cycle = entry.get("cycle", "?")
        released = entry.get("releaseDate", "?")
        is_recommended = cycle == recommended_cycle
        is_latest = cycle == latest_cycle and cycle != recommended_cycle
        label = status_label(entry, is_recommended, is_latest)
        lines.append(f"| {cycle} | {released} | {eol_display(entry)} | {label} |")

    lines.append("")

    if upcoming_eol:
        eol_date, _ = parse_eol(upcoming_eol)
        days_left = (eol_date - today).days if eol_date else None
        if days_left is not None:
            months_left = round(days_left / 30)
            lines.append(
                f"If your project still targets {upcoming_eol['cycle']}, start planning a migration — "
                f"it reaches end of life in just {months_left} month{'s' if months_left != 1 else ''}. "
                f"Check your version with:"
            )
        else:
            lines.append("Check your version with:")
    else:
        lines.append("Check your version with:")

    lines.append("")
    lines.append("```bash")
    lines.append("python --version")
    lines.append("```")
    lines.append("")
    lines.append("Full schedule: [devguide.python.org/versions](https://devguide.python.org/versions/) · [endoflife.date/python](https://endoflife.date/python)")

    return "\n".join(lines)

def update_readme(table_content):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        re.escape(TABLE_START) + r".*?" + re.escape(TABLE_END),
        re.DOTALL
    )
    replacement = TABLE_START + "\n" + table_content + "\n" + TABLE_END

    if not re.search(pattern, content):
        raise ValueError("Could not find PYTHON_VERSIONS_START/END markers in README.md")

    updated = re.sub(pattern, replacement, content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    print("README.md updated successfully.")

def main():
    versions = fetch_versions()
    table = build_table(versions)
    update_readme(table)

if __name__ == "__main__":
    main()
