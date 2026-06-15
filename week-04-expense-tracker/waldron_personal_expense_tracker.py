"""
Author: Ryan Waldron
Date: 2026-06-14
Description: Personal Expense Tracker. Saves expense records (date,
description, amount, category) to a CSV file and reads them back each
session. Lets the user add new expenses, search records by keyword,
view spending totals by category, view this month's expenses, and
generate a summary report file.
Tier Attempted: Advanced (Base + Intermediate + Advanced)

Test Output (Run 1 - first run, no expenses.csv present yet,
2 expenses added, one description over 30 characters,
then a case-insensitive search for "food"):

===== Personal Expense Tracker =====

===== Your Expense Records =====
No expenses on record yet.

How many expenses do you want to add? 2

--- Expense 1 ---
Description: Grocery shopping
Amount: $87.45
Category: Food

--- Expense 2 ---
Description: This is a very long description for testing truncation logic
Amount: $49.99
Category: Health

===== Updated Expense Records =====
Date        Description                         Amount  Category
------------------------------------------------------------------
2026-06-14  Grocery shopping                    $87.45  Food
2026-06-14  This is a very long descriptio      $49.99  Health

Would you like to search your expenses? (yes/no): yes
Enter a keyword to search for: food

===== Search Results for 'food' =====
Date        Description                         Amount  Category
------------------------------------------------------------------
2026-06-14  Grocery shopping                    $87.45  Food

===== Spending by Category =====
Food          $   87.45
Health        $   49.99
================================

===== Expenses This Month (2026-06) =====
Date        Description                         Amount  Category
------------------------------------------------------------------
2026-06-14  Grocery shopping                    $87.45  Food
2026-06-14  This is a very long descriptio      $49.99  Health

Report saved to expense_report.txt (15 lines written).

Thank you for using Expense Tracker. Goodbye!

Additional scenarios verified (see conversation log for full transcripts):
- Second run (file already exists) -> both saved expenses reappear,
  confirming the CSV file was written with csv.writer (header row
  included) and read back correctly with csv.reader.
- Entered 0 for "how many expenses do you want to add?" -> the for loop
  ran zero times; existing records displayed unchanged.
- Entered "abc" for an amount -> caught by get_valid_amount()'s
  try/except ValueError and re-prompted until "12.50" was entered.
- Entered "3Food" for a category -> caught by get_valid_category()'s
  .startswith() check and re-prompted until "Transport" was entered.
- Searched for "xyz" (no matches) -> printed "No expenses found matching
  'xyz'." without crashing.
- Entered "two" for "how many expenses do you want to add?" -> the
  top-level except ValueError clause printed "Invalid input encountered:
  invalid literal for int() with base 10: 'two'", and the finally clause
  still printed the goodbye message.
- Manually added a record dated in the prior month directly to
  expenses.csv -> filter_by_month() excluded it from "Expenses This
  Month" while calculate_totals() still included it in the overall
  category totals and report.
- Added a second "Food" expense (Coffee, $4.55) -> calculate_totals()
  combined it with the existing Food total into one tuple ($92.00)
  instead of creating a second "Food" entry, and re-sorted it to the top.
- expense_report.txt was regenerated on every run; its totals, category
  breakdown, and "This Month" section matched the on-screen output, and
  the printed line count matched the file's actual line count each time.
"""

import os
import csv
import datetime


EXPENSES_FILE = "expenses.csv"
REPORT_FILE = "expense_report.txt"


def build_record(description, amount, category):
    """Build one CSV-ready record line from a description, amount, and category."""
    today_str = str(datetime.date.today())
    short_description = description[:30]
    formatted_amount = f"{amount:.2f}"
    fields = [today_str, short_description, formatted_amount, category]
    return ",".join(fields)


def append_record(filename, record_line):
    """Append one record line to the CSV file, writing a header row first if the file is new."""
    file_is_new = not os.path.exists(filename)
    # record_line was joined in build_record(); split it back into fields for csv.writer
    fields = record_line.split(",")
    with open(filename, "a", newline="") as file:
        writer = csv.writer(file)
        if file_is_new:
            writer.writerow(["Date", "Description", "Amount", "Category"])
        writer.writerow(fields)


