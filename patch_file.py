import sys
import re

file_path = "plugins/llm-application-dev/skills/prompt-engineering-patterns/scripts/optimize-prompt.py"

with open(file_path, "r") as f:
    text = f.read()

# Remove module level import json
text = re.sub(r'import json\nimport time', 'import time', text, count=1)

# Add import json into export_results
old_method = """    def export_results(self, filename: str):
        \"\"\"Export optimization results to JSON.\"\"\"
        with open(filename, 'w') as f:
            json.dump(self.results_history, f, indent=2)"""

new_method = """    def export_results(self, filename: str):
        \"\"\"Export optimization results to JSON.\"\"\"
        import json
        with open(filename, 'w') as f:
            json.dump(self.results_history, f, indent=2)"""

text = text.replace(old_method, new_method)

with open(file_path, "w") as f:
    f.write(text)
