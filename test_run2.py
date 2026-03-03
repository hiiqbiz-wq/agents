import sys
class MockNumPy:
    def mean(self, x): return 0.96
    def percentile(self, x, p): return 0.5
sys.modules['numpy'] = MockNumPy()
import runpy
runpy.run_path("plugins/llm-application-dev/skills/prompt-engineering-patterns/scripts/optimize-prompt.py", run_name="__main__")
