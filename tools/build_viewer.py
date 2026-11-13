"""Embed data/auth_logs.csv into the browser log viewer -> docs/index.html.
The viewer then works offline (double-click the file) and on GitHub Pages.
Run:  python3 tools/build_viewer.py
"""
from pathlib import Path

root = Path(__file__).resolve().parent.parent
csv_text = (root / "data" / "auth_logs.csv").read_text().strip().replace("`", "")
html = (root / "tools" / "viewer_template.html").read_text().replace("__CSV_DATA__", csv_text)
(root / "docs").mkdir(exist_ok=True)
(root / "docs" / "index.html").write_text(html)
print("docs/index.html built")
