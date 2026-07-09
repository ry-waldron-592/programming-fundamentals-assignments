"""
Author: Ryan Waldron
Date: 2026-07-08
Description: Library Book Management System built with object-oriented
             programming. A base Book class models a single book; three
             subclasses (EBook, AudioBook, ReferenceBook) specialize it
             through inheritance and method overriding; and an independent
             Library class manages the whole collection, generates reports,
             and persists the catalog to a CSV file. The program runs a
             base-level demo, a polymorphism demo, and an interactive menu.
Tier Attempted: Advanced (Base + Intermediate + Advanced)

Recorded test output (verifies the required cases):

--- Base: newly created Book ---
978-0743273565  The Great Gatsby             by F. Scott Fitzgerald    1925  Classic Fiction    Available

--- Base: check_out on available book ---
check_out returned: True   available=False   borrower=Jordan

--- Base: check_out on already checked-out book ---
check_out returned: False  available=False   borrower=Jordan

--- Base: return_book ---
'Dune' has been returned and is now available.
available=True   borrower=None

--- Intermediate: check out an EBook twice ---
active_downloads=2   available=True   status=Digital - 2 active download(s)

--- Intermediate: get_listening_info on a long AudioBook (>10 hrs) ---
Narrated by Rob Inglis. Listening time: 11.0 hours. (Long listen - plan accordingly!)

--- Advanced: report / save 9 books to CSV, reload (no duplicates) ---
Loaded 9 records from library.csv; 9 books in collection after reload.

--- Advanced: remove_book valid / invalid ISBN ---
remove valid   -> True
remove invalid -> False
"""

import csv


# ---------------------------------------------------------------------------
# The Book class - a single physical book
# ---------------------------------------------------------------------------
class Book:
    """A single physical library book that can be borrowed and returned."""

    def __init__(self, title, author, isbn, year, genre):
        # Store the five identifying fields, then set the two state fields.
        self.title = title
        self.author = author
        self.isbn = isbn
        self.year = year
        self.genre = genre
        self.available = True       # every new book starts available
        self.borrower = None        # nobody has it checked out yet

    def __str__(self):
        # Return one aligned, readable line ending in the current status.
        return (f"{self.isbn:<15} {self.title:<28} by {self.author:<24} "
                f"{self.year}  {self.genre:<16} {self.get_status()}")

    def check_out(self, patron_name):
        # Borrow the book if it is free; return True/False, never print.
        if self.available:
            self.available = False
            self.borrower = patron_name
            return True
        return False

    def return_book(self):
        # Reset availability and return a confirmation string (no printing).
        self.available = True
        self.borrower = None
        return f"'{self.title}' has been returned and is now available."

    def get_status(self):
        # Report whether the book is free or who currently holds it.
        if self.available:
            return "Available"
        return f"Checked out to {self.borrower}"


# ---------------------------------------------------------------------------
# Specialized book types that inherit from Book
# ---------------------------------------------------------------------------
class EBook(Book):
    """A digital book that any number of patrons can access at once."""

    def __init__(self, title, author, isbn, year, genre, file_format, file_size_mb):
        # Reuse Book's initializer, then add the digital-only attributes.
        super().__init__(title, author, isbn, year, genre)
        self.file_format = file_format
        self.file_size_mb = file_size_mb
        self.active_downloads = 0

    def check_out(self, patron_name):
        # A file is never "out": count a download and always succeed.
        self.active_downloads += 1
        return True

    def get_status(self):
        # Status reflects the live download count instead of a borrower.
        if self.active_downloads == 0:
            return "Digital - available for download"
        return f"Digital - {self.active_downloads} active download(s)"

    def __str__(self):
        # Inherit the Book line, then add a format/size line beneath it.
        return super().__str__() + f"\n    [Format: {self.file_format} | {self.file_size_mb} MB]"

    def get_download_info(self):
        # New method: a one-line summary of the digital file details.
        return (f"Format: {self.file_format} | Size: {self.file_size_mb} MB | "
                f"Downloads: {self.active_downloads}")


