from datetime import datetime, timedelta

def generate_smart_schedule(subject, topics_text, exam_date_str):
    # Parse the comma-separated topics
    topics = [t.strip() for t in topics_text.split(',') if t.strip()]
    if not topics:
        return {"error": "Please enter at least one topic."}

    try:
        exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format."}

    today = datetime.now()
    # Calculate days available, ignoring the time of day
    days_available = (exam_date.date() - today.date()).days

    if days_available <= 0:
        return {"error": "Exam date must be in the future!"}

    schedule = {}
    
    # Initialize an empty schedule for all available days
    for i in range(days_available + 1):
        current_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        schedule[current_date] = {"date": current_date, "day_num": i+1, "learn": [], "review": [], "test": []}

    # Algorithm: Distribute learning evenly across the first 70% of available days
    learning_days = max(1, int(days_available * 0.7))
    
    for index, topic in enumerate(topics):
        # 1. Initial Learning Day
        learn_day = index % learning_days
        learn_date = (today + timedelta(days=learn_day)).strftime("%Y-%m-%d")
        schedule[learn_date]["learn"].append(topic)
        
        # 2. First Review (Spaced Repetition: +1 Day)
        rev1_day = learn_day + 1
        if rev1_day < days_available:
            rev1_date = (today + timedelta(days=rev1_day)).strftime("%Y-%m-%d")
            schedule[rev1_date]["review"].append(topic)
        
        # 3. Second Review (Spaced Repetition: +4 Days)
        rev2_day = learn_day + 4
        if rev2_day < days_available:
            rev2_date = (today + timedelta(days=rev2_day)).strftime("%Y-%m-%d")
            schedule[rev2_date]["review"].append(topic)

    # Assign Mock Tests for the last 10% of days
    test_start = max(1, int(days_available * 0.9))
    for i in range(test_start, days_available):
        test_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        schedule[test_date]["test"].append(f"Full Mock Test: {subject}")
        
    # Override: The day right before the exam is strictly for rest and light review
    day_before = (exam_date - timedelta(days=1)).strftime("%Y-%m-%d")
    if day_before in schedule:
        schedule[day_before]["learn"] = []
        schedule[day_before]["review"] = ["Light concept skimming", "Rest, Hydrate, & Sleep Early"]
        schedule[day_before]["test"] = []

    # Clean up: Only return days where the student actually has a task scheduled
    active_schedule = [day for day in schedule.values() if day["learn"] or day["review"] or day["test"]]
    
    return {"schedule": active_schedule, "days_left": days_available}