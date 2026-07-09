"""
Author: Ryan Waldron
Date: 2026-07-08
Description: Personal Task & Project Manager backed by a SQLite database.
             Base-level standalone functions manage a single tasks table;
             a TaskManager class adds projects (one-to-many), a LEFT JOIN,
             keyword search, and CSV export; the Advanced layer adds a
             many-to-many tag system, manual-transaction bulk insert with
             rollback, a CSV import, a performance index, and a separate
             DatabaseReport class that builds formatted statistical reports.
Tier Attempted: Advanced (Base + Intermediate + Advanced)

Note: The program deletes and recreates tasks.db at the start of each run so
      the demonstration output is deterministic and reproducible. The final
      tasks.db (advanced state) is included with the submission, along with
      tasks_export.csv (produced by export) and a sample import_tasks.csv.

Recorded test output (from a full run; the report date reflects the run date):

################ BASE LEVEL: standalone functions ################
Task added with ID: 1 ... 6
=== All Tasks ===  (ordered by priority then due_date)
3   Fix login bug             High      Pending     2025-11-15
5   Prepare slide deck        High      Pending     2025-11-22
...
Status updated for task 3: True
Task 6 deleted: True

######## INTERMEDIATE + ADVANCED: TaskManager & DatabaseReport ########
=== All Tasks with Project ===  (LEFT JOIN; "(No Project)" for unlinked)
3   Draft introduction        High      Pending     2025-01-05 Research Paper
6   Read chapter 4            Low       Pending     2027-11-18 (No Project)
=== Project Summary: Research Paper (id 1) ===
Done : 1 | In Progress : 1 | Pending : 1
=== Search results for 'email' ===  (matches title OR description)
4   Update resume  (matched in description)   5   Send follow-up email (title)
Exported 6 rows to tasks_export.csv
Re-tagging task 1 'urgent' returned: False   (duplicate link ignored)
Tasks tagged 'urgent': task 1, task 3        (three-table JOIN)
Tags on task 1: ['urgent', 'work']
bulk_add_tasks inserted 3 tasks
Rollback demo: batch failed (IntegrityError); task count unchanged (9 -> 9)

========================================
          TASK MANAGER REPORT
          Generated: 2026-07-08
========================================
--- Status Summary ---   Pending: 7 | In Progress: 1 | Done: 1
--- Priority Summary --- High: 3 | Medium: 3 | Low: 3
--- Overdue Tasks ---    tasks 1, 3, 5 (past due, not Done)
========================================
Imported 3 tasks from import_tasks.csv
"""

import sqlite3
import csv
import os
import datetime


# ===========================================================================
# Base-level standalone functions - one tasks table
# ===========================================================================
def create_connection(db_file):
    """Open (or create) the SQLite database file; return the connection or None."""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as err:
        print(f"Error connecting to database: {err}")
        return None


def setup_database(conn):
    """Create the tasks table if it does not already exist."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT,
                priority    TEXT    DEFAULT 'Medium',
                status      TEXT    DEFAULT 'Pending',
                due_date    TEXT,
                project_id  INTEGER
            )
        """)
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error setting up database: {err}")


def add_task(conn, title, description, priority, due_date):
    """Insert one task (project_id is always None here); return its new id or None."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, priority, due_date, project_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (title, description, priority, due_date, None))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as err:
        print(f"Error adding task: {err}")
        return None


def get_all_tasks(conn):
    """Return every task row ordered by priority then due date (empty list on error)."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY priority, due_date")
        return cursor.fetchall()
    except sqlite3.Error as err:
        print(f"Error retrieving tasks: {err}")
        return []


def get_tasks_by_status(conn, status):
    """Return all tasks with the given status, ordered by priority."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY priority", (status,))
        return cursor.fetchall()
    except sqlite3.Error as err:
        print(f"Error retrieving tasks by status: {err}")
        return []


def update_task_status(conn, task_id, new_status):
    """Update one task's status; return True if a row was actually changed."""
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as err:
        print(f"Error updating task status: {err}")
        return False


