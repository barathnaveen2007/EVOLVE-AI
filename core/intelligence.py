
from datetime import datetime


def analyze_goal(goal, deadline_months, weekly_hours):
    """Analyze whether a goal has a realistic time commitment."""

    if not goal.strip():
        return {"status": "error", "message": "Please enter a goal."}

    if deadline_months <= 0 or weekly_hours <= 0:
        return {"status": "error", "message": "Time values must be positive."}

    total_hours = deadline_months * 4.33 * weekly_hours

    if total_hours < 20:
        difficulty = "High"
    elif total_hours < 100:
        difficulty = "Medium"
    else:
        difficulty = "Flexible"

    return {
        "goal": goal,
        "deadline_months": deadline_months,
        "weekly_hours": weekly_hours,
        "estimated_hours": round(total_hours, 1),
        "difficulty": difficulty,
        "analyzed_at": datetime.now().isoformat()
    }


def generate_recommendations(analysis):
    """Generate transparent, rule-based recommendations."""

    if analysis.get("status") == "error":
        return [analysis["message"]]

    hours = analysis["estimated_hours"]

    recommendations = [
        f"Schedule {analysis['weekly_hours']} hours each week.",
        "Break the goal into smaller weekly milestones.",
        "Record your progress consistently."
    ]

    if hours < 20:
        recommendations.append(
            "Consider extending your deadline or increasing study time."
        )

    else:
        recommendations.append(
            "Review your progress every seven days."
        )

    return recommendations


def compare_progress(target, actual):
    """Compare a target against a recorded result."""

    if target <= 0:
        return {"status": "error", "message": "Target must be positive."}

    percentage = (actual / target) * 100

    return {
        "target": target,
        "actual": actual,
        "completion_percentage": round(percentage, 1),
        "remaining": max(0, target - actual)
    }
