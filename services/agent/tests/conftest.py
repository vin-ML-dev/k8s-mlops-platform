"""Configure the Python import path for Agent tests."""

import sys
from pathlib import Path


AGENT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AGENT_ROOT))
