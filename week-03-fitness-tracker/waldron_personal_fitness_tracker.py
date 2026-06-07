"""
Author: Jason
Date: 2026-06-07
Description: Personal Fitness Tracker. Collects workout sessions from the
user, calculates each workout's calorie burn rate and intensity label,
then reports a session summary with totals, averages, the best workout,
a calorie-goal check, and an effort trend analysis.
Tier Attempted: Advanced (Base + Intermediate + Advanced)

Test Output (run with goal=1000, workouts Running/30/320, Yoga/45/180, Cycling/40/300, then "done"):

Welcome to the Personal Fitness Tracker!
Log your workouts and I'll calculate your burn rate, intensity, and a session summary.

Enter your daily calorie burn goal (whole number): 1000

Enter your workouts below. Type 'done' as the workout name when you're finished.

--- Workout 1 ---
Workout name (or 'done' to finish): Running
Duration (minutes): 30
Calories burned: 320
Result: Running | 30 min | 320 cal | 10.7 cal/min | Intensity: High

--- Workout 2 ---
Workout name (or 'done' to finish): Yoga
Duration (minutes): 45
Calories burned: 180
Result: Yoga | 45 min | 180 cal | 4.0 cal/min | Intensity: Low

--- Workout 3 ---
Workout name (or 'done' to finish): Cycling
Duration (minutes): 40
Calories burned: 300
Result: Cycling | 40 min | 300 cal | 7.5 cal/min | Intensity: Moderate

--- Workout 4 ---
Workout name (or 'done' to finish): done

Workout              Duration  Calories       Rate  Intensity
------------------------------------------------------------
Running                    30       320   10.7 c/m  High
Yoga                       45       180    4.0 c/m  Low
Cycling                    40       300    7.5 c/m  Moderate

===== Session Summary =====
Workouts logged : 3
Total calories  : 800
Avg calories    : 266.7
Avg duration    : 38.3 min
Best workout    : Running
Effort trend    : Mixed
Goal check      : 200 calories short of your 1000-calorie goal.
===========================

All workouts logged. Great job staying active!

Additional scenarios verified (see conversation log for full transcripts):
- "done" on the first prompt -> prints a no-workouts message, no crash, no summary
- Single workout logged -> Effort trend returns "Not enough data"
- Boundary rates of exactly 5.0 and 10.0 cal/min -> "Moderate" and "High" respectively
- Two workouts tied for the highest calories -> find_best_workout() returns the first one logged
- Strictly decreasing calories (400, 400, 100) -> Effort trend returns "Declining"
- Total calories meeting/exceeding the goal -> check_goal() returns the "Goal reached!" message
"""


def calories_per_minute(calories, duration):
    """Return calories burned per minute, rounded to one decimal place."""
    rate = calories / duration
    return round(rate, 1)


def get_intensity(rate):
    """Return a Low/Moderate/High label for a calories-per-minute rate."""
    if rate < 5.0:
        return "Low"
    elif rate < 10.0:
        return "Moderate"
    else:
        return "High"


def calculate_total(values):
    """Return the sum of a list of numbers using an accumulator."""
    total = 0
    for value in values:
        total += value
    return total


def calculate_average(values):
    """Return the average of a list of numbers, rounded to one decimal place."""
    total = calculate_total(values)
    return round(total / len(values), 1)


def find_best_workout(names, calories_list):
    """Return the name of the workout with the highest calorie burn (first one wins ties)."""
    best_index = 0
    for i in range(len(calories_list)):
        if calories_list[i] > calories_list[best_index]:
            best_index = i
    return names[best_index]


def check_goal(total_calories, goal):
    """Return a message comparing total calories burned to the daily goal."""
    if total_calories >= goal:
        return f"Goal reached! You burned {total_calories} calories."
    else:
        shortfall = goal - total_calories
        return f"{shortfall} calories short of your {goal}-calorie goal."


def format_workout_row(name, duration, calories, width=20):
    """Build and return one formatted table row for a workout (computes its own rate/intensity)."""
    rate = calories_per_minute(calories, duration)
    intensity = get_intensity(rate)
    return f"{name:<{width}} {duration:>8} {calories:>9} {rate:>6} c/m  {intensity}"


def print_workout_table(names, durations, calories_list):
    """Print a header row followed by a formatted row for every logged workout."""
    print(f"{'Workout':<20} {'Duration':>8} {'Calories':>9} {'Rate':>10}  Intensity")
    print("-" * 60)
    for i in range(len(names)):
        print(format_workout_row(names[i], durations[i], calories_list[i]))


def analyze_trend(calories_list):
    """Compare each workout's calories to the previous one and classify the overall trend."""
    if len(calories_list) < 2:
        return "Not enough data"

    increases = 0
    decreases = 0
    for i in range(1, len(calories_list)):
        if calories_list[i] > calories_list[i - 1]:
            increases += 1
        elif calories_list[i] < calories_list[i - 1]:
            decreases += 1

    if increases > 0 and decreases > 0:
        return "Mixed"
    elif decreases == 0:
        return "Improving"
    else:
        return "Declining"


# ---- Main program ----

print("Welcome to the Personal Fitness Tracker!")
print("Log your workouts and I'll calculate your burn rate, intensity, and a session summary.")
print()

calorie_goal = int(input("Enter your daily calorie burn goal (whole number): "))

workout_names = []
workout_durations = []
workout_calories = []

print()
print("Enter your workouts below. Type 'done' as the workout name when you're finished.")

workout_number = 0
while True:
    workout_number += 1
    print(f"\n--- Workout {workout_number} ---")
    name = input("Workout name (or 'done' to finish): ").strip()
    if name.lower() == "done":
        break

    # Nested loops: keep re-prompting until valid whole-number input is given
    while True:
        duration_text = input("Duration (minutes): ")
        try:
            duration = int(duration_text)
            break
        except ValueError:
            print("Please enter a whole number for duration.")

    while True:
        calories_text = input("Calories burned: ")
        try:
            calories = int(calories_text)
            break
        except ValueError:
            print("Please enter a whole number for calories burned.")

    workout_names.append(name)
    workout_durations.append(duration)
    workout_calories.append(calories)

    rate = calories_per_minute(calories, duration)
    intensity = get_intensity(rate)
    print(f"Result: {name} | {duration} min | {calories} cal | {rate} cal/min | Intensity: {intensity}")

print()
if len(workout_names) == 0:
    print("No workouts were logged this session. Come back when you're ready to get moving!")
else:
    print_workout_table(workout_names, workout_durations, workout_calories)

    total_calories = calculate_total(workout_calories)
    average_calories = calculate_average(workout_calories)
    average_duration = calculate_average(workout_durations)
    best_workout = find_best_workout(workout_names, workout_calories)
    trend = analyze_trend(workout_calories)
    goal_message = check_goal(total_calories, calorie_goal)

    print()
    print("===== Session Summary =====")
    print(f"Workouts logged : {len(workout_names)}")
    print(f"Total calories  : {total_calories}")
    print(f"Avg calories    : {average_calories}")
    print(f"Avg duration    : {average_duration} min")
    print(f"Best workout    : {best_workout}")
    print(f"Effort trend    : {trend}")
    print(f"Goal check      : {goal_message}")
    print("===========================")
    print()
    print("All workouts logged. Great job staying active!")
