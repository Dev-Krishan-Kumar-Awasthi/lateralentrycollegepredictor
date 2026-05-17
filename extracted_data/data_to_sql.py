import csv
import sqlite3
import traceback
from pathlib import Path


DB_FILE = "data.db"
CSV_FILES = [
    "college2024.csv",
    "college2025.csv",
]


# -------------------------------------------------------------------
# Database Schema
# -------------------------------------------------------------------

CREATE_SEATINFO_TABLE = """
CREATE TABLE IF NOT EXISTS SeatInfo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    college_name TEXT NOT NULL,

    college_type TEXT NOT NULL
        CHECK (college_type IN ('GOVT', 'Private', 'S.F.I.')),

    branch TEXT NOT NULL,

    opening_rank INTEGER NOT NULL,
    closing_rank INTEGER NOT NULL,

    category TEXT NOT NULL
        CHECK (category IN ('UR', 'OBC', 'SC', 'ST')),

    gender TEXT NOT NULL
        CHECK (gender IN ('M', 'F', 'OP')),

    domicile TEXT NOT NULL
        CHECK (domicile IN ('Y', 'N')),

    total_seats INTEGER NOT NULL,

    year INTEGER NOT NULL
);
"""

CREATE_CGPA_TABLE = """
CREATE TABLE IF NOT EXISTS CgpaRankRange (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    cgpa REAL NOT NULL,

    min_rank INTEGER NOT NULL,
    max_rank INTEGER NOT NULL,

    year INTEGER NOT NULL
);
"""

INSERT_SEATINFO = """
INSERT INTO SeatInfo (
    college_name,
    college_type,
    branch,
    opening_rank,
    closing_rank,
    category,
    gender,
    domicile,
    total_seats,
    year
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


# -------------------------------------------------------------------
# Validation Helpers
# -------------------------------------------------------------------

VALID_COLLEGE_TYPES = {"GOVT", "Private", "S.F.I."}
VALID_CATEGORIES = {"UR", "OBC", "SC", "ST"}
VALID_GENDERS = {"M", "F", "OP"}
VALID_DOMICILE = {"Y", "N"}


def validate_row(
    college_type: str,
    category: str,
    gender: str,
    domicile: str,
) -> None:
    if college_type not in VALID_COLLEGE_TYPES:
        raise ValueError(f"Invalid college_type: {college_type}")

    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category: {category}")

    if gender not in VALID_GENDERS:
        raise ValueError(f"Invalid gender: {gender}")

    if domicile not in VALID_DOMICILE:
        raise ValueError(f"Invalid domicile: {domicile}")


# -------------------------------------------------------------------
# Row Parsing
# -------------------------------------------------------------------

def parse_csv_row(row: list[str]) -> tuple:
    (
        _sno,
        college_name,
        college_type,
        branch,
        _quota,
        opening_rank,
        closing_rank,
        category_field,  # Example: UR/X/F
        domicile,
        total_seats,
        year,
    ) = row

    # category_field format: CATEGORY / something / GENDER
    category, _, gender = category_field.split("/")

    # Normalize whitespace
    college_name = college_name.strip()
    college_type = college_type.strip()
    branch = branch.strip()
    category = category.strip()
    gender = gender.strip()
    domicile = domicile.strip().upper()

    # Validate enum-like values
    validate_row(
        college_type=college_type,
        category=category,
        gender=gender,
        domicile=domicile,
    )

    return (
        college_name,
        college_type,
        branch,
        int(opening_rank),
        int(closing_rank),
        category,
        gender,
        domicile,
        int(total_seats),
        int(year),
    )


# -------------------------------------------------------------------
# CSV Loading
# -------------------------------------------------------------------

def load_csv_to_db(csv_file: str, cursor: sqlite3.Cursor) -> None:
    print(f"Loading {csv_file}...")

    inserted_rows = 0

    with open(csv_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        for line_number, row in enumerate(reader, start=1):
            try:
                data = parse_csv_row(row)
                cursor.execute(INSERT_SEATINFO, data)
                inserted_rows += 1

            except Exception as e:
                print("\n" + "=" * 80)
                print(f"Error while processing file: {csv_file}")
                print(f"Line number: {line_number}")
                print(f"Raw row: {row}")
                print(f"Exception type: {type(e).__name__}")
                print(f"Exception message: {e}")
                print("Full traceback:")
                print(traceback.format_exc())
                print("=" * 80 + "\n")

    print(f"Inserted {inserted_rows} rows from {csv_file}\n")



RANK_CSV_FILES = [
    "rank2024.csv",
    "rank2025.csv",
]

INSERT_CGPA_RANGE = """
INSERT INTO CgpaRankRange (
    cgpa,
    min_rank,
    max_rank,
    year
)
VALUES (?, ?, ?, ?)
"""


def parse_rank_row(row: list[str]) -> tuple:
    """
    Expected CSV format:
    cgpa,min_rank,max_rank,year

    Example:
    8.6938,174,174,2024
    """
    if len(row) != 4:
        raise ValueError(
            f"Expected 4 columns, got {len(row)} columns"
        )

    cgpa, min_rank, max_rank, year = row

    return (
        float(cgpa),
        int(min_rank),
        int(max_rank),
        int(year),
    )


def load_rank_csv_to_db(
    csv_file: str,
    cursor: sqlite3.Cursor
) -> None:
    print(f"Loading CGPA rank file: {csv_file}...")

    inserted_rows = 0

    with open(csv_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        for line_number, row in enumerate(reader, start=1):
            try:
                data = parse_rank_row(row)
                cursor.execute(INSERT_CGPA_RANGE, data)
                inserted_rows += 1

            except Exception as e:
                print("\n" + "=" * 80)
                print(f"Error while processing file: {csv_file}")
                print(f"Line number: {line_number}")
                print(f"Raw row: {row}")
                print(f"Exception type: {type(e).__name__}")
                print(f"Exception message: {e}")
                print(traceback.format_exc())
                print("=" * 80 + "\n")

    print(
        f"Inserted {inserted_rows} rows into "
        f"CgpaRankRange from {csv_file}\n"
    )


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> None:
    conn = sqlite3.connect(DB_FILE)

    try:
        cursor = conn.cursor()

        # Create tables
        cursor.execute(CREATE_SEATINFO_TABLE)
        cursor.execute(CREATE_CGPA_TABLE)

        # Load CSV files
        for csv_file in CSV_FILES:
            if not Path(csv_file).exists():
                print(f"File not found: {csv_file}")
                continue

            load_csv_to_db(csv_file, cursor)

        # Load CGPA-to-rank CSV files
        for csv_file in RANK_CSV_FILES:
            if not Path(csv_file).exists():
                print(f"File not found: {csv_file}")
                continue

            load_rank_csv_to_db(csv_file, cursor)

        # Save all changes
        conn.commit()
        print("Database committed successfully.")

    except Exception as e:
        conn.rollback()
        print("\nDatabase transaction failed.")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {e}")
        print(traceback.format_exc())

    finally:
        conn.close()
        print("Database connection closed.")



if __name__ == "__main__":
    main()