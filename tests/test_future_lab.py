from core.future_lab import generate_scenarios

def test_generates_three_scenarios():
    result = generate_scenarios(6, 7, 8)
    assert len(result) == 3
    assert {x["key"] for x in result} == {"daily", "weekend", "project"}

def test_scores_are_bounded():
    for item in generate_scenarios(100, 10, 10):
        assert 0 <= item["score"] <= 100
