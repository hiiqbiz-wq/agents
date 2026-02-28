import sys
import os
import importlib.util
import pytest

# Load the module under test
current_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(current_dir, "optimize-prompt.py")

spec = importlib.util.spec_from_file_location("optimize_prompt", module_path)
optimize_prompt = importlib.util.module_from_spec(spec)
sys.modules["optimize_prompt"] = optimize_prompt
spec.loader.exec_module(optimize_prompt)

PromptOptimizer = optimize_prompt.PromptOptimizer

@pytest.fixture
def optimizer():
    # Mock LLM client isn't needed for make_concise, but we need to instantiate PromptOptimizer
    class MockLLMClient:
        def complete(self, prompt):
            return "mock"
    return PromptOptimizer(MockLLMClient(), [])

def test_make_concise_single_replacements(optimizer):
    assert optimizer.make_concise("I need this in order to proceed.") == "I need this to proceed."
    assert optimizer.make_concise("It failed due to the fact that it was broken.") == "It failed because it was broken."
    assert optimizer.make_concise("We are ready at this point in time.") == "We are ready now."
    assert optimizer.make_concise("Please call in the event that you need help.") == "Please call if you need help."

def test_make_concise_multiple_replacements(optimizer):
    prompt = "in order to fix this due to the fact that it broke at this point in time"
    expected = "to fix this because it broke now"
    assert optimizer.make_concise(prompt) == expected

def test_make_concise_no_replacements(optimizer):
    prompt = "This is a very simple and straightforward prompt."
    assert optimizer.make_concise(prompt) == prompt

def test_make_concise_empty_string(optimizer):
    assert optimizer.make_concise("") == ""

def test_make_concise_case_sensitivity(optimizer):
    # The current implementation is simple replace(), which is case-sensitive
    # This documents the current behavior.
    prompt = "In order to do this"
    assert optimizer.make_concise(prompt) == prompt

def test_make_concise_partial_match(optimizer):
    # Ensure it doesn't do unintended replacements
    # (Though current implementation might just replace exact string matches)
    prompt = "We are at this point in timekeeper"
    # "at this point in time" gets replaced with "now"
    expected = "We are nowkeeper"
    assert optimizer.make_concise(prompt) == expected
