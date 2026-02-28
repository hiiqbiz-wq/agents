import pytest
import sys
import os

# Add the scripts directory to sys.path so we can import the module
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts'))
sys.path.insert(0, script_dir)
import importlib.util

spec = importlib.util.spec_from_file_location("optimize_prompt", os.path.join(script_dir, "optimize-prompt.py"))
optimize_prompt = importlib.util.module_from_spec(spec)
sys.modules["optimize_prompt"] = optimize_prompt
spec.loader.exec_module(optimize_prompt)

PromptOptimizer = optimize_prompt.PromptOptimizer

@pytest.fixture
def optimizer():
    # Pass None for llm_client and test_suite since they aren't needed for calculate_accuracy
    return PromptOptimizer(llm_client=None, test_suite=[])

def test_calculate_accuracy_exact_match(optimizer):
    """Test that exact matches, ignoring case and whitespace, return 1.0."""
    assert optimizer.calculate_accuracy("Positive", "Positive") == 1.0
    assert optimizer.calculate_accuracy("positive", "Positive") == 1.0
    assert optimizer.calculate_accuracy("  Positive  ", "Positive") == 1.0
    assert optimizer.calculate_accuracy("Negative", "negative") == 1.0

def test_calculate_accuracy_partial_match(optimizer):
    """Test that partial matches calculate word overlap correctly."""
    # response_words: {'the', 'movie', 'was', 'ok'}
    # expected_words: {'the', 'movie', 'was', 'great'}
    # expected_words length: 4. Overlap: 3. Accuracy: 3 / 4 = 0.75
    assert optimizer.calculate_accuracy("The movie was ok", "The movie was great") == 0.75

    # Word order shouldn't matter for this implementation
    assert optimizer.calculate_accuracy("great was movie the", "the movie was great") == 1.0

def test_calculate_accuracy_no_match(optimizer):
    """Test that no matching words return 0.0."""
    assert optimizer.calculate_accuracy("Positive", "Negative") == 0.0
    assert optimizer.calculate_accuracy("Completely different response", "Not a single word matches") == 0.0

def test_calculate_accuracy_empty_strings(optimizer):
    """Test edge cases with empty strings."""
    # Both empty strings
    assert optimizer.calculate_accuracy("", "") == 1.0

    # Response empty, expected not empty
    assert optimizer.calculate_accuracy("", "Positive") == 0.0

    # Response not empty, expected empty
    assert optimizer.calculate_accuracy("Positive", "") == 0.0

    # Both whitespace only
    assert optimizer.calculate_accuracy("   ", "\t\n") == 1.0

def test_calculate_accuracy_whitespace_and_punctuation(optimizer):
    """Test handling of whitespace."""
    # Newlines and tabs
    assert optimizer.calculate_accuracy(" \n\t text \n", "text") == 1.0
    assert optimizer.calculate_accuracy("text with \n spaces", "text with spaces") == 1.0
