# Week 5 — Movie Collection Manager

**Topic:** Lists and Dictionaries
**Tier attempted:** Advanced (Base + Intermediate + Advanced)

## Overview

A command-line manager for a personal movie library. Each movie is a
dictionary (`title`, `year`, `genres` list, `rating`) and the collection
is a list of those dictionaries. The program loads the collection from
`movies.csv` at startup (falling back to a built-in starter list the
first time), lets the user add movies, filter by genre, update ratings,
view per-genre statistics, sort flexibly, browse a nested genre catalog,
look up ratings, and see each genre's highest-rated champion. The full
collection is saved back to `movies.csv` on exit.

## How to run

```
python waldron_movie_collection_manager.py
```

On the first run there is no `movies.csv`, so the built-in five-movie
starter list is used. The collection is saved on exit, and every later
run reloads it from the CSV file.

## What it demonstrates

- **List of dictionaries** as the primary data structure, with each
  movie holding `title` (str), `year` (int), `genres` (list of str), and
  `rating` (float)
- **Dictionary operations:** creating (`create_movie`), accessing by key,
  updating in place (`update_rating`), and iterating with `.items()`
  (`display_genre_catalog`, `find_genre_champions`)
- **List operations:** appending new movies, in-place `.sort()` by year,
  `sorted()` with a `key` for rating/title/year, reverse sorting, list
  slicing for the top-N (`find_top_rated`), and nested-list membership
  checks for genres (`filter_by_genre`, `get_genre_stats`)
- **Dictionary comprehension:** `get_rating_lookup` builds a
  title-to-rating lookup on a single line
- **Nested dictionary:** `build_genre_catalog` groups movies into a dict
  of genre → list of movie dicts using an explicit loop and `if/else`
- **String operations:** `" / ".join()` for display, `.split(",")` with
  whitespace stripping for genre input, `.lower()` for case-insensitive
  matching, and `"|".join()` / `.split("|")` at the CSV boundary
- **File I/O:** `csv.reader` / `csv.writer` to load and save the
  collection, with `try/except FileNotFoundError` returning the starter
  list when no CSV exists yet
- **Functions:** ten single-responsibility functions plus a `main()` that
  calls them in sequence; `get_average_rating` uses a manual accumulator
  (no `sum()`) and `find_genre_champions` finds the max by hand (no
  `max()`)

## Files

- `waldron_movie_collection_manager.py` — program source (with a sample
  run recorded in the header comment block)
- `movies.csv` — collection produced while testing; genres are stored as
  a pipe-separated string (e.g. `Action|Crime|Drama`) so the
  comma-delimited CSV stays intact
