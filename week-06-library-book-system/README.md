# Week 6 — Library Book Management System

**Topic:** Object-Oriented Programming (classes, inheritance, polymorphism)
**Tier attempted:** Advanced (Base + Intermediate + Advanced)

## Overview

An object-oriented library catalog. A base `Book` class models a single
book and knows how to check itself out, be returned, and report its
status. Three subclasses specialize it through inheritance:

- **`EBook`** — never unavailable; each checkout increments an
  `active_downloads` counter instead of setting a borrower.
- **`AudioBook`** — circulates like a print book but adds a narrator and
  a listening duration (with a "long listen" note past 10 hours).
- **`ReferenceBook`** — permanently in-library only; refuses checkout.

An independent `Library` class manages the whole collection: add/remove,
search by author or genre, list available/checked-out books, generate a
formatted report, and persist the catalog to `library.csv`. The program
runs a base demo, a polymorphism demo, then an interactive menu.

## How to run

```
python waldron_library_book_system.py
```

On the first run there is no `library.csv`, so the program seeds a
nine-book starter collection. Choosing **[q] Save and quit** writes the
current collection to `library.csv`, and every later run reloads it.

## What it demonstrates

- **Classes:** `Book` defines `__init__`, `__str__`, `check_out`,
  `return_book`, and `get_status`. Instance attributes are set with
  `self.`; `check_out`/`return_book` return values rather than printing,
  and `__str__` returns an f-string with alignment format specifiers.
- **Inheritance:** each subclass uses `class Sub(Book):`, calls
  `super().__init__(...)` first, adds its own attributes, and reuses the
  base display line via `super().__str__()`.
- **Method overriding:** `EBook` overrides `check_out`/`get_status`,
  `ReferenceBook` overrides `check_out`/`return_book`/`get_status`, and
  every subclass overrides `__str__` to append a type-specific line.
- **New behaviors:** `get_download_info` (EBook) and `get_listening_info`
  (AudioBook) are methods that do not exist on `Book`.
- **Polymorphism:** `run_polymorphism_demo` loops over a mixed list and
  calls the same three methods on every object — no `isinstance`/`type`
  branching — so each type responds in its own way.
- **The `Library` manager** (independent class, not a `Book` subclass):
  `add_book`, `remove_book`, `find_by_isbn`, `find_by_author`,
  `find_by_genre`, `get_available_books`, `get_checked_out_books`, and
  `generate_report` (builds and *returns* a multi-line string using
  string multiplication and format specifiers).
- **File I/O with `csv`:** `save_to_csv` uses `isinstance()` to write a
  `type` column plus `extra1`/`extra2` for subclass fields;
  `load_from_csv` reads the `type` column to rebuild the correct class
  and restores the `available`/`borrower` state.
- **Exception handling:** file operations are wrapped in `try/except`;
  `load_from_csv` catches `FileNotFoundError` (informational message,
  collection unchanged) separately from `ValueError` and a general
  `Exception` fallback.
- **Interactive menu:** a `while` loop offers eight operations and a
  save-and-quit option, prompting for the book type when adding.
- **Prior-week concepts:** list comprehensions for filtering/searching,
  `sorted()` with a `key`, f-string formatting, loops, and functions.

## Files

- `waldron_library_book_system.py` — program source (all classes plus the
  main program; a recorded test run is in the header comment block)
- `library.csv` — sample catalog produced while testing; Dune and
  Educated are checked out to demonstrate the report and reload
