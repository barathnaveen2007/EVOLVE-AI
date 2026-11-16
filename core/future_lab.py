def clamp(value, low=0, high=100):
    return max(low, min(high, int(round(value))))

def generate_scenarios(weekly_hours, consistency, practical_preference):
    """Transparent heuristic scores; these are not probabilities or validated forecasts."""
    hours = max(0.5, float(weekly_hours))
    consistency = int(consistency)
    practical = int(practical_preference)

    daily_score = clamp(48 + consistency * 3 + min(hours, 10) * 1.5)
    weekend_score = clamp(53 + (11-consistency) * 2 + min(hours, 10) * 1.2)
    project_score = clamp(45 + practical * 3.2 + min(hours, 10) * 1.4)

    return [
        {
            "key": "daily",
            "name": "Daily short sessions",
            "score": daily_score,
            "description": "Short, frequent sessions spread across the week.",
            "rationale": f"Rewards stated consistency confidence ({consistency}/10) and uses available time ({hours:g} hours/week).",
            "forecast_text": "A frequent practice routine may support steady progress if the user can maintain the schedule.",
            "assumptions": "The user can protect several short study windows each week; interruptions are manageable."
        },
        {
            "key": "weekend",
            "name": "Weekend intensive",
            "score": weekend_score,
            "description": "One or two longer sessions concentrated on weekends.",
            "rationale": f"May suit lower weekday consistency; available time is {hours:g} hours/week.",
            "forecast_text": "Longer sessions may make it easier to complete substantial tasks, but gaps between sessions may slow feedback.",
            "assumptions": "Weekends remain available and long sessions do not cause excessive fatigue."
        },
        {
            "key": "project",
            "name": "Project-first learning",
            "score": project_score,
            "description": "Learn concepts by building a small practical project every week.",
            "rationale": f"Reflects practical-learning preference ({practical}/10) and available time ({hours:g} hours/week).",
            "forecast_text": "Building practical projects may improve applied understanding if project scope stays small.",
            "assumptions": "Projects are appropriately scoped and the user has access to learning resources."
        }
    ]
