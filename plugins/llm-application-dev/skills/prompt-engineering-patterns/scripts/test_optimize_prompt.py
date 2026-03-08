import pytest
import importlib.util
import sys
import os
from unittest.mock import MagicMock

# Mock numpy before importing the script that depends on it
mock_np = MagicMock()
mock_np.bool_ = bool
sys.modules["numpy"] = mock_np

# Dynamically import the script because of the hyphen in the filename
script_path = os.path.join(os.path.dirname(__file__), 'optimize-prompt.py')
spec = importlib.util.spec_from_file_location("optimize_prompt", script_path)
optimize_prompt = importlib.util.module_from_spec(spec)
sys.modules["optimize_prompt"] = optimize_prompt
spec.loader.exec_module(optimize_prompt)

class MockLLMClient:
    def complete(self, prompt):
        return "mocked response"

@pytest.fixture
def optimizer():
    return optimize_prompt.PromptOptimizer(MockLLMClient(), [])

def test_calculate_accuracy_exact_match(optimizer):
    # Exact match, same case
    assert optimizer.calculate_accuracy("Hello World", "Hello World") == 1.0

    # Exact match, different case
    assert optimizer.calculate_accuracy("hello world", "HELLO WORLD") == 1.0

    # Exact match, trailing/leading whitespace
    assert optimizer.calculate_accuracy("  hello world  ", "hello world") == 1.0
    assert optimizer.calculate_accuracy("hello world", "  hello world  ") == 1.0

def test_calculate_accuracy_partial_match(optimizer):
    # Partial match (word overlap)
    # response has 3 words out of 4 expected -> 3/4 = 0.75
    assert pytest.approx(optimizer.calculate_accuracy("The quick brown", "The quick brown fox"), 0.01) == 0.75

def test_calculate_accuracy_no_match(optimizer):
    # Disjoint match, with one overlapping stop word ("and" = 1/3)
    assert optimizer.calculate_accuracy("Apples and oranges", "Cats and dogs") == 0.3333333333333333

    # Completely disjoint
    assert optimizer.calculate_accuracy("Apples Oranges", "Cats Dogs") == 0.0

def test_calculate_accuracy_empty_expected(optimizer):
    # Expected is empty string
    assert optimizer.calculate_accuracy("Some response", "") == 0.0

def test_calculate_accuracy_empty_response(optimizer):
    # Response is empty string, expected is not
    assert optimizer.calculate_accuracy("", "Expected string") == 0.0

def test_calculate_accuracy_duplicate_words(optimizer):
    # overlap = len(response_words & expected_words) -> set intersection
    # expected: "a a b", set("a", "b"). len = 2.
    # response: "a c c", set("a", "c"). overlap = 1 ("a"). score = 1/2 = 0.5.
    assert optimizer.calculate_accuracy("a c c", "a a b") == 0.5

def test_add_examples(optimizer):
    prompt = "Identify the topic of this article:"
    expected = (
        "Identify the topic of this article:\n\n"
        "Example:\n"
        "Input: Sample input\n"
        "Output: Sample output\n"
    )
    assert optimizer.add_examples(prompt) == expected
