"""Generate runtime configuration for the Render-hosted static frontend."""

import json
import os
from pathlib import Path


api_base_url = os.environ.get("API_BASE_URL", "").strip().rstrip("/")
if api_base_url and not api_base_url.startswith("https://"):
    raise SystemExit("API_BASE_URL must be an https URL")

Path("config.js").write_text(
    f"window.CAMPUSPULSE_API_BASE = {json.dumps(api_base_url)};\n",
    encoding="utf-8",
)