class AudioBook(Book):
    """A narrated book; it circulates like a print Book but adds audio data."""

    def __init__(self, title, author, isbn, year, genre, narrator, duration_hours):
        # Reuse Book's initializer, then store the narration details.
        super().__init__(title, author, isbn, year, genre)
        self.narrator = narrator
        self.duration_hours = duration_hours

    def __str__(self):
        # Inherit the Book line, then add a narrator/duration line.
        return super().__str__() + f"\n    [Narrator: {self.narrator} | Duration: {self.duration_hours} hrs]"

    def get_listening_info(self):
        # New method: describe the listen, flagging long ones.
        info = f"Narrated by {self.narrator}. Listening time: {self.duration_hours} hours."
        if self.duration_hours > 10:
            info += " (Long listen - plan accordingly!)"
        return info


class ReferenceBook(Book):
    """An on-site reference work that can never be checked out."""

    def __init__(self, title, author, isbn, year, genre, edition):
        # Reuse Book's initializer, add the edition, then lock circulation.
        super().__init__(title, author, isbn, year, genre)
        self.edition = edition
        self.available = False      # permanently non-circulating

    def check_out(self, patron_name):
        # Hard rule: reference books stay in the library. Print and refuse.
        print("Reference books are for in-library use only and cannot be checked out.")
        return False

    def return_book(self):
        # Nothing to return; report that and change nothing.
        return "Reference books do not need to be returned."

    def get_status(self):
        # Always report the in-library-only status with its edition.
        return f"In-Library Use Only (Edition {self.edition})"

    def __str__(self):
        # Inherit the Book line, then add the reference marker line.
        return super().__str__() + f"\n    [Reference - Edition {self.edition} - In-Library Use Only]"

    def get_reference_info(self):
        # New method: describe how this reference work may be used.
        return (f"'{self.title}' (Edition {self.edition}) is a reference work "
                f"for in-library use only.")


