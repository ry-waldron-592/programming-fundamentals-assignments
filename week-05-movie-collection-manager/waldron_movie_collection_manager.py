"""
Author: Ryan Waldron
Date: 2026-06-21
Description: Movie Collection Manager. Stores, displays, and analyzes a
             personal library of films using lists and dictionaries.
             Persists the collection to a CSV file between sessions.
Tier Attempted: Advanced (Base + Intermediate + Advanced)

Sample Run (first run, no movies.csv present yet; two movies added,
filter for "action", Tenet's rating updated to 8.0, sorted by rating
descending, looked up "Moana"):

Your Movie Collection
----------------------------------------------------------------------
Tenet                          2020   Sci-Fi / Action / Thriller 7.3
London Has Fallen              2016   Action / Thriller         5.9
Hunter Killer                  2018   Action / Thriller         6.6
Night School                   2018   Comedy                    5.5
Moana                          2016   Animation / Adventure     7.6

Let's add two new movies to the collection.

New movie #1
  Title: The Dark Knight
  Year: 2008
  Genres (separated by commas): Action, Crime, Drama
  Rating: 9.0

New movie #2
  Title: Spirited Away
  Year: 2001
  Genres (separated by commas): Animation, Adventure
  Rating: 8.6

All Movies Sorted by Year
----------------------------------------------------------------------
Spirited Away                  2001   Animation / Adventure     8.6
The Dark Knight                2008   Action / Crime / Drama    9.0
London Has Fallen              2016   Action / Thriller         5.9
Moana                          2016   Animation / Adventure     7.6
Hunter Killer                  2018   Action / Thriller         6.6
Night School                   2018   Comedy                    5.5
Tenet                          2020   Sci-Fi / Action / Thriller 7.3

Top 3 Rated Movies
----------------------------------------------------------------------
The Dark Knight                2008   Action / Crime / Drama    9.0
Spirited Away                  2001   Animation / Adventure     8.6
Moana                          2016   Animation / Adventure     7.6

Collection average rating: 7.21

Unique genres in collection: Action, Adventure, Animation, Comedy, Crime, Drama, Sci-Fi, Thriller

Enter a genre to filter by: action

Movies in the action genre
----------------------------------------------------------------------
The Dark Knight                2008   Action / Crime / Drama    9.0
London Has Fallen              2016   Action / Thriller         5.9
Hunter Killer                  2018   Action / Thriller         6.6
Tenet                          2020   Sci-Fi / Action / Thriller 7.3

Do you want to update a movie's rating? (yes/no): yes
  Movie title: tenet
  New rating: 8.0
  Updated rating for 'tenet'.

Collection After Update
----------------------------------------------------------------------
Spirited Away                  2001   Animation / Adventure     8.6
The Dark Knight                2008   Action / Crime / Drama    9.0
London Has Fallen              2016   Action / Thriller         5.9
Moana                          2016   Animation / Adventure     7.6
Hunter Killer                  2018   Action / Thriller         6.6
Night School                   2018   Comedy                    5.5
Tenet                          2020   Sci-Fi / Action / Thriller 8.0

===== Genre Statistics =====
Genre                Avg Rating   Count
----------------------------------------
Crime                9.0          1
Drama                9.0          1
Animation            8.1          2
Adventure            8.1          2
Sci-Fi               8.0          1
Action               7.38         4
Thriller             6.83         3
Comedy               5.5          1
============================

Sort by (title / year / rating): rating
Direction (asc / desc): desc

Movies Sorted by Rating (desc)
----------------------------------------------------------------------
The Dark Knight                2008   Action / Crime / Drama    9.0
Spirited Away                  2001   Animation / Adventure     8.6
Tenet                          2020   Sci-Fi / Action / Thriller 8.0
Moana                          2016   Animation / Adventure     7.6
Hunter Killer                  2018   Action / Thriller         6.6
London Has Fallen              2016   Action / Thriller         5.9
Night School                   2018   Comedy                    5.5

===== Genre Catalog =====

Animation
  Spirited Away (8.6)
  Moana (7.6)

Action
  The Dark Knight (9.0)
  Hunter Killer (6.6)
  London Has Fallen (5.9)

Comedy
  Night School (5.5)

Sci-Fi
  Tenet (8.0)

=========================

Enter a movie title to look up its rating: Moana
  Rating for 'Moana': 7.6

===== Genre Champions =====
Animation -> Spirited Away (8.6)
Action -> The Dark Knight (9.0)
Comedy -> Night School (5.5)
Sci-Fi -> Tenet (8.0)
===========================

Saved 7 movies to movies.csv.
"""

import csv

CSV_FILENAME = "movies.csv"