def load_records(filename):
    """Load saved expense records from a CSV file as a list of [date, description, amount, category] rows."""
    records = []
    if not os.path.exists(filename):
        return records
    try:
        with open(filename, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                if row[0] == "Date":
                    continue
                records.append(row)
    except FileNotFoundError:
        return []
    return records


def display_records(records):
    """Print all expense records in aligned columns, or a message if there are none."""
    if not records:
        print("No expenses on record yet.")
        return
    print(f"{'Date':<12}{'Description':<32}{'Amount':>10}  {'Category'}")
    print("-" * 66)
    for date, description, amount, category in records:
        print(f"{date:<12}{description:<32}{'$' + amount:>10}  {category}")


def search_expenses(records, keyword):
    """Return records whose description or category contains the keyword, case-insensitively."""
    keyword_lower = keyword.lower()
    matches = []
    for record in records:
        description, category = record[1], record[3]
        if keyword_lower in description.lower() or keyword_lower in category.lower():
            matches.append(record)
    return matches


def calculate_totals(records):
    """Return a list of (category, total) tuples, sorted with the highest total first."""
    totals = []
    for record in records:
        category = record[3]
        amount = float(record[2])
        found = False
        for i in range(len(totals)):
            if totals[i][0] == category:
                totals[i] = (category, totals[i][1] + amount)
                found = True
                break
        if not found:
            totals.append((category, amount))
    totals.sort(key=lambda pair: pair[1], reverse=True)
    return totals


def filter_by_month(records, year, month):
    """Return records whose date string falls within the given year and month."""
    matches = []
    for record in records:
        date_string = record[0]
        if date_string[:4] == year and date_string[5:7] == month:
            matches.append(record)
    return matches


def generate_report(records, filename):
    """Write a multi-section summary report to filename and return the number of lines written."""
    today = datetime.date.today()
    total_spending = sum(float(record[2]) for record in records)
    totals = calculate_totals(records)

    year_str = str(today.year)
    month_str = f"{today.month:02d}"
    month_records = filter_by_month(records, year_str, month_str)
    month_spending = sum(float(record[2]) for record in month_records)

    lines = []
    lines.append("=" * 36)
    lines.append("EXPENSE SUMMARY REPORT".center(36))
    lines.append(f"Generated: {today}")
    lines.append("=" * 36)
    lines.append(f"{'Total records':<16}: {len(records)}")
    lines.append(f"{'Total spending':<16}: ${total_spending:.2f}")
    lines.append("")
    lines.append("--- Spending by Category ---")
    for category, total in totals:
        lines.append(f"{category:<16}: ${total:.2f}")
    lines.append("")
    lines.append(f"--- This Month ({year_str}-{month_str}) ---")
    lines.append(f"Records this month: {len(month_records)}")
    lines.append(f"Spending this month: ${month_spending:.2f}")
    lines.append("=" * 36)

    report_text = "\n".join(lines)

    line_count = 0
    with open(filename, "w") as file:
        for line in report_text.splitlines():
            file.write(line + "\n")
            line_count += 1
    return line_count


def get_valid_amount():
    """Prompt for an amount, re-prompting until float() conversion succeeds."""
    while True:
        amount_text = input("Amount: $").strip()
        try:
            return float(amount_text)
        except ValueError:
            print("Please enter a valid number (e.g., 12.50).")


def get_valid_category():
    """Prompt for a category, re-prompting until it starts with a letter."""
    invalid_starts = "0123456789!@#$%^&*()_-+=[]{}|\\;:'\",.<>/?`~"
    while True:
        category = input("Category: ").strip()
        starts_invalid = False
        for char in invalid_starts:
            if category.startswith(char):
                starts_invalid = True
                break
        if not starts_invalid:
            return category
        print("Category must start with a letter, not a digit or special character.")


# ---- Main program ----

print("===== Personal Expense Tracker =====\n")

try:
    records = load_records(EXPENSES_FILE)
    print("===== Your Expense Records =====")
    display_records(records)

    num_new = int(input("\nHow many expenses do you want to add? "))

    for i in range(num_new):
        print(f"\n--- Expense {i + 1} ---")
        description = input("Description: ").strip()
        amount = get_valid_amount()
        category = get_valid_category()

        record_line = build_record(description, amount, category)
        append_record(EXPENSES_FILE, record_line)

    records = load_records(EXPENSES_FILE)
    print("\n===== Updated Expense Records =====")
    display_records(records)

    search_choice = input("\nWould you like to search your expenses? (yes/no): ").strip().lower()
    if search_choice.startswith("y"):
        keyword = input("Enter a keyword to search for: ").strip()
        results = search_expenses(records, keyword)
        print(f"\n===== Search Results for '{keyword}' =====")
        if results:
            display_records(results)
        else:
            print(f"No expenses found matching '{keyword}'.")

    print("\n===== Spending by Category =====")
    totals = calculate_totals(records)
    if not totals:
        print("No spending recorded yet.")
    else:
        for category, total in totals:
            print(f"{category:<14}${total:>8.2f}")
    print("=" * 32)

    today = datetime.date.today()
    year_str = str(today.year)
    month_str = f"{today.month:02d}"
    month_records = filter_by_month(records, year_str, month_str)
    print(f"\n===== Expenses This Month ({year_str}-{month_str}) =====")
    display_records(month_records)

    lines_written = generate_report(records, REPORT_FILE)
    print(f"\nReport saved to {REPORT_FILE} ({lines_written} lines written).")

except FileNotFoundError as error:
    print(f"\nA required file could not be found: {error}")
except ValueError as error:
    print(f"\nInvalid input encountered: {error}")
except Exception as error:
    print(f"\nAn unexpected error occurred: {error}")
finally:
    print("\nThank you for using Expense Tracker. Goodbye!")