def delete_task(conn, task_id):
    """Delete the task with the given id; return True if a row was deleted."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as err:
        print(f"Error deleting task: {err}")
        return False


def display_tasks(tasks):
    """Print task tuples as an aligned table: ID, Title, Priority, Status, Due Date."""
    if not tasks:
        print("No tasks found.")
        return
    print(f"{'ID':<3} {'Title':<25} {'Priority':<9} {'Status':<11} {'Due Date':<10}")
    print(f"{'-' * 3} {'-' * 25} {'-' * 9} {'-' * 11} {'-' * 10}")
    for row in tasks:
        # row layout: id, title, description, priority, status, due_date, project_id
        task_id, title, _desc, priority, status, due_date, _pid = row
        print(f"{task_id:<3} {title[:25]:<25} {priority:<9} {status:<11} {(due_date or ''):<10}")


# ===========================================================================
# The TaskManager class - projects, joins, search, export, tags, transactions
# ===========================================================================
class TaskManager:
    """Encapsulates every database operation behind a clean method interface."""

    def __init__(self, db_file):
        """Open the connection, enable foreign keys, and create all tables."""
        try:
            self.conn = sqlite3.connect(db_file)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self._setup_tables()
        except sqlite3.Error as err:
            print(f"Error initializing TaskManager: {err}")
            raise

    def _setup_tables(self):
        """Private: create all tables plus a status index; called only from __init__."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT,
                priority    TEXT    DEFAULT 'Medium',
                status      TEXT    DEFAULT 'Pending',
                due_date    TEXT,
                project_id  INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                description TEXT,
                status      TEXT    DEFAULT 'Active',
                due_date    TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT    UNIQUE NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_tags (
                task_id INTEGER NOT NULL,
                tag_id  INTEGER NOT NULL,
                PRIMARY KEY (task_id, tag_id)
            )
        """)
        # Speed up status filters - standard practice on frequently queried columns.
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status)")
        self.conn.commit()

    # --- projects -------------------------------------------------------
    def add_project(self, name, description, due_date):
        """Insert a project row; commit and return the new id."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO projects (name, description, due_date) VALUES (?, ?, ?)",
            (name, description, due_date))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_projects(self):
        """Return all project rows ordered by name."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY name")
        return cursor.fetchall()

    # --- tasks ----------------------------------------------------------
    def add_task(self, title, description, priority, due_date, project_id=None):
        """Insert a task (optionally linked to a project); return the new id."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, priority, due_date, project_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (title, description, priority, due_date, project_id))
        self.conn.commit()
        return cursor.lastrowid

    def get_project_tasks(self, project_id):
        """Return all tasks belonging to one project, ordered by priority then due date."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE project_id = ? ORDER BY priority, due_date",
            (project_id,))
        return cursor.fetchall()

    def get_tasks_with_project_name(self):
        """LEFT JOIN every task with its project name (NULL when it has no project)."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, t.title, t.priority, t.status, t.due_date, p.name
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            ORDER BY t.priority, t.due_date
        """)
        return cursor.fetchall()

    def get_project_summary(self, project_id):
        """GROUP BY: return (status, count) tuples for one project's tasks."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT status, COUNT(*) FROM tasks WHERE project_id = ? GROUP BY status",
            (project_id,))
        return cursor.fetchall()

    def search_tasks(self, keyword):
        """Return tasks whose title OR description contains the keyword (SQL LIKE)."""
        pattern = '%' + keyword + '%'
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE title LIKE ? OR description LIKE ?",
            (pattern, pattern))
        return cursor.fetchall()

    def update_task_status(self, task_id, new_status):
        """Update a task's status; return True if a row was changed."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def export_to_csv(self, filename):
        """Export the joined task/project view to CSV; return the number of data rows."""
        try:
            rows = self.get_tasks_with_project_name()
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Title", "Priority", "Status", "Due Date", "Project"])
                count = 0
                for row in rows:
                    row = list(row)
                    if row[5] is None:               # project name column
                        row[5] = "(No Project)"
                    writer.writerow(row)
                    count += 1
            return count
        except (IOError, sqlite3.Error) as err:
            print(f"Error exporting to CSV: {err}")
            return 0

    # --- tags (many-to-many) -------------------------------------------
    def add_tag(self, name):
        """Insert a tag if new (INSERT OR IGNORE); return its id either way."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
        cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
        row = cursor.fetchone()
        self.conn.commit()
        return row[0] if row else None

    def tag_task(self, task_id, tag_id):
        """Associate a tag with a task; return True if a new link was created."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
            (task_id, tag_id))
        self.conn.commit()
        return cursor.rowcount == 1

    def get_tasks_by_tag(self, tag_name):
        """Three-table JOIN: return all tasks carrying the given tag name."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.*
            FROM tasks t
            JOIN task_tags tt ON t.id = tt.task_id
            JOIN tags tg      ON tt.tag_id = tg.id
            WHERE tg.name = ?
        """, (tag_name,))
        return cursor.fetchall()

    def get_tags_for_task(self, task_id):
        """Return a flat list of tag-name strings attached to one task."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT tg.name
            FROM task_tags tt
            JOIN tags tg ON tt.tag_id = tg.id
            WHERE tt.task_id = ?
        """, (task_id,))
        return [row[0] for row in cursor.fetchall()]

    # --- transactions ---------------------------------------------------
    def bulk_add_tasks(self, tasks_list):
        """Insert many tasks in one manual transaction; roll back and re-raise on error."""
        count = 0
        try:
            self.conn.isolation_level = None          # manual transaction control
            self.conn.execute("BEGIN")
            for task in tasks_list:
                self.conn.execute(
                    "INSERT INTO tasks (title, description, priority, due_date, project_id) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (task["title"], task.get("description"), task.get("priority", "Medium"),
                     task.get("due_date"), task.get("project_id")))
                count += 1
            self.conn.execute("COMMIT")
            return count
        except sqlite3.Error:
            self.conn.execute("ROLLBACK")
            raise
        finally:
            self.conn.isolation_level = ""            # restore default behavior

    def import_from_csv(self, filename):
        """Read a CSV with DictReader and insert its rows via one bulk transaction."""
        try:
            tasks_list = []
            with open(filename, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_pid = (row.get("project_id") or "").strip()
                    project_id = int(raw_pid) if raw_pid else None
                    tasks_list.append({
                        "title": row["title"],
                        "description": row.get("description"),
                        "priority": row.get("priority", "Medium"),
                        "due_date": row.get("due_date"),
                        "project_id": project_id,
                    })
            return self.bulk_add_tasks(tasks_list)
        except FileNotFoundError:
            print(f"Import file '{filename}' not found - nothing imported.")
            return 0
        except csv.Error as err:
            print(f"CSV error while importing: {err}")
            return 0
        except sqlite3.Error as err:
            print(f"Database error while importing: {err}")
            return 0

    def close(self):
        """Close the underlying database connection."""
        self.conn.close()


# ===========================================================================
# The DatabaseReport class - formatted statistics, composed with TaskManager
# ===========================================================================
class DatabaseReport:
    """Builds formatted report strings from a TaskManager's connection (never prints)."""

    def __init__(self, task_manager):
        """Store the TaskManager instance; all queries use self.tm.conn."""
        self.tm = task_manager

    def get_status_summary(self):
        """Return a formatted count of tasks grouped by status."""
        cursor = self.tm.conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        rows = cursor.fetchall()
        if not rows:
            return "No tasks in database."
        lines = ["--- Status Summary ---"]
        for status, count in rows:
            lines.append(f"{status:<12}: {count} task(s)")
        return "\n".join(lines)

    def get_priority_summary(self):
        """Return a formatted count by priority, ordered High > Medium > Low."""
        cursor = self.tm.conn.cursor()
        cursor.execute("""
            SELECT priority, COUNT(*) FROM tasks GROUP BY priority
            ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END
        """)
        rows = cursor.fetchall()
        lines = ["--- Priority Summary ---"]
        for priority, count in rows:
            lines.append(f"{priority:<12}: {count} task(s)")
        return "\n".join(lines)

    def get_overdue_tasks(self):
        """Return tasks past their due date and not yet Done (date compared in SQL)."""
        cursor = self.tm.conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE due_date < date('now') AND status != 'Done'")
        return cursor.fetchall()

    def _format_overdue(self):
        """Return the overdue section as an aligned block of text."""
        rows = self.get_overdue_tasks()
        lines = ["--- Overdue Tasks ---"]
        if not rows:
            lines.append("No overdue tasks.")
            return "\n".join(lines)
        lines.append(f"{'ID':<3} {'Title':<25} {'Priority':<9} {'Due Date':<10}")
        lines.append(f"{'-' * 3} {'-' * 25} {'-' * 9} {'-' * 10}")
        for row in rows:
            task_id, title, _desc, priority, _status, due_date, _pid = row
            lines.append(f"{task_id:<3} {title[:25]:<25} {priority:<9} {(due_date or ''):<10}")
        return "\n".join(lines)

    def generate_full_report(self):
        """Combine all summaries into one titled, multi-line report string."""
        line = "=" * 40
        today = datetime.date.today().isoformat()
        parts = [
            line,
            "          TASK MANAGER REPORT",
            f"          Generated: {today}",
            line,
            self.get_status_summary(),
            "",
            self.get_priority_summary(),
            "",
            self._format_overdue(),
            line,
        ]
        return "\n".join(parts)


