"""Copy the browser app to Vercel's CDN-served public directory."""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "frontend"
PUBLIC = ROOT / "public"

PUBLIC.mkdir(exist_ok=True)
for filename in ("index.html", "styles.css", "app.js"):
    shutil.copy2(SOURCE / filename, PUBLIC / filename)
