"""Test package for TrackARuntime.

This file ensures `python -m unittest discover tests` can import the
project modules using absolute imports (`m1_m2.*`, `m3.*`, `m4.*`).
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
