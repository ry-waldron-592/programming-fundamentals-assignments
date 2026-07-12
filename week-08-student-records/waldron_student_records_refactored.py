# =============================================================================
# Student Record Management System  --  REFACTORED (OBJECT-ORIENTED) VERSION
# Programming Fundamentals with Python - Week 8 Refactoring Exercise
#
# This is the clean redesign of student_records_fixed.py.  The external
# behaviour is identical (same menu, same output, same students.csv), but the
# flat top-down script has been rebuilt around two classes:
#
#   * Student        - represents a single student record.
#   * StudentRoster  - owns the list of students and provides every menu action.
#
# The linear search has been replaced with a binary search, file access is
# wrapped in exception handling, and user input is normalised with string
# operations.  A GraduateStudent subclass is included as the bonus (R-08).
# =============================================================================

import csv


class Student:
    """A single student record with its five data fields."""

    def __init__(self, student_id, student_name, major, gpa, total_credits):
        """Store each field as an instance attribute, trimming stray whitespace."""
        self.student_id = student_id.strip()
        self.student_name = student_name.strip()
        self.major = major.strip()
        self.gpa = gpa.strip()
        self.total_credits = total_credits.strip()

    def __str__(self):
        """Return the multi-line detail block used when a student is found."""
        return (
            f"  Student ID    : {self.student_id}\n"
            f"  Student Name  : {self.student_name}\n"
            f"  Major         : {self.major}\n"
            f"  GPA           : {self.gpa}\n"
            f"  Total Credits : {self.total_credits}"
        )

    def table_row(self, row_number):
        """Return this student formatted as one row of the listing table."""
        return (
            f"{row_number:<5}"
            f"{self.student_id:<12}"
            f"{self.student_name:<22}"
            f"{self.major:<24}"
            f"{self.gpa:<6}"
            f"{self.total_credits}"
        )


class GraduateStudent(Student):
    """A Student pursuing a graduate degree, extended with a thesis topic (bonus R-08)."""

    def __init__(self, student_id, student_name, major, gpa, total_credits, thesis_topic):
        """Initialise the shared student fields, then add the thesis topic."""
        super().__init__(student_id, student_name, major, gpa, total_credits)
        self.thesis_topic = thesis_topic.strip()

    def __str__(self):
        """Return the base detail block plus an extra thesis-topic line."""
        return f"{super().__str__()}\n  Thesis Topic  : {self.thesis_topic}"


class StudentRoster:
    """Manages the collection of students and carries out each menu action."""

    def __init__(self):
        """Start with an empty roster and no CSV loaded."""
        self.students = []          # List of Student objects, kept sorted by ID
        self.csv_loaded = False     # True once a file has been loaded successfully
        self.filename = ""          # Name of the most recently loaded file

    def load_csv(self, filename):
        """Read student records from a CSV file, replacing any current roster."""
        students = []
        try:
            with open(filename, newline="") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    # A row missing an expected column raises KeyError, handled below.
                    students.append(
                        Student(
                            row["StudentID"],
                            row["StudentName"],
                            row["Major"],
                            row["GPA"],
                            row["TotalCredits"],
                        )
                    )
        except FileNotFoundError:
            print()
            print(f"Error: could not find a file named '{filename}'. Please try again.")
            return
        except (KeyError, csv.Error) as error:
            print()
            print(f"Error: '{filename}' is not in the expected format ({error}).")
            return

        # Sort by normalised ID so the binary search always works on ordered data.
        students.sort(key=lambda student: student.student_id.upper())

        self.students = students
        self.filename = filename
        self.csv_loaded = True

        print()
        print(f"Success! {len(self.students)} student record(s) loaded from '{filename}'.")

    def list_students(self):
        """Print every loaded student in a numbered, formatted table."""
        if not self.csv_loaded:
            print()
            print("No data loaded. Please use Option 1 to read a CSV file first.")
            return

        print()
        print("-" * 80)
        print(f"{'#':<5} {'Student ID':<12} {'Student Name':<22} {'Major':<24} {'GPA':<6} {'Credits'}")
        print("-" * 82)

        row_number = 1
        for student in self.students:
            print(student.table_row(row_number))
            row_number += 1

        print("-" * 82)
        print(f"Total records: {len(self.students)}")

    def search_by_id(self, search_id):
        """Find and display one student by ID using a binary search."""
        if not self.csv_loaded:
            print()
            print("No data loaded. Please use Option 1 to read a CSV file first.")
            return

        # Normalise the query so the search is case-insensitive and space-tolerant.
        target_id = search_id.strip().upper()

        match = None
        low = 0
        high = len(self.students) - 1
        while low <= high:                      # keep halving until the window is empty
            mid = (low + high) // 2
            current_id = self.students[mid].student_id.upper()
            if current_id == target_id:
                match = self.students[mid]
                break                           # found it; stop searching
            elif current_id < target_id:
                low = mid + 1                   # target must be in the upper half
            else:
                high = mid - 1                  # target must be in the lower half

        print()
        if match is None:
            print(f"No student found with ID '{search_id}'.")
        else:
            print("Student found!")
            print("-" * 40)
            print(match)
            print("-" * 40)

    def run(self):
        """Display the menu and dispatch user choices until the user exits."""
        print("=" * 60)
        print("   Student Record Management System")
        print("=" * 60)

        while True:
            print()
            print("Please select an option:")
            print("  1. Read CSV")
            print("  2. List CSV Contents")
            print("  3. Search for Student by ID")
            print("  4. Exit")
            print()

            menu_choice = input("Enter your choice (1-4): ").strip()

            if menu_choice == "1":
                filename = input("Enter the CSV filename (e.g., students.csv): ").strip()
                self.load_csv(filename)
            elif menu_choice == "2":
                self.list_students()
            elif menu_choice == "3":
                search_id = input("Enter the Student ID to search for: ").strip()
                self.search_by_id(search_id)
            elif menu_choice == "4":
                print()
                print("Thank you for using the Student Record Management System. Goodbye!")
                break
            else:
                print()
                print(f"'{menu_choice}' is not a valid option. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    roster = StudentRoster()
    roster.run()
