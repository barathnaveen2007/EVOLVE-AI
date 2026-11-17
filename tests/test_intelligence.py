
from core.intelligence import (
    analyze_goal,
    generate_recommendations,
    compare_progress
)


def test_goal_analysis():
    result = analyze_goal("Learn Python", 3, 5)

    assert result["goal"] == "Learn Python"
    assert result["estimated_hours"] > 0


def test_recommendations():
    result = analyze_goal("Learn AI", 6, 5)
    recommendations = generate_recommendations(result)

    assert len(recommendations) > 0


def test_progress():
    result = compare_progress(10, 5)

    assert result["completion_percentage"] == 50