# ---------------------------------------------------------------------------
# The Library class - manages the whole collection
# ---------------------------------------------------------------------------
class Library:
    """Manages a collection of Book (and subclass) objects for a branch."""

    def __init__(self, name):
        # Store the branch name and start with an empty collection.
        self.name = name
        self.collection = []

    def add_book(self, book):
        # Append a Book (or any subclass) to the collection.
        self.collection.append(book)

    def remove_book(self, isbn):
        # Remove the book with an exact ISBN match; report success.
        for book in self.collection:
            if book.isbn == isbn:
                self.collection.remove(book)
                return True
        return False

    def find_by_isbn(self, isbn):
        # Return the first exact ISBN match, or None.
        for book in self.collection:
            if book.isbn == isbn:
                return book
        return None

    def find_by_author(self, author):
        # Case-insensitive "contains" search over the author field.
        needle = author.lower()
        return [b for b in self.collection if needle in b.author.lower()]

    def find_by_genre(self, genre):
        # Case-insensitive exact-match search over the genre field.
        needle = genre.lower()
        return [b for b in self.collection if b.genre.lower() == needle]

    def get_available_books(self):
        # All books currently marked available.
        return [b for b in self.collection if b.available]

    def get_checked_out_books(self):
        # All books currently unavailable (EBooks never appear here).
        return [b for b in self.collection if not b.available]

    def generate_report(self):
        # Build and RETURN a formatted multi-line report string (no printing).
        line = "=" * 40
        available = self.get_available_books()
        # "Checked out" means a patron holds it; a ReferenceBook is
        # unavailable but has no borrower, so it is reported separately.
        checked_out = [b for b in self.collection if b.borrower is not None]

        # Count by exact type using isinstance(), most specific first.
        ebooks = [b for b in self.collection if isinstance(b, EBook)]
        audiobooks = [b for b in self.collection if isinstance(b, AudioBook)]
        references = [b for b in self.collection if isinstance(b, ReferenceBook)]
        print_books = [b for b in self.collection
                       if isinstance(b, Book)
                       and not isinstance(b, (EBook, AudioBook, ReferenceBook))]

        rows = [
            line,
            f"     LIBRARY REPORT: {self.name}",
            line,
            f"Total books in collection : {len(self.collection)}",
            f"Available                 : {len(available)}",
            f"Checked out               : {len(checked_out)}",
            "",
            "--- Collection by Type ---",
            f"Print Books   : {len(print_books)}",
            f"eBooks        : {len(ebooks)}",
            f"Audiobooks    : {len(audiobooks)}",
            f"Reference     : {len(references)}",
            "",
            "--- Currently Checked Out ---",
        ]
        if checked_out:
            for b in checked_out:
                rows.append(f"  {b.title!r:<28} -> {b.borrower}")
        else:
            rows.append("  (none)")
        rows.append(line)
        return "\n".join(rows)

    def save_to_csv(self, filename):
        # Serialize the whole collection, using isinstance() per-row for type.
        header = ["type", "title", "author", "isbn", "year", "genre",
                  "available", "borrower", "extra1", "extra2"]
        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                count = 0
                for b in self.collection:
                    borrower = b.borrower if b.borrower is not None else ""
                    # Order matters: check the most specific types first.
                    if isinstance(b, EBook):
                        row = ["EBook", b.title, b.author, b.isbn, b.year, b.genre,
                               b.available, borrower, b.file_format, b.file_size_mb]
                    elif isinstance(b, AudioBook):
                        row = ["AudioBook", b.title, b.author, b.isbn, b.year, b.genre,
                               b.available, borrower, b.narrator, b.duration_hours]
                    elif isinstance(b, ReferenceBook):
                        row = ["ReferenceBook", b.title, b.author, b.isbn, b.year, b.genre,
                               b.available, borrower, b.edition, ""]
                    else:
                        row = ["Book", b.title, b.author, b.isbn, b.year, b.genre,
                               b.available, borrower, "", ""]
                    writer.writerow(row)
                    count += 1
            return count
        except Exception as err:
            print(f"Could not save the library to '{filename}': {err}")
            return 0

    def load_from_csv(self, filename):
        # Rebuild the collection from the CSV, choosing a class per row.
        try:
            loaded = []
            with open(filename, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    kind = row["type"]
                    title = row["title"]
                    author = row["author"]
                    isbn = row["isbn"]
                    year = int(row["year"])
                    genre = row["genre"]
                    extra1 = row["extra1"]
                    extra2 = row["extra2"]

                    if kind == "EBook":
                        book = EBook(title, author, isbn, year, genre, extra1, float(extra2))
                    elif kind == "AudioBook":
                        book = AudioBook(title, author, isbn, year, genre, extra1, float(extra2))
                    elif kind == "ReferenceBook":
                        book = ReferenceBook(title, author, isbn, year, genre, int(extra1))
                    else:
                        book = Book(title, author, isbn, year, genre)

                    # Restore borrow state saved in the CSV.
                    book.available = (row["available"] == "True")
                    book.borrower = row["borrower"] if row["borrower"] else None
                    loaded.append(book)

            # Only replace the collection once the file parsed cleanly.
            self.collection = loaded
            return len(loaded)
        except FileNotFoundError:
            print(f"No existing catalog at '{filename}' yet - starting fresh.")
            return 0
        except ValueError as err:
            print(f"A row in '{filename}' had a bad number and was rejected: {err}")
            return 0
        except Exception as err:
            print(f"Could not load the library from '{filename}': {err}")
            return 0


# ---------------------------------------------------------------------------
# Starter data used to seed an empty library
# ---------------------------------------------------------------------------
def build_starter_collection():
    """Return a mixed list of nine books covering all four types."""
    return [
        Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565", 1925, "Classic Fiction"),
        Book("Educated", "Tara Westover", "978-0399590504", 2018, "Memoir"),
        Book("Dune", "Frank Herbert", "978-0441013593", 1965, "Science Fiction"),
        Book("The Hobbit", "J.R.R. Tolkien", "978-0547928227", 1937, "Fantasy"),
        EBook("Clean Code", "Robert C. Martin", "978-0132350884", 2008, "Programming", "EPUB", 1.2),
        EBook("The Pragmatic Programmer", "Andrew Hunt", "978-0135957059", 2019, "Programming", "PDF", 3.4),
        AudioBook("Becoming", "Michelle Obama", "978-1524763138", 2018, "Memoir", "Michelle Obama", 19.0),
        AudioBook("The Lord of the Rings", "J.R.R. Tolkien", "978-0544003415", 1954, "Fantasy", "Rob Inglis", 11.0),
        ReferenceBook("Chicago Manual of Style", "University of Chicago", "978-0226287058", 2017, "Reference", 17),
    ]


# ---------------------------------------------------------------------------
# Demo: basic Book operations on a plain list
# ---------------------------------------------------------------------------
def run_base_demo():
    """Exercise the required Base-level Book operations on a plain list."""
    collection = [
        Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565", 1925, "Classic Fiction"),
        Book("Educated", "Tara Westover", "978-0399590504", 2018, "Memoir"),
        Book("Dune", "Frank Herbert", "978-0441013593", 1965, "Science Fiction"),
        Book("The Hobbit", "J.R.R. Tolkien", "978-0547928227", 1937, "Fantasy"),
        Book("1984", "George Orwell", "978-0451524935", 1949, "Dystopian"),
        Book("The Silent Patient", "Alex Michaelides", "978-1250301697", 2019, "Thriller"),
    ]

    print("=== Full Collection ===")
    for book in collection:
        print(book)

    print()
    # Check out the first two books to different patrons.
    for patron, book in zip(("Jordan", "Priya"), collection[:2]):
        if book.check_out(patron):
            print(f"'{book.title}' checked out to {patron}.")
        else:
            print(f"'{book.title}' is already checked out.")

    # Try to check out the first book again - it should now refuse.
    if not collection[0].check_out("Sam"):
        print(f"'{collection[0].title}' is already checked out.")

    # Return the second checked-out book.
    print(collection[1].return_book())

    print("\n=== Sorted by Title ===")
    for book in sorted(collection, key=lambda b: b.title):
        print(book)

    print("\n=== Available Books ===")
    for book in [b for b in collection if b.available]:
        print(book)


# ---------------------------------------------------------------------------
# Demo: polymorphism across a mixed list of book types
# ---------------------------------------------------------------------------
def run_polymorphism_demo():
    """Call the same methods on a mixed list to show type-specific behavior."""
    mixed_collection = [
        Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565", 1925, "Classic Fiction"),
        Book("Dune", "Frank Herbert", "978-0441013593", 1965, "Science Fiction"),
        EBook("Clean Code", "Robert C. Martin", "978-0132350884", 2008, "Programming", "EPUB", 1.2),
        EBook("The Pragmatic Programmer", "Andrew Hunt", "978-0135957059", 2019, "Programming", "PDF", 3.4),
        AudioBook("Becoming", "Michelle Obama", "978-1524763138", 2018, "Memoir", "Michelle Obama", 19.0),
        AudioBook("The Lord of the Rings", "J.R.R. Tolkien", "978-0544003415", 1954, "Fantasy", "Rob Inglis", 11.0),
        ReferenceBook("Chicago Manual of Style", "University of Chicago", "978-0226287058", 2017, "Reference", 17),
        ReferenceBook("World Atlas", "National Geographic", "978-1426220586", 2019, "Reference", 11),
    ]

    print("\n--- Polymorphism Demonstration ---")
    for item in mixed_collection:
        print(item)
        result = item.check_out("Test Patron")
        print(f"  check_out result: {result}")
        print(f"  status: {item.get_status()}\n")


# ---------------------------------------------------------------------------
# The interactive command-line menu
# ---------------------------------------------------------------------------
MENU = """
[1] Display all books        [2] Add a book
[3] Check out a book         [4] Return a book
[5] Search by author         [6] Search by genre
[7] Display available books  [8] Generate report
[q] Save and quit
"""


def prompt_add_book(library):
    """Prompt for a book type and its fields, then add it to the library."""
    kind = input("Type (Book/EBook/AudioBook/ReferenceBook): ").strip().lower()
    title = input("Title: ").strip()
    author = input("Author: ").strip()
    isbn = input("ISBN: ").strip()
    try:
        year = int(input("Year: ").strip())
    except ValueError:
        print("Year must be a whole number. Book not added.")
        return

    try:
        if kind == "ebook":
            fmt = input("File format (PDF/EPUB): ").strip()
            size = float(input("File size (MB): ").strip())
            book = EBook(title, author, isbn, year, "General", fmt, size)
        elif kind == "audiobook":
            narrator = input("Narrator: ").strip()
            hours = float(input("Duration (hours): ").strip())
            book = AudioBook(title, author, isbn, year, "General", narrator, hours)
        elif kind == "referencebook":
            edition = int(input("Edition: ").strip())
            book = ReferenceBook(title, author, isbn, year, "Reference", edition)
        else:
            genre = input("Genre: ").strip()
            book = Book(title, author, isbn, year, genre)
    except ValueError:
        print("A numeric field was invalid. Book not added.")
        return

    library.add_book(book)
    print(f"Added '{book.title}'.")


def run_interactive(library):
    """Present the menu loop until the user chooses to save and quit."""
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip().lower()

        if choice in ("q", "quit"):
            written = library.save_to_csv("library.csv")
            print(f"Saved {written} books to library.csv. Goodbye!")
            break

        elif choice == "1":
            for book in library.collection:
                print(book)

        elif choice == "2":
            prompt_add_book(library)

        elif choice == "3":
            isbn = input("ISBN to check out: ").strip()
            book = library.find_by_isbn(isbn)
            if book is None:
                print("No book with that ISBN.")
            else:
                patron = input("Patron name: ").strip()
                if book.check_out(patron):
                    print(f"'{book.title}' checked out to {patron}.")
                else:
                    print(f"'{book.title}' could not be checked out.")

        elif choice == "4":
            isbn = input("ISBN to return: ").strip()
            book = library.find_by_isbn(isbn)
            if book is None:
                print("No book with that ISBN.")
            else:
                print(book.return_book())

        elif choice == "5":
            author = input("Author to search for: ").strip()
            matches = library.find_by_author(author)
            if matches:
                for book in matches:
                    print(book)
            else:
                print("No matching books.")

        elif choice == "6":
            genre = input("Genre to search for: ").strip()
            matches = library.find_by_genre(genre)
            if matches:
                for book in matches:
                    print(book)
            else:
                print("No matching books.")

        elif choice == "7":
            for book in library.get_available_books():
                print(book)

        elif choice == "8":
            print(library.generate_report())

        else:
            print("Unknown option - please choose from the menu.")


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------
def main():
    """Run the base demo, the polymorphism demo, then the interactive menu."""
    print("############ BOOK OPERATIONS DEMO ############\n")
    run_base_demo()

    print("\n\n######## POLYMORPHISM DEMO ########")
    run_polymorphism_demo()

    print("\n######## INTERACTIVE LIBRARY ########")
    library = Library("Riverside Public")
    # Load an existing catalog if present; otherwise seed with starter data.
    if library.load_from_csv("library.csv") == 0 and not library.collection:
        for book in build_starter_collection():
            library.add_book(book)
        print(f"Seeded the library with {len(library.collection)} starter books.")

    run_interactive(library)


if __name__ == "__main__":
    main()
