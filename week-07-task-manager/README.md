# Week 7 — Personal Task & Project Manager

**Topic:** Database Programming (SQLite via the `sqlite3` module)
**Tier attempted:** Advanced (Base + Intermediate + Advanced)

## Overview

A task manager backed by a real SQLite relational database instead of an
in-memory list or a CSV file. The program is organized in three layers
that mirror the assignment tiers:

- **Base** — standalone functions (`create_connection`, `setup_database`,
  `add_task`, `get_all_tasks`, `get_tasks_by_status`,
  `update_task_status`, `delete_task`, `display_tasks`) that operate on a
  single `tasks` table with full CRUD and parameterized queries.
- **Intermediate** — a `TaskManager` class that adds a `projects` table
  (one-to-many via `project_id`), a `LEFT JOIN`, `GROUP BY` project
  summaries, `LIKE` keyword search, and CSV export.
- **Advanced** — a many-to-many tag system (`tags` + `task_tags` junction
  table), manual-transaction bulk insert with rollback, a CSV import, a
  performance index, and a separate `DatabaseReport` class that builds
  formatted statistical reports from aggregate queries.

## How to run

```
python waldron_personal_task_manager.py
```

The program **deletes and recreates `tasks.db` at the start of each run**
so the demonstration output is deterministic and reproducible. It runs the
Base-level function demo first, then the full `TaskManager` /
`DatabaseReport` demo. On completion it leaves three files behind:
`tasks.db`, `tasks_export.csv`, and it reads the shipped
`import_tasks.csv`.

## What it demonstrates

- **SQL fundamentals:** `CREATE TABLE IF NOT EXISTS`, `INSERT`, `SELECT`
  with `WHERE` / `ORDER BY`, `UPDATE`, `DELETE`, `LEFT JOIN`, three-table
  `JOIN`, `GROUP BY` with `COUNT(*)`, a `CASE` expression in `ORDER BY`,
  `LIKE` search, `INSERT OR IGNORE`, and `date('now')` date filtering.
- **Parameterized queries everywhere** — every variable value is passed
  as a `?` placeholder tuple; no SQL is ever built with f-strings or
  concatenation (prevents SQL injection).
- **Relationships:** one-to-many (tasks → project) and many-to-many
  (tasks ↔ tags via a junction table with a composite primary key).
- **Transactions:** `bulk_add_tasks` takes manual control
  (`isolation_level = None`, explicit `BEGIN` / `COMMIT` / `ROLLBACK`),
  re-raises on error, and restores `isolation_level` in a `finally`
  block. A rollback demo inserts a batch with one `NULL` title and shows
  the whole batch is undone.
- **Exception handling per tier:** every DB function catches
  `sqlite3.Error`; `export_to_csv` catches `IOError` and `sqlite3.Error`;
  `import_from_csv` catches `FileNotFoundError`, `csv.Error`, and
  `sqlite3.Error` as separate clauses.
- **OOP composition:** `DatabaseReport` is independent of `TaskManager`
  and works through the `TaskManager` instance it is given
  (`self.tm.conn`); all its methods **return** strings and never print.
- **Prior-week skills:** `csv` module for import/export, list
  comprehensions, f-string format specifiers for aligned tables, string
  multiplication for separators, and the `datetime` module for the report
  header.
- **Performance:** `CREATE INDEX IF NOT EXISTS idx_tasks_status` on the
  frequently filtered `status` column, created inside `_setup_tables()`.

## Files

- `waldron_personal_task_manager.py` — program source (all functions and
  classes; a recorded run is summarized in the header comment block)
- `tasks.db` — SQLite database produced by a run (final Advanced state)
- `tasks_export.csv` — output of `export_to_csv()` (`(No Project)` shown
  for unlinked tasks; no raw `None` values)
- `import_tasks.csv` — sample 3-row import file read by `import_from_csv()`
