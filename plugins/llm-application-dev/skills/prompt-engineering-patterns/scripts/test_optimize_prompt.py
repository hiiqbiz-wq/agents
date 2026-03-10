import sys
from unittest.mock import MagicMock

# Mock numpy before importing the module that uses it
mock_np = MagicMock()
sys.modules["numpy"] = mock_np

import importlib.util
import os

# Load the module
script_path = os.path.join(os.path.dirname(__file__), "optimize-prompt.py")
spec = importlib.util.spec_from_file_location("optimize_prompt", script_path)
optimize_prompt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(optimize_prompt)

def test_make_concise_in_order_to():
    optimizer = optimize_prompt.PromptOptimizer(None, [])
    prompt = "in order to succeed, you must work hard."
    expected = "to succeed, you must work hard."
    assert optimizer.make_concise(prompt) == expected

def test_make_concise_due_to_the_fact_that():
    optimizer = optimize_prompt.PromptOptimizer(None, [])
    prompt = "due to the fact that it rained, the game was cancelled."
    expected = "because it rained, the game was cancelled."
    assert optimizer.make_concise(prompt) == expected

def test_make_concise_at_this_point_in_time():
    optimizer = optimize_prompt.PromptOptimizer(None, [])
    prompt = "at this point in time, we are ready."
    expected = "now, we are ready."
    assert optimizer.make_concise(prompt) == expected

def test_make_concise_in_the_event_that():
    optimizer = optimize_prompt.PromptOptimizer(None, [])
    prompt = "in the event that you fail, try again."
    expected = "if you fail, try again."
    assert optimizer.make_concise(prompt) == expected

def test_make_concise_multiple_replacements():
    optimizer = optimize_prompt.PromptOptimizer(None, [])
    prompt = "in order to improve, due to the fact that it is necessary, at this point in time."
    expected = "to improve, because it is necessary, now."
    assert optimizer.make_concise(prompt) == expected

def test_make_concise_no_replacements():
    optimizer = optimize_prompt.PromptOptimizer(None, [])
    prompt = "This prompt is already concise."
    assert optimizer.make_concise(prompt) == prompt