# Starter collection used when no CSV file exists yet
STARTER_MOVIES = [
    {"title": "Tenet",              "year": 2020, "genres": ["Sci-Fi", "Action", "Thriller"], "rating": 7.3},
    {"title": "London Has Fallen",  "year": 2016, "genres": ["Action", "Thriller"],           "rating": 5.9},
    {"title": "Hunter Killer",      "year": 2018, "genres": ["Action", "Thriller"],           "rating": 6.6},
    {"title": "Night School",       "year": 2018, "genres": ["Comedy"],                       "rating": 5.5},
    {"title": "Moana",              "year": 2016, "genres": ["Animation", "Adventure"],       "rating": 7.6},
]


# Advanced: load the collection from CSV at startup
def load_from_csv(filename):
    """Load movies from CSV. Return the starter list if the file does not exist."""
    try:
        movies = []
        with open(filename, "r", newline="") as f:
            reader = csv.reader(f)
            next(reader)  # skip header row
            for row in reader:
                title, year, genres_str, rating = row
                movies.append({
                    "title": title,
                    "year": int(year),
                    "genres": genres_str.split("|"),
                    "rating": float(rating)
                })
        return movies
    except FileNotFoundError:
        # Return copies so the starter constant is never mutated
        return [movie.copy() for movie in STARTER_MOVIES]


# Base: build a movie dictionary
def create_movie(title, year, genres, rating):
    """Return a new movie dictionary from the four required fields."""
    return {
        "title": title,
        "year": year,
        "genres": genres,
        "rating": rating
    }


# Base: display the collection in a formatted table
def display_movies(movies, heading):
    """Print a formatted table of all movies under the given heading."""
    print()
    print(heading)
    print("-" * 70)
    if not movies:
        print("No movies in this collection.")
        return
    for movie in movies:
        title = movie["title"]
        year = movie["year"]
        genres = " / ".join(movie["genres"])
        rating = movie["rating"]
        print(f"{title:<30} {year:<6} {genres:<25} {rating:<5}")


# Base: return the top n movies by rating
def find_top_rated(movies, n):
    """Return a new list of the top n movies sorted by rating descending."""
    sorted_movies = sorted(movies, key=lambda m: m["rating"], reverse=True)
    return sorted_movies[:n]


# Base: compute the average rating without using sum()
def get_average_rating(movies):
    """Return the average rating across all movies, rounded to 2 decimal places."""
    if not movies:
        return 0.0
    total = 0.0
    for movie in movies:
        total += movie["rating"]
    return round(total / len(movies), 2)


# Intermediate: filter movies by genre, case insensitive
def filter_by_genre(movies, genre):
    """Return a new list of movies whose genres list contains the given genre."""
    target = genre.lower()
    result = []
    for movie in movies:
        movie_genres_lower = [g.lower() for g in movie["genres"]]
        if target in movie_genres_lower:
            result.append(movie)
    return result


# Intermediate: update a movie's rating by title
def update_rating(movies, title, new_rating):
    """Search by title (case insensitive) and update the rating. Return True or False."""
    target = title.lower()
    for movie in movies:
        if movie["title"].lower() == target:
            movie["rating"] = new_rating
            return True
    return False


# Intermediate: compute per genre statistics
def get_genre_stats(movies):
    """Return a list of (genre, avg_rating, count) tuples sorted by avg rating descending."""
    # Build the unique genres list using a membership check, not a set
    unique_genres = []
    for movie in movies:
        for genre in movie["genres"]:
            if genre not in unique_genres:
                unique_genres.append(genre)

    stats = []
    for genre in unique_genres:
        ratings = []
        for movie in movies:
            if genre in movie["genres"]:
                ratings.append(movie["rating"])
        if ratings:
            total = 0.0
            for r in ratings:
                total += r
            avg = round(total / len(ratings), 2)
            stats.append((genre, avg, len(ratings)))

    stats.sort(key=lambda t: t[1], reverse=True)
    return stats


# Intermediate: flexible sort that does not modify the original list
def sort_movies(movies, sort_key, reverse=False):
    """Return a new list sorted by the given key. Return list unchanged if key is invalid."""
    valid_keys = ["title", "year", "rating"]
    if sort_key not in valid_keys:
        return movies
    return sorted(movies, key=lambda m: m[sort_key], reverse=reverse)


# Advanced: build a nested dictionary catalog keyed by primary genre
def build_genre_catalog(movies):
    """Organize movies into a nested dict where each key is a primary genre."""
    catalog = {}
    for movie in movies:
        primary = movie["genres"][0]
        if primary in catalog:
            catalog[primary].append(movie)
        else:
            catalog[primary] = [movie]
    return catalog


# Advanced: display the nested genre catalog
def display_genre_catalog(catalog):
    """Print each genre section with its movies sorted by rating descending."""
    print()
    print("===== Genre Catalog =====")
    for genre, movie_list in catalog.items():
        print(f"\n{genre}")
        sorted_section = sorted(movie_list, key=lambda m: m["rating"], reverse=True)
        for movie in sorted_section:
            print(f"  {movie['title']} ({movie['rating']})")
    print("\n=========================")