# ===========================================================================
# Display helper for the JOIN view (task + project name)
# ===========================================================================
def display_tasks_with_project(rows):
    """Print the LEFT JOIN result as an aligned table including the Project column."""
    if not rows:
        print("No tasks found.")
        return
    print(f"{'ID':<3} {'Title':<25} {'Priority':<9} {'Status':<11} {'Due Date':<10} Project")
    print(f"{'-' * 3} {'-' * 25} {'-' * 9} {'-' * 11} {'-' * 10} {'-' * 13}")
    for row in rows:
        task_id, title, priority, status, due_date, project = row
        project = project if project else "(No Project)"
        print(f"{task_id:<3} {title[:25]:<25} {priority:<9} {status:<11} "
              f"{(due_date or ''):<10} {project}")


# ===========================================================================
# Demo 1: base-level standalone functions
# ===========================================================================
def run_base_demo(db_file):
    """Exercise the required Base-level functions on a single tasks table."""
    print("################ BASE LEVEL: standalone functions ################\n")
    conn = create_connection(db_file)
    if conn is None:
        print("Could not open the database. Stopping base demo.")
        return
    setup_database(conn)

    starter = [
        ("Write project proposal", "Draft the Q4 proposal", "Medium", "2025-11-20"),
        ("Update resume", "Refresh work history", "Low", "2025-12-01"),
        ("Fix login bug", "Users cannot log in on mobile", "High", "2025-11-15"),
        ("Plan team lunch", "Pick a date and venue", "Low", "2025-11-28"),
        ("Prepare slide deck", "Quarterly review slides", "High", "2025-11-22"),
        ("Archive old files", "Clear last year's folder", "Medium", "2025-12-05"),
    ]
    ids = []
    for title, desc, priority, due in starter:
        new_id = add_task(conn, title, desc, priority, due)
        ids.append(new_id)
        print(f"Task added with ID: {new_id}")

    print("\n=== All Tasks ===")
    display_tasks(get_all_tasks(conn))

    print("\n=== Pending Tasks ===")
    display_tasks(get_tasks_by_status(conn, "Pending"))

    updated = update_task_status(conn, ids[2], "In Progress")
    print(f"\nStatus updated for task {ids[2]}: {updated}")

    deleted = delete_task(conn, ids[5])
    print(f"Task {ids[5]} deleted: {deleted}")

    print("\n=== All Tasks (after update and delete) ===")
    display_tasks(get_all_tasks(conn))

    conn.close()


