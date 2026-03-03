import sys
from unittest.mock import MagicMock
sys.modules['numpy'] = MagicMock()
import runpy
runpy.run_path("plugins/llm-application-dev/skills/prompt-engineering-patterns/scripts/optimize-prompt.py", run_name="__main__")
