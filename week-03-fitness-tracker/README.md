# Week 3 — Personal Fitness Tracker

**Topic:** Loops and Functions
**Tier attempted:** Advanced (Base + Intermediate + Advanced)

## Overview

A command-line program that logs a user's workout sessions and reports on
their performance. The user sets a daily calorie-burn goal, then enters
workouts (name, duration, calories burned) until typing "done". For each
workout the program calculates a calories-per-minute rate and an intensity
label (Low / Moderate / High), then prints a formatted table and a session
summary covering totals, averages, the best workout, an effort-trend
analysis, and a goal check.

## How to run

```
python fitness_tracker.py
```

## What it demonstrates

- Functions defined with `def` that accept parameters and return values
  (`calories_per_minute`, `get_intensity`, `calculate_total`,
  `calculate_average`, `find_best_workout`, `check_goal`,
  `format_workout_row`, `print_workout_table`, `analyze_trend`)
- A `while` loop with a sentinel value (`"done"`) for variable-length input
- Parallel lists for storing workout names, durations, and calories
- Conditional logic (`if`/`elif`/`else`) inside functions
- Functions composed from other functions (e.g. `calculate_average` calls
  `calculate_total`; `format_workout_row` calls `calories_per_minute` and
  `get_intensity`)
- A function with a default parameter value (`format_workout_row(..., width=20)`)
- Nested loops (input validation loops nested inside the main collection loop)

A recorded sample run and additional verified test scenarios are documented
in the comment block at the top of [fitness_tracker.py](fitness_tracker.py).
