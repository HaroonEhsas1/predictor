"""Dynamic threshold manager for adaptive trading system.

Creates or loads `config/thresholds.yml`, allowing run-time updates of
min_confidence / min_margin without changing code.  When the file does
not exist it is initialised with safe defaults.
"""

from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Dict, Any

# Where to store the file
CONFIG_DIR = Path(__file__).parent / "config"
CONFIG_DIR.mkdir(exist_ok=True)
THRESH_FILE = CONFIG_DIR / "thresholds.yml"

# Sensible bootstrap defaults (can be overwritten after first day)
_DEFAULTS: Dict[str, Any] = {
    "min_confidence": 0.65,  # calibrated probability
    "min_margin": 0.015,    # absolute |p_up - p_down|
    "volatility_window": 20,
}


def _write_defaults() -> None:
    """Create file with default thresholds."""
    with THRESH_FILE.open("w", encoding="utf-8") as fp:
        yaml.safe_dump(_DEFAULTS, fp)


def load_thresholds() -> Dict[str, Any]:
    """Return current thresholds; create defaults if missing."""
    if not THRESH_FILE.exists():
        _write_defaults()
    with THRESH_FILE.open("r", encoding="utf-8") as fp:
        data: Dict[str, Any] = yaml.safe_load(fp) or {}
    # Ensure all default keys present
    patched = {**_DEFAULTS, **data}
    if patched != data:
        with THRESH_FILE.open("w", encoding="utf-8") as fp:
            yaml.safe_dump(patched, fp)
    return patched


def update_thresholds(**kwargs) -> None:
    """Update one or more thresholds and save to disk."""
    data = load_thresholds()
    data.update({k: v for k, v in kwargs.items() if v is not None})
    with THRESH_FILE.open("w", encoding="utf-8") as fp:
        yaml.safe_dump(data, fp)