# ===========================================================================
# Demo 2: TaskManager + DatabaseReport (intermediate + advanced)
# ===========================================================================
def run_manager_demo(db_file, import_csv):
    """Exercise the TaskManager and DatabaseReport classes end to end."""
    print("\n\n######## INTERMEDIATE + ADVANCED: TaskManager & DatabaseReport ########\n")
    try:
        tm = TaskManager(db_file)
    except sqlite3.Error:
        print("Could not initialize the TaskManager. Stopping.")
        return

    # Projects
    p1 = tm.add_project("Research Paper", "Term research paper", "2025-12-10")
    p2 = tm.add_project("Job Search", "Applications and follow-ups", "2025-12-31")
    print(f"Project added with ID: {p1}")
    print(f"Project added with ID: {p2}")

    # Tasks - a mix across both projects plus one with no project
    t1 = tm.add_task("Write project proposal", "Outline the paper", "High", "2025-02-10", p1)
    t2 = tm.add_task("Find three sources", "Library and online search", "Medium", "2027-11-25", p1)
    t3 = tm.add_task("Draft introduction", "First 500 words", "High", "2025-01-05", p1)
    t4 = tm.add_task("Update resume", "Email the resume to references", "Low", "2027-12-01", p2)
    t5 = tm.add_task("Send follow-up email", "Ping the recruiter", "Medium", "2025-03-18", p2)
    t6 = tm.add_task("Read chapter 4", "Personal reading goal", "Low", "2027-11-18", None)
    print(f"Task IDs added: {[t1, t2, t3, t4, t5, t6]}")

    # Give the collection a mix of statuses
    tm.update_task_status(t1, "In Progress")
    tm.update_task_status(t2, "Done")

    print("\n=== All Tasks with Project ===")
    display_tasks_with_project(tm.get_tasks_with_project_name())

    print(f"\n=== Project Summary: Research Paper (id {p1}) ===")
    for status, count in tm.get_project_summary(p1):
        print(f"{status:<12}: {count}")

    print("\n=== Search results for 'email' ===")
    display_tasks(tm.search_tasks("email"))

    exported = tm.export_to_csv("tasks_export.csv")
    print(f"\nExported {exported} rows to tasks_export.csv")

    # Tags (many-to-many)
    tag_urgent = tm.add_tag("urgent")
    tag_work = tm.add_tag("work")
    tag_personal = tm.add_tag("personal")
    tm.add_tag("urgent")   # duplicate: INSERT OR IGNORE returns the existing id
    print(f"\nTag IDs (urgent, work, personal): {tag_urgent}, {tag_work}, {tag_personal}")

    tm.tag_task(t1, tag_urgent)
    tm.tag_task(t1, tag_work)
    tm.tag_task(t3, tag_urgent)
    tm.tag_task(t6, tag_personal)
    first_link_repeated = tm.tag_task(t1, tag_urgent)  # already exists -> False
    print(f"Re-tagging task {t1} 'urgent' returned: {first_link_repeated}")

    print("\n=== Tasks tagged 'urgent' ===")
    display_tasks(tm.get_tasks_by_tag("urgent"))

    print(f"\nTags on task {t1}: {tm.get_tags_for_task(t1)}")

    # Bulk insert in one transaction
    bulk = [
        {"title": "Book flight", "description": "Conference travel", "priority": "Medium", "due_date": "2027-09-01"},
        {"title": "Renew license", "description": "Driver's license", "priority": "High", "due_date": "2027-09-15"},
        {"title": "Water plants", "description": "Weekly chore", "priority": "Low", "due_date": "2027-09-20"},
    ]
    inserted = tm.bulk_add_tasks(bulk)
    print(f"\nbulk_add_tasks inserted {inserted} tasks")

    # Demonstrate transaction rollback: one bad row must undo the whole batch
    before = len(tm.get_tasks_with_project_name())
    bad_batch = [
        {"title": "Good task", "description": "ok", "priority": "Low", "due_date": "2027-10-01"},
        {"title": None, "description": "missing title violates NOT NULL", "priority": "Low", "due_date": "2027-10-02"},
    ]
    try:
        tm.bulk_add_tasks(bad_batch)
    except sqlite3.Error as err:
        after = len(tm.get_tasks_with_project_name())
        print(f"Rollback demo: batch failed ({type(err).__name__}); "
              f"task count unchanged ({before} -> {after})")

    # Full statistical report
    report = DatabaseReport(tm)
    print("\n" + report.generate_full_report())

    # CSV import (sample file shipped with the submission)
    if os.path.exists(import_csv):
        imported = tm.import_from_csv(import_csv)
        print(f"\nImported {imported} tasks from {import_csv}")
    else:
        print(f"\n{import_csv} not present - skipping import step")

    tm.close()


# ===========================================================================
# Main program
# ===========================================================================
def main():
    """Reset the database for a reproducible run, then run both demos."""
    db_file = "tasks.db"

    # Fresh start so IDs and output are deterministic each run.
    if os.path.exists(db_file):
        os.remove(db_file)
    run_base_demo(db_file)

    # Recreate the file cleanly for the class-based (multi-table) schema.
    if os.path.exists(db_file):
        os.remove(db_file)
    run_manager_demo(db_file, "import_tasks.csv")


if __name__ == "__main__":
    main()
