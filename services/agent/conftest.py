"""Make the Agent service importable when pytest starts at repository root."""

from pathlib import Path
import sys


AGENT_SERVICE_DIR = Path(__file__).resolve().parent

if str(AGENT_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_SERVICE_DIR))
