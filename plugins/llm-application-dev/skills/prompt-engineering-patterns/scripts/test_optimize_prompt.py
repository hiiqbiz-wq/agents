import importlib.util
import os
import sys
import pytest

# Dynamically import the script due to the hyphen in the filename
script_path = os.path.join(os.path.dirname(__file__), 'optimize-prompt.py')
spec = importlib.util.spec_from_file_location('optimize_prompt', script_path)
optimize_prompt = importlib.util.module_from_spec(spec)
sys.modules['optimize_prompt'] = optimize_prompt
spec.loader.exec_module(optimize_prompt)

PromptOptimizer = optimize_prompt.PromptOptimizer


@pytest.fixture
def optimizer():
    class MockLLMClient:
        pass

    # Initialize with mock client and empty test suite
    return PromptOptimizer(MockLLMClient(), [])


def test_make_concise_single_replacement(optimizer):
    """Test replacing a single redundant phrase."""
    prompt = "Please explain this in order to help me understand."
    expected = "Please explain this to help me understand."
    assert optimizer.make_concise(prompt) == expected


def test_make_concise_multiple_replacements(optimizer):
    """Test replacing multiple different redundant phrases in one string."""
    prompt = "due to the fact that it is raining at this point in time, we will stay indoors in the event that lightning strikes."
    expected = "because it is raining now, we will stay indoors if lightning strikes."
    assert optimizer.make_concise(prompt) == expected


def test_make_concise_no_replacements(optimizer):
    """Test that a string without redundant phrases remains unchanged."""
    prompt = "This is already a concise and direct prompt."
    expected = "This is already a concise and direct prompt."
    assert optimizer.make_concise(prompt) == expected


def test_make_concise_empty_string(optimizer):
    """Test behavior with an empty string."""
    assert optimizer.make_concise("") == ""


def test_make_concise_multiple_same_replacements(optimizer):
    """Test replacing multiple instances of the same redundant phrase."""
    prompt = "in order to do A, you must first do B in order to do C."
    expected = "to do A, you must first do B to do C."
    assert optimizer.make_concise(prompt) == expected


def test_make_concise_case_sensitivity(optimizer):
    """
    Test that replacements are currently case-sensitive.
    (If the implementation changes to case-insensitive later, this test will need updating).
    """
    prompt = "In order to start, Due to the fact that we are ready."
    expected = "In order to start, Due to the fact that we are ready."
    assert optimizer.make_concise(prompt) == expected
