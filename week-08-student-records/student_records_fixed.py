# =============================================================================
# Student Record Management System  --  DEBUGGED / FIXED VERSION
# Programming Fundamentals with Python - Week 8 Refactoring Exercise
#
# This program reads student data from a CSV file and provides a menu-driven
# interface to list all students and search for a student by ID.
#
# This file is the ORIGINAL top-down program with all 10 deliberately
# introduced bugs corrected.  The structure (global variables, single main
# loop) is intentionally unchanged so it can be compared against the original.
# The clean object-oriented redesign lives in waldron_student_records_refactored.py.
# Each fix below is tagged  # BUGFIX n  and documented in bug_report.txt.
# =============================================================================

import csv

# -----------------------------------------------------------------------------
# Global Variables
# -----------------------------------------------------------------------------
student_records = []        # Holds all student records loaded from the CSV
csv_filename = ""           # Stores the filename entered by the user
menu_choice = ""            # Stores the user's menu selection
csv_loaded = False          # Tracks whether a CSV file has been loaded

search_id = ""              # Stores the Student ID entered during a search
found_student = None        # Stores the matching student record, if found
search_index = 0            # Loop counter used during linear search

row_number = 0              # Loop counter used when printing student records
current_student = None      # Holds the current record during iteration

student_id = ""             # Fields parsed from each CSV row
student_name = ""
major = ""
gpa = ""
total_credits = ""

# =============================================================================
# Main Program Loop
# =============================================================================

print("=" * 60)
print("   Student Record Management System")
print("=" * 60)

while True:

    # -------------------------------------------------------------------------
    # Display Menu
    # -------------------------------------------------------------------------
    print()
    print("Please select an option:")
    print("  1. Read CSV")
    print("  2. List CSV Contents")
    print("  3. Search for Student by ID")
    print("  4. Exit")
    print()

    menu_choice = input("Enter your choice (1-4): ").strip()

    # =========================================================================
    # Option 1: Read CSV
    # =========================================================================
    if menu_choice == "1":

        csv_filename = input("Enter the CSV filename (e.g., students.csv): ").strip()

        student_records = []        # BUGFIX 3: reset so re-loading does not duplicate records

        csv_file = open(csv_filename, newline="")
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            student_id     = row["StudentID"]
            student_name   = row["StudentName"]
            major          = row["Major"]
            gpa            = row["GPA"]
            total_credits  = row["TotalCredits"]

            student_record = {
                "StudentID"    : student_id,
                "StudentName"  : student_name,
                "Major"        : major,
                "GPA"          : gpa,
                "TotalCredits" : total_credits
            }

            student_records.append(student_record)

        csv_file.close()            # BUGFIX 1: close AFTER iterating the reader, not before

        csv_loaded = True           # BUGFIX 4: mark data as loaded so Options 2 and 3 work

        print()
        print(f"Success! {len(student_records)} student record(s) loaded from '{csv_filename}'.")

    # =========================================================================
    # Option 2: List CSV Contents
    # =========================================================================
    elif menu_choice == "2":

        if not csv_loaded:
            print()
            print("No data loaded. Please use Option 1 to read a CSV file first.")

        else:
            print()
            print("-" * 80)
            print(f"{'#':<5} {'Student ID':<12} {'Student Name':<22} {'Major':<24} {'GPA':<6} {'Credits'}")
            print("-" * 82)

            row_number = 1

            for current_student in student_records:
                print(
                    f"{row_number:<5}"
                    f"{current_student['StudentID']:<12}"
                    f"{current_student['StudentName']:<22}"
                    f"{current_student['Major']:<24}"
                    f"{current_student['GPA']:<6}"
                    f"{current_student['TotalCredits']}"
                )
                row_number = row_number + 1     # BUGFIX 7: advance the row counter each iteration

            print("-" * 82)
            print(f"Total records: {len(student_records)}")

    # =========================================================================
    # Option 3: Search for Student by ID
    # =========================================================================
    elif menu_choice == "3":

        if not csv_loaded:
            print()
            print("No data loaded. Please use Option 1 to read a CSV file first.")

        else:
            search_id = input("Enter the Student ID to search for: ").strip()

            found_student = None        # BUGFIX 6: clear any result from a previous search
            search_index = 0

            while search_index < len(student_records):      # BUGFIX 5: use < to stay in range
                # BUGFIX 9: upper-case BOTH sides so the search is case-insensitive
                if student_records[search_index]["StudentID"].upper() == search_id.upper():
                    found_student = student_records[search_index]
                    search_index = len(student_records)      # BUGFIX 10: truly end the loop
                else:
                    search_index = search_index + 1

            print()

            if found_student is None:
                print(f"No student found with ID '{search_id}'.")
            else:
                print("Student found!")
                print("-" * 40)
                print(f"  Student ID    : {found_student['StudentID']}")   # BUGFIX 2: correct key
                print(f"  Student Name  : {found_student['StudentName']}")
                print(f"  Major         : {found_student['Major']}")
                print(f"  GPA           : {found_student['GPA']}")
                print(f"  Total Credits : {found_student['TotalCredits']}")
                print("-" * 40)

    # =========================================================================
    # Option 4: Exit
    # =========================================================================
    elif menu_choice == "4":        # BUGFIX 8: compare to the string "4", not the integer 4
        print()
        print("Thank you for using the Student Record Management System. Goodbye!")
        break

    # =========================================================================
    # Invalid Input
    # =========================================================================
    else:
        print()
        print(f"'{menu_choice}' is not a valid option. Please enter 1, 2, 3, or 4.")
