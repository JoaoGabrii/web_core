"""Generate the public, static WebCore site for Cloudflare Pages.

No FastAPI, database, credentials or administrative endpoints are deployed.
Run: python3 build_static.py
Cloudflare Pages output directory: dist
"""
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"
HOME = (ROOT / "templates" / "home.html").read_text(encoding="utf-8")
BASE = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")

title_match = re.search(r"{% block title %}(.*?){% endblock %}", HOME, re.S)
content_match = re.search(r"{% block content %}(.*?){% endblock %}", HOME, re.S)
if not title_match or not content_match:
    raise SystemExit("Template structure changed; refusing to publish an incomplete site.")

page = BASE.replace(
    "{% block title %}WebCore — Soluções Digitais{% endblock %}",
    title_match.group(1).strip(),
).replace(
    "{% block content %}{% endblock %}",
    content_match.group(1).strip(),
)
if "{%" in page or "{{" in page:
    raise SystemExit("Unrendered Jinja template directive in generated HTML.")

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
(OUT / "index.html").write_text(page, encoding="utf-8")
shutil.copytree(ROOT / "static", OUT / "static")
(OUT / "_headers").write_text(
    "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: DENY\n"
    "/static/*\n  Cache-Control: public, max-age=3600\n",
    encoding="utf-8",
)
print(f"WebCore public site built: {OUT / 'index.html'}")
