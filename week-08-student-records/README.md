# Week 8 — Student Record Management System (Debug, Fix & Refactor)

**Topic:** Debugging (syntax, logic, and subtle logic errors) and refactoring a
top-down script into an object-oriented design
**Final assignment:** Part 1 (find & fix 10 bugs) + Part 2 (OOP refactor with
binary search) + bonus inheritance

## Overview

The starter program `student_records.py` (provided by the course) had **10
deliberately introduced bugs** and was written in a flat, top-down style with
global variables. This folder delivers both required parts:

- **Part 1 — Debug & Fix:** `student_records_fixed.py` is the original program
  with all 10 bugs corrected and the top-down structure otherwise preserved, so
  it can be diffed against the original. Every fix is tagged `# BUGFIX n` in the
  code and documented in `bug_report.txt`.
- **Part 2 — Refactor:** `waldron_student_records_refactored.py` rebuilds the same
  behaviour around a `Student` class and a `StudentRoster` class, replaces the
  linear search with a **binary search**, adds exception handling, and includes
  a `GraduateStudent` subclass for the bonus.

Both programs present the same 4-option menu and produce byte-for-byte identical
output for the nine required test cases.

## How to run

```
python student_records_fixed.py
python waldron_student_records_refactored.py
```

At the menu: choose **1** and enter `students.csv` to load, **2** to list, **3**
to search by ID (case-insensitive), and **4** to exit.

## The 10 bugs (Part 1)

| # | Type | Line | Bug |
|---|------|------|-----|
| 1 | Crash | 69 | File closed before `csv.DictReader` is iterated → `ValueError` |
| 2 | Crash | 149 | Wrong dict key `Student_ID` → `KeyError` when a match displays |
| 3 | Logic | 67–86 | Roster not cleared before load → re-load duplicates to 20 records |
| 4 | Logic | 89 | `csv_loaded` never set `True` → Options 2 & 3 always blocked |
| 5 | Logic | 135 | `while ... <= len(...)` off-by-one → `IndexError` on no match |
| 6 | Logic | 133 | `found_student` not reset → stale prior match shown |
| 7 | Logic | 108–116 | `row_number` never incremented → every row numbered "1" |
| 8 | Logic | 159 | `menu_choice == 4` (int vs str) → Exit never fires |
| 9 | Subtle | 136 | Input not upper-cased → lowercase search fails |
| 10 | Subtle | 138 | "Force to end" set to `len-1` → infinite loop on last record |

Full write-ups (original code, fix, symptom, explanation) are in
`bug_report.txt`.

## Refactor highlights (Part 2)

- **R-01/R-02 OOP & encapsulation:** `Student` holds one record with a `__str__`
  detail block; `StudentRoster` owns `students`, `csv_loaded`, and `filename` as
  instance attributes — no globals.
- **R-03 methods:** `load_csv()`, `list_students()`, `search_by_id()`, `run()`.
- **R-04 binary search:** `search_by_id()` sorts the roster by normalised ID on
  load and searches with an explicit low/high/mid loop — no `list.index()` and
  no `in` operator.
- **R-05 exception handling:** `load_csv()` wraps file I/O in `try/except` for
  `FileNotFoundError` and catches `KeyError` / `csv.Error` for malformed rows,
  printing a helpful message and returning to the menu instead of crashing.
- **R-06 string operations:** IDs are `.strip()`-ed and `.upper()`-ed so search
  is case-insensitive and whitespace-tolerant.
- **R-07 CSV module:** still uses `csv.DictReader`; `students.csv` is unchanged.
- **R-08 bonus inheritance:** `GraduateStudent(Student)` adds a `thesis_topic`
  attribute and cleanly overrides `__str__`.

## What it demonstrates

This assignment exercises the full semester's toolkit — reading a bug through to
its root cause, then rebuilding a working-but-messy script into a maintainable
OOP design without changing what the user sees:

- **Systematic debugging:** the ten bugs are triaged by *how* they fail — crashes
  (`ValueError`, `KeyError`), plain logic errors (off-by-one, missing state flag,
  int-vs-string comparison), and subtle errors that only surface under specific
  input (lowercase search, searching the last record). Each is fixed in place and
  documented with original code, corrected code, symptom, and reasoning.
- **OOP & encapsulation:** two single-responsibility classes — `Student` (one
  record) and `StudentRoster` (the collection + menu actions) — with all state
  as instance attributes and no globals.
- **Algorithms:** an explicit binary search (low/high/mid loop) replacing the
  linear scan, plus the `list.sort(key=...)` that makes binary search valid.
- **Robustness:** `try/except` around file I/O and CSV parsing so a bad filename
  returns to the menu instead of crashing; `.strip()`/`.upper()` normalisation so
  search is case-insensitive and whitespace-tolerant.
- **Inheritance (bonus):** `GraduateStudent` extends `Student` and overrides
  `__str__` via `super()`.

### Challenges & design choices

- **Behavioural equivalence over "nicer" output.** The original listing table has
  a cosmetic quirk: the header row inserts spaces between columns but the data
  rows do not, so the columns don't line up perfectly. Because the assignment
  requires the refactored program to be *byte-for-byte identical* to the fixed
  version (tests T1–T9), I deliberately **reproduced that spacing** in
  `Student.table_row()` rather than "fixing" the alignment — matching the spec
  mattered more than prettier output.
- **Binary search needs sorted data.** A binary search is only correct on an
  ordered list, so `load_csv()` sorts the roster by normalised ID on load. The
  provided `students.csv` is already in ID order, so this sort doesn't change the
  Option-2 listing order — the two programs still produce identical output — but
  it makes the search robust even if the CSV rows were shuffled.
- **Two search bugs interacted.** The trickiest bugs to isolate were the search
  loop's off-by-one (`<=`) and the "force to end" line (`len - 1`): together they
  produced *different* failures depending on the query — an `IndexError` on a
  missing ID versus an infinite loop when matching the last record. I found them
  by testing the boundaries specifically (nonexistent ID and the final record),
  which is why those cases are called out separately in `bug_report.txt`.
- **Choosing where each bug "lives."** An off-by-one loop bound technically
  crashes, but I classified it as a *logic* error (a wrong boundary condition)
  and reserved the *crash* category for the two mechanical failures (closed-file
  read, wrong dictionary key), keeping the 2 / 6 / 2 split the assignment defines.
- **Normalisation vs. display.** Search compares on an upper-cased key but the
  "No student found with ID '…'" message echoes back the user's original input,
  so the feedback reflects exactly what they typed.

### Verification

Both programs were run on **Python 3.12** against test cases T1–T9. All nine
pass, and the refactored program's output is **byte-for-byte identical** to the
fixed program's (verified with `diff`). Additional checks confirmed: re-loading
keeps the count at 10 (not 20), an unknown filename prints a helpful message and
returns to the menu instead of crashing, the "no data loaded" guards fire before
a load, invalid menu input is rejected, and the bonus `GraduateStudent` subclass
adds `thesis_topic` and overrides `__str__` cleanly.

## Files

- `student_records_fixed.py` — Part 1 deliverable (debugged original)
- `waldron_student_records_refactored.py` — Part 2 deliverable (OOP + binary search)
- `students.csv` — original, unmodified data file (10 records)
- `bug_report.txt` — one entry per bug (type, line, original, fix, symptom, why)