# Advanced: build a title to rating lookup using a dictionary comprehension
def get_rating_lookup(movies):
    """Return a dict mapping each movie's title to its rating."""
    return {movie["title"]: movie["rating"] for movie in movies}


# Advanced: find the highest rated movie in each genre without using max()
def find_genre_champions(catalog):
    """Return a dict mapping each genre to the title of its highest rated movie."""
    champions = {}
    for genre, movie_list in catalog.items():
        best_movie = movie_list[0]
        best_rating = best_movie["rating"]
        for movie in movie_list:
            if movie["rating"] > best_rating:
                best_movie = movie
                best_rating = movie["rating"]
        champions[genre] = best_movie["title"]
    return champions


# Advanced: persist the collection to CSV
def save_to_csv(movies, filename):
    """Write the movie collection to a CSV file. Genres serialized as pipe separated."""
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "year", "genres", "rating"])
        for movie in movies:
            genres_str = "|".join(movie["genres"])
            writer.writerow([movie["title"], movie["year"], genres_str, movie["rating"]])


def main():
    # Advanced: load from CSV at the very start
    movies = load_from_csv(CSV_FILENAME)

    # Step 2: display the collection as loaded
    display_movies(movies, "Your Movie Collection")

    # Step 3: ask the user to add two new movies
    print("\nLet's add two new movies to the collection.")
    for i in range(2):
        print(f"\nNew movie #{i + 1}")
        title = input("  Title: ")
        year = int(input("  Year: "))
        genres_input = input("  Genres (separated by commas): ")
        genres = [g.strip() for g in genres_input.split(",")]
        rating = float(input("  Rating: "))
        new_movie = create_movie(title, year, genres, rating)
        movies.append(new_movie)

    # Step 4: sort by year in place and display
    movies.sort(key=lambda m: m["year"])
    display_movies(movies, "All Movies Sorted by Year")

    # Step 5: top 3 rated
    top_3 = find_top_rated(movies, 3)
    display_movies(top_3, "Top 3 Rated Movies")

    # Step 6: average rating
    avg = get_average_rating(movies)
    print(f"\nCollection average rating: {avg}")

    # Intermediate Step 7: display unique genres found in the collection
    unique_genres = []
    for movie in movies:
        for genre in movie["genres"]:
            if genre not in unique_genres:
                unique_genres.append(genre)
    unique_genres.sort()
    print(f"\nUnique genres in collection: {', '.join(unique_genres)}")

    # Intermediate Step 8: filter by genre
    print()
    target_genre = input("Enter a genre to filter by: ")
    filtered = filter_by_genre(movies, target_genre)
    if filtered:
        display_movies(filtered, f"Movies in the {target_genre} genre")
    else:
        print(f"No movies match the genre '{target_genre}'.")

    # Intermediate Step 9: optionally update a rating
    print()
    choice = input("Do you want to update a movie's rating? (yes/no): ").strip().lower()
    if choice == "yes":
        update_title = input("  Movie title: ")
        new_rating = float(input("  New rating: "))
        success = update_rating(movies, update_title, new_rating)
        if success:
            print(f"  Updated rating for '{update_title}'.")
            display_movies(movies, "Collection After Update")
        else:
            print(f"  No movie titled '{update_title}' found in the collection.")

    # Intermediate Step 10: genre statistics
    stats = get_genre_stats(movies)
    print("\n===== Genre Statistics =====")
    print(f"{'Genre':<20} {'Avg Rating':<12} {'Count':<6}")
    print("-" * 40)
    for genre, avg_rating, count in stats:
        print(f"{genre:<20} {avg_rating:<12} {count:<6}")
    print("============================")

    # Intermediate Step 11: flexible sort
    print()
    sort_choice = input("Sort by (title / year / rating): ").strip().lower()
    direction = input("Direction (asc / desc): ").strip().lower()
    reverse_flag = (direction == "desc")
    sorted_result = sort_movies(movies, sort_choice, reverse=reverse_flag)
    display_movies(sorted_result, f"Movies Sorted by {sort_choice.capitalize()} ({direction})")

    # Advanced: nested genre catalog
    catalog = build_genre_catalog(movies)
    display_genre_catalog(catalog)

    # Advanced: rating lookup demonstration
    rating_lookup = get_rating_lookup(movies)
    print()
    lookup_title = input("Enter a movie title to look up its rating: ")
    if lookup_title in rating_lookup:
        print(f"  Rating for '{lookup_title}': {rating_lookup[lookup_title]}")
    else:
        print(f"  '{lookup_title}' not found in the lookup.")

    # Advanced: genre champions
    champions = find_genre_champions(catalog)
    print("\n===== Genre Champions =====")
    for genre, title in champions.items():
        rating = rating_lookup[title]
        print(f"{genre} -> {title} ({rating})")
    print("===========================")

    # Advanced: save to CSV at the very end
    save_to_csv(movies, CSV_FILENAME)
    print(f"\nSaved {len(movies)} movies to {CSV_FILENAME}.")


if __name__ == "__main__":
    main()
