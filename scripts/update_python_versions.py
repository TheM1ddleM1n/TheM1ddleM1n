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

def classify(entry):
    today = date.today()
    eol = entry.get("eol")
    lts = entry.get("lts", False)

    if isinstance(eol, bool):
        is_eol = eol
    else:
        is_eol = datetime.strptime(eol, "%Y-%m-%d").date() <= today

    if is_eol:
        return "eol"
    if lts:
        return "lts"
    return "active"

def status_label(entry, cycle, is_recommended):
    today = date.today()
    eol = entry.get("eol")

    if isinstance(eol, bool):
        eol_date = None
        is_eol = eol
    else:
        eol_date = datetime.strptime(eol, "%Y-%m-%d").date()
        is_eol = eol_date <= today

    if is_eol:
        return "🔴 EOL — stop using this"

    support_end = entry.get("support")
    if support_end and not isinstance(support_end, bool):
        support_date = datetime.strptime(support_end, "%Y-%m-%d").date()
        security_only = support_date <= today
    else:
        security_only = False

    if is_recommended:
        return "✅ **Recommended**"

    if security_only:
        days_left = (eol_date - today).days if eol_date else None
        if days_left is not None and days_left < 180:
            return "🟠 Security-only — migrate soon"
        return "🟡 Security-only"

    return "🟢 Active support"

def eol_display(entry):
    eol = entry.get("eol")
    if isinstance(eol, bool):
        return "Unknown" if not eol else "~~EOL~~"
    today = date.today()
    eol_date = datetime.strptime(eol, "%Y-%m-%d").date()
    if eol_date <= today:
        return f"~~{eol}~~"
    return eol

def build_table(versions):
    today = date.today()

    active = []
    for entry in versions:
        eol = entry.get("eol")
        if isinstance(eol, bool):
            is_eol = eol
        else:
            is_eol = datetime.strptime(eol, "%Y-%m-%d").date() <= today
        if not is_eol:
            active.append(entry)

    def sort_key(e):
        try:
            return tuple(int(x) for x in e["cycle"].split("."))
        except Exception:
            return (0,)

    active_sorted = sorted(active, key=sort_key)
    all_sorted = sorted(versions, key=sort_key)

    recommended_cycle = active_sorted[-2]["cycle"] if len(active_sorted) >= 2 else (active_sorted[-1]["cycle"] if active_sorted else None)

    lines = []
    lines.append("> **Recommended: Python " + (recommended_cycle or "?") + "** — stable, fully supported, and widely compatible with modern libraries. The latest version is available if you want cutting-edge features but may have rough edges in some packages.")
    lines.append("")
    lines.append("Each Python version gets ~2 years of full bug-fix releases, then ~3 years of security-only patches, totalling 5 years of support.")
    lines.append("")
    lines.append("| Version | Released | EOL Date | Status |")
    lines.append("|---------|----------|----------|--------|")

    for entry in all_sorted:
        cycle = entry.get("cycle", "?")
        released = entry.get("releaseDate", "?")
        eol_str = eol_display(entry)
        label = status_label(entry, cycle, cycle == recommended_cycle)
        lines.append(f"| {cycle} | {released} | {eol_str} | {label} |")

    lines.append("")
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
