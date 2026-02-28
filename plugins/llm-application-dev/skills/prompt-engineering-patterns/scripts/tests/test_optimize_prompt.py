import pytest
import os
import sys
import json
from unittest.mock import MagicMock

# Add the parent directory to the path so we can import the script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module as optimize_prompt
import importlib.util
spec = importlib.util.spec_from_file_location("optimize_prompt", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "optimize-prompt.py"))
optimize_prompt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(optimize_prompt)

TestCase = optimize_prompt.TestCase
PromptOptimizer = optimize_prompt.PromptOptimizer

class MockLLMClient:
    def complete(self, prompt):
        return "Positive"

@pytest.fixture
def mock_client():
    return MockLLMClient()

@pytest.fixture
def test_suite():
    return [
        TestCase(input={'text': 'Good'}, expected_output='Positive'),
        TestCase(input={'text': 'Bad'}, expected_output='Negative')
    ]

@pytest.fixture
def optimizer(mock_client, test_suite):
    opt = PromptOptimizer(mock_client, test_suite)
    yield opt
    opt.shutdown()

def test_testcase_initialization():
    tc = TestCase(input={'text': 'Test'}, expected_output='Result', metadata={'source': 'user'})
    assert tc.input == {'text': 'Test'}
    assert tc.expected_output == 'Result'
    assert tc.metadata == {'source': 'user'}

def test_testcase_without_metadata():
    tc = TestCase(input={'text': 'Test'}, expected_output='Result')
    assert tc.input == {'text': 'Test'}
    assert tc.expected_output == 'Result'
    assert tc.metadata is None

def test_calculate_accuracy(optimizer):
    # Exact match
    assert optimizer.calculate_accuracy("Positive", "Positive") == 1.0
    assert optimizer.calculate_accuracy(" positive ", "Positive") == 1.0
    assert optimizer.calculate_accuracy("POSITIVE", "positive") == 1.0

    # No match
    assert optimizer.calculate_accuracy("Negative", "Positive") == 0.0

    # Partial match
    # response words: {'this', 'is', 'positive'}
    # expected words: {'positive'}
    # overlap: {'positive'} (1)
    # len(expected_words): 1
    # score: 1.0
    assert optimizer.calculate_accuracy("This is positive", "Positive") == 1.0

    # response words: {'positive'}
    # expected words: {'this', 'is', 'positive'}
    # overlap: {'positive'} (1)
    # len(expected_words): 3
    # score: 0.333...
    assert abs(optimizer.calculate_accuracy("Positive", "This is positive") - 0.33333333) < 1e-6

    # Empty expected
    assert optimizer.calculate_accuracy("Positive", "") == 0.0

def test_evaluate_prompt(optimizer):
    prompt_template = "Classify: {text}"

    # Mock complete to take exactly 0.01 seconds to avoid timing flakiness if possible,
    # but since time.time() is used, we can just assert the metrics are present.
    metrics = optimizer.evaluate_prompt(prompt_template)

    # Our test_suite has 2 cases: Good (expected Positive), Bad (expected Negative)
    # Our mock_client returns "Positive" for everything.
    # Case 1: text="Good", expected="Positive" -> accuracy = 1.0
    # Case 2: text="Bad", expected="Negative" -> accuracy = 0.0
    # avg_accuracy should be 0.5

    assert 'avg_accuracy' in metrics
    assert metrics['avg_accuracy'] == 0.5

    assert 'avg_latency' in metrics
    assert metrics['avg_latency'] > 0.0

    assert 'p95_latency' in metrics
    assert metrics['p95_latency'] > 0.0

    assert 'avg_tokens' in metrics
    # Prompt tokens: "Classify: Good" -> 2
    # Response tokens: "Positive" -> 1
    # Total = 3
    # Prompt tokens: "Classify: Bad" -> 2
    # Response tokens: "Positive" -> 1
    # Total = 3
    # avg_tokens = 3.0
    assert metrics['avg_tokens'] == 3.0

    assert 'success_rate' in metrics
    assert metrics['success_rate'] == 1.0

def test_evaluate_prompt_with_custom_test_cases(optimizer):
    prompt_template = "Classify: {text}"
    custom_suite = [
        TestCase(input={'text': 'Good'}, expected_output='Positive')
    ]

    metrics = optimizer.evaluate_prompt(prompt_template, test_cases=custom_suite)

    # Mock client returns Positive. Expected is Positive. Accuracy = 1.0
    assert metrics['avg_accuracy'] == 1.0

def test_make_concise(optimizer):
    prompt = "We need this in order to proceed due to the fact that at this point in time in the event that it fails."
    expected = "We need this to proceed because now if it fails."
    assert optimizer.make_concise(prompt) == expected

def test_add_examples(optimizer):
    prompt = "Classify the text."
    result = optimizer.add_examples(prompt)

    assert "Classify the text." in result
    assert "Example:" in result
    assert "Input: Sample input" in result
    assert "Output: Sample output" in result

def test_generate_variations(optimizer):
    prompt = "Classify the text."
    metrics = {'avg_accuracy': 0.5}

    variations = optimizer.generate_variations(prompt, metrics)

    # Should return top 3 variations
    assert len(variations) == 3

    # Check what we generated
    # Variation 1: Add explicit format instruction
    assert "Provide your answer in a clear, concise format." in variations[0]
    # Variation 2: Add step-by-step instruction
    assert "Let's solve this step by step." in variations[1]
    # Variation 3: Add verification step
    assert "Verify your answer before responding." in variations[2]

def test_compare_prompts(optimizer):
    # Mock complete to return 'Positive' for A and B.
    # With 2 test cases (1 Pos, 1 Neg expected), both will score 0.5.
    result = optimizer.compare_prompts("Prompt A: {text}", "Prompt B: {text}")

    assert 'prompt_a_metrics' in result
    assert 'prompt_b_metrics' in result
    assert 'winner' in result
    assert 'improvement' in result

    # Since scores are the same (0.5), 'A' or 'B' will be returned based on `>` check, so it'll return 'B'.
    assert result['improvement'] == 0.0

def test_export_results(optimizer, tmp_path):
    optimizer.results_history = [
        {'iteration': 0, 'prompt': 'test', 'metrics': {'avg_accuracy': 1.0}}
    ]

    export_file = tmp_path / "results.json"
    optimizer.export_results(str(export_file))

    assert export_file.exists()

    with open(export_file, 'r') as f:
        data = json.load(f)

    assert len(data) == 1
    assert data[0]['iteration'] == 0
    assert data[0]['prompt'] == 'test'
    assert data[0]['metrics']['avg_accuracy'] == 1.0

def test_optimize_reaches_target(optimizer):
    # Create an optimizer with a custom mock client and test suite that will easily hit 1.0 accuracy
    custom_suite = [
        TestCase(input={'text': 'Good'}, expected_output='Positive')
    ]
    optimizer.test_suite = custom_suite

    # mock_client always returns 'Positive', so accuracy will be 1.0
    results = optimizer.optimize("Base prompt: {text}", max_iterations=3)

    assert results['best_score'] == 1.0
    # It should break after iteration 0 because target > 0.95
    assert len(results['history']) == 1
    assert results['best_prompt'] == "Base prompt: {text}"

def test_optimize_max_iterations(optimizer):
    # Setup so that it never reaches 0.95 accuracy
    custom_suite = [
        TestCase(input={'text': 'Bad'}, expected_output='Negative')
    ]
    optimizer.test_suite = custom_suite

    results = optimizer.optimize("Base prompt: {text}", max_iterations=2)

    assert results['best_score'] == 0.0
    assert len(results['history']) == 2
