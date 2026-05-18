import urllib.request
import urllib.error
import json
import re
from datetime import date, datetime

API_URL = "https://endoflife.date/api/python.json"
README_PATH = "README.md"
TABLE_START = "<!-- PYTHON_VERSIONS_START -->"
TABLE_END = "<!-- PYTHON_VERSIONS_END -->"
MIN_VERSION = (3, 8)


def version_sort_key(entry):
    try:
        return tuple(int(x) for x in entry["cycle"].split("."))
    except Exception:
        return (0,)


def version_tuple(entry):
    try:
        return tuple(int(x) for x in entry["cycle"].split("."))
    except Exception:
        return (0,)


def parse_date(value):
    if not value or isinstance(value, bool):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_entry_dates(entry):
    eol_raw = entry.get("eol")
    if isinstance(eol_raw, bool):
        eol_date = None
        is_eol = eol_raw
    else:
        eol_date = parse_date(eol_raw)
        is_eol = eol_date is not None and eol_date <= date.today()

    support_end = parse_date(entry.get("support"))
    return eol_date, is_eol, support_end


def months_between(from_date, to_date):
    months = (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month)
    if to_date.day < from_date.day:
        months -= 1
    return months


def eol_display(eol_date, is_eol):
    if eol_date is None:
        return "~~EOL~~" if is_eol else "Unknown"
    if is_eol:
        return f"~~{eol_date}~~"
    return str(eol_date)


def months_until_eol_display(eol_date, is_eol):
    if is_eol:
        return "—"
    if eol_date is None:
        return "?"
    months = months_between(date.today(), eol_date)
    return f"{months}mo"


def status_label(is_eol, is_recommended, is_latest, support_end):
    today = date.today()
    if is_eol:
        return "🔴 EOL — stop using this"
    if is_recommended:
        return "✅ **This is recommended**"
    if is_latest:
        return "🟢 Latest"
    security_only = support_end is not None and support_end <= today
    if security_only:
        return "🟠 Security-only — migrate soon"
    return "🟡 Security-only"


def format_row(entry, recommended_cycle, latest_cycle):
    today = date.today()
    cycle = entry.get("cycle", "?")
    released = entry.get("releaseDate", "?")
    eol_date, is_eol, support_end = parse_entry_dates(entry)

    is_recommended = cycle == recommended_cycle
    is_latest = cycle == latest_cycle and cycle != recommended_cycle

    security_only = (
        not is_eol
        and support_end is not None
        and support_end <= today
    )

    label = status_label(is_eol, is_recommended, is_latest, support_end)
    eol_col = eol_display(eol_date, is_eol)
    months_col = months_until_eol_display(eol_date, is_eol)

    return f"| {cycle} | {released} | {eol_col} | {months_col} | {label} |"


def fetch_versions():
    try:
        with urllib.request.urlopen(API_URL) as response:
            data = json.loads(response.read().decode())
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to fetch version data: {e}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse version data: {e}")

    if not isinstance(data, list) or len(data) == 0:
        raise RuntimeError("Version data is empty or malformed")

    return data


def build_table(versions):
    today = date.today()

    all_sorted = sorted(
        (e for e in versions if version_tuple(e) >= MIN_VERSION),
        key=version_sort_key
    )

    if not all_sorted:
        raise RuntimeError("No versions matched the minimum version filter")

    active = [e for e in all_sorted if not parse_entry_dates(e)[1]]

    recommended = active[-2] if len(active) >= 2 else (active[-1] if active else None)
    latest = active[-1] if active else None

    recommended_cycle = recommended["cycle"] if recommended else "?"
    latest_cycle = latest["cycle"] if latest else "?"

    upcoming_eol = next(
        (
            e for e in all_sorted
            if not parse_entry_dates(e)[1]
            and parse_entry_dates(e)[0] is not None
            and months_between(today, parse_entry_dates(e)[0]) <= 12
        ),
        None
    )

    lines = [
        f"> **Recommended: Python {recommended_cycle}** — stable, fully supported, and widely compatible with modern libraries. "
        f"**{latest_cycle}** is available if you want the latest but may have rough edges in some packages. "
        f"And it might not work on all computers",
        "",
        "Each Python version gets ~2 years of full bug-fix releases, then ~3 years of security-only patches, for a total of 5 years of support. After that it's EOL — no more patches, ever.",
        "",
        "| Version | Released | EOL Date | Months Until EOL | Status |",
        "|---------|----------|----------|------------------|--------|",
        *[format_row(e, recommended_cycle, latest_cycle) for e in all_sorted],
        "",
    ]

    if upcoming_eol:
        eol_date, _, _ = parse_entry_dates(upcoming_eol)
        months_left = months_between(today, eol_date)
        lines.append(
            f"If your project still targets {upcoming_eol['cycle']}, start planning a migration — "
            f"it reaches end of life in just {months_left} month{'s' if months_left != 1 else ''}. "
            f"Check your version with:"
        )
    else:
        lines.append("Check your version with:")

    lines += [
        "",
        "```bash",
        "python --version",
        "```",
        "",
        "Full schedule: [devguide.python.org/versions](https://devguide.python.org/versions/) · [endoflife.date/python](https://endoflife.date/python)",
    ]

    return "\n".join(lines)


def update_readme(table_content):
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        raise RuntimeError(f"Failed to read {README_PATH}: {e}")

    pattern = re.compile(
        re.escape(TABLE_START) + r".*?" + re.escape(TABLE_END),
        re.DOTALL
    )

    if not re.search(pattern, content):
        raise ValueError(f"Could not find version markers in {README_PATH}")

    updated = re.sub(pattern, TABLE_START + "\n" + table_content + "\n" + TABLE_END, content)

    try:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(updated)
    except OSError as e:
        raise RuntimeError(f"Failed to write {README_PATH}: {e}")

    print(f"✓ {README_PATH} updated successfully")


def main():
    print("Fetching Python version data...")
    versions = fetch_versions()
    print(f"✓ Retrieved {len(versions)} versions")

    print("Building version table...")
    table = build_table(versions)
    print("✓ Table built")

    print(f"Updating {README_PATH}...")
    update_readme(table)


if __name__ == "__main__":
    main()
