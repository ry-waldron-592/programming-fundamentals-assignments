# Week 4 — Personal Expense Tracker

**Topic:** Modules, Strings, and Files
**Tier attempted:** Advanced (Base + Intermediate + Advanced)

## Overview

A command-line expense tracker that saves records (date, description,
amount, category) to `expenses.csv` and reloads them every session. The
user can add new expenses, search existing records by keyword, view
running totals by category, view this month's expenses, and generate a
formatted summary report (`expense_report.txt`).

## How to run

```
python waldron_personal_expense_tracker.py
```

## What it demonstrates

- **Modules:** `os`, `datetime`, and `csv` from the standard library
- **File I/O:** `csv.reader`/`csv.writer` for reading and appending
  `expenses.csv` (with a header row written automatically the first
  time), plus a separate `expense_report.txt` summary report
- **String operations:** slicing (`description[:30]`, `date_string[:4]`
  and `date_string[5:7]`), `.split(",")`, `",".join()`, `.strip()`,
  `.lower()`, `.startswith()`, `.splitlines()`, and f-string format
  specifiers for column alignment (`{value:<12}`, `{value:>10}`, etc.)
- **Exception handling:** `try/except/finally` around the main program
  with separate `except` clauses for `FileNotFoundError`, `ValueError`,
  and a general `Exception` fallback; `try/except` inside
  `get_valid_amount()` to re-prompt on bad numeric input
- **Functions:** `build_record`, `append_record`, `load_records`,
  `display_records`, `search_expenses`, `calculate_totals`,
  `filter_by_month`, `generate_report`, `get_valid_amount`, and
  `get_valid_category`, each with a single responsibility
- **Input validation:** a `while` loop re-prompts for a category until it
  starts with a letter (checked with `.startswith()` against a string of
  digits and special characters), and re-prompts for an amount until it
  parses as a `float`

## Files

- `waldron_personal_expense_tracker.py` — program source
- `expenses.csv` — sample data produced while testing (includes a header
  row plus records across two different months, to demonstrate month
  filtering)
- `expense_report.txt` — sample summary report produced by
  `generate_report()`
