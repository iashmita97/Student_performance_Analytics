"""
functions.py - reusable data-processing and calculation functions.

This file contains NO Streamlit code. Keeping the calculations separate from
the web interface (app.py) means they can be tested on their own with
test_functions.py.

Libraries used:
    * pandas - loading the CSV file, DataFrames, filtering
    * NumPy  - numerical calculations (sums, means, minimum, maximum)
"""

from pathlib import Path

import numpy as np
import pandas as pd

# =============================================================================
# CONFIGURATION - all grading and policy rules live in this one section.
#
# IMPORTANT: The grade boundaries, pass rules and attendance threshold below
# are PROVISIONAL ASSUMPTIONS made for this project. They are NOT verified
# official college rules. To use different rules, change only the values here;
# the rest of the program (and the web app) will follow automatically.
# =============================================================================

# Column names expected in students.csv
TEXT_COLUMNS = ["Student_ID", "Name", "Department"]
SUBJECT_COLUMNS = ["Mathematics", "Python", "Computer_Science", "English"]
ATTENDANCE_COLUMN = "Attendance"
REQUIRED_COLUMNS = TEXT_COLUMNS + SUBJECT_COLUMNS + [ATTENDANCE_COLUMN]

# Marks scheme: four subjects, each worth 100 marks -> maximum total of 400.
NUMBER_OF_SUBJECTS = len(SUBJECT_COLUMNS)
MAX_MARKS_PER_SUBJECT = 100
MAX_TOTAL_MARKS = NUMBER_OF_SUBJECTS * MAX_MARKS_PER_SUBJECT
MIN_VALUE = 0  # marks and attendance may not be below this
MAX_VALUE = 100  # marks and attendance may not be above this

# Grade boundaries, checked from the highest grade downwards.
# Each pair is (minimum average needed, grade).
#   A: 90-100 | B: 80 to below 90 | C: 70 to below 80
#   D: 60 to below 70 | E: 40 to below 60 | F: below 40
GRADE_BOUNDARIES = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (40, "E"),
]
LOWEST_GRADE = "F"

# Pass policy: BOTH conditions must be true to pass.
#   1. at least PASS_MARK_PER_SUBJECT marks in every subject, AND
#   2. an overall average of at least PASS_AVERAGE.
# (This is separate from the grade boundaries above, even though the numbers
# 40 and the "E" boundary happen to match.)
PASS_MARK_PER_SUBJECT = 35
PASS_AVERAGE = 40

# A student is flagged as "low attendance" when attendance is BELOW this value.
# Attendance is never used as a pass/fail condition.
LOW_ATTENDANCE_THRESHOLD = 75

# Averages are rounded to this many decimals ONLY when comparing students, so
# tiny floating-point differences (e.g. 85.25 vs 85.25000000000001) do not
# break ties.
COMPARISON_DECIMALS = 6

# Columns of the final processed results table (also used for the CSV download)
CALCULATED_COLUMNS = ["Total", "Average", "Grade", "Result", "Rank", "Low_Attendance"]
RESULT_COLUMNS = REQUIRED_COLUMNS + CALCULATED_COLUMNS

# The default data file sits in the same folder as this script, so the path
# works on any computer (no absolute paths).
DEFAULT_DATA_FILE = Path(__file__).resolve().parent / "students.csv"


# =============================================================================
# ERROR TYPE
# =============================================================================
class DataValidationError(Exception):
    """Raised when the student data is missing, malformed or invalid.

    The attribute `problems` is a list of readable messages, so the web app
    can show every problem to the user instead of only the first one.
    """

    def __init__(self, problems):
        if isinstance(problems, str):
            problems = [problems]
        self.problems = list(problems)
        super().__init__("; ".join(self.problems))


# =============================================================================
# 1. LOADING AND VALIDATING DATA
# =============================================================================
def _is_missing(value):
    """True if a cell is empty, None, NaN or only spaces."""
    if value is None:
        return True
    if pd.isna(value):
        return True
    return str(value).strip() == ""


def find_data_problems(df):
    """Check a DataFrame and return a list of problem messages.

    An empty list means the data is valid. Nothing is changed or "fixed";
    invalid data is only reported, never replaced with invented values.
    Line numbers refer to the CSV file (line 1 is the header).
    """
    problems = []

    # --- Missing columns: nothing else can be checked without them ---------
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        problems.append("Missing required column(s): " + ", ".join(missing_columns) + ".")
        return problems

    if len(df) == 0:
        problems.append("The file has a header but contains no student rows.")
        return problems

    # --- Missing values in any required column -----------------------------
    for column in REQUIRED_COLUMNS:
        for position, value in enumerate(df[column]):
            if _is_missing(value):
                problems.append(f"Line {position + 2}: missing value in '{column}'.")

    # --- Marks and attendance must be numbers between 0 and 100 ------------
    for column in SUBJECT_COLUMNS + [ATTENDANCE_COLUMN]:
        numbers = pd.to_numeric(df[column], errors="coerce")  # bad text -> NaN
        for position in range(len(df)):
            original = df[column].iloc[position]
            if _is_missing(original):
                continue  # already reported above
            number = numbers.iloc[position]
            line = position + 2
            if pd.isna(number) or not np.isfinite(number):
                problems.append(f"Line {line}: '{original}' in '{column}' is not a valid number.")
            elif number < MIN_VALUE or number > MAX_VALUE:
                problems.append(
                    f"Line {line}: {column} value {original} is outside the "
                    f"allowed range {MIN_VALUE}-{MAX_VALUE}."
                )

    # --- Student IDs must be unique ----------------------------------------
    first_seen_on_line = {}
    for position, value in enumerate(df["Student_ID"]):
        if _is_missing(value):
            continue  # already reported above
        student_id = str(value).strip()
        line = position + 2
        if student_id in first_seen_on_line:
            problems.append(
                f"Line {line}: duplicate Student_ID '{student_id}' "
                f"(first used on line {first_seen_on_line[student_id]})."
            )
        else:
            first_seen_on_line[student_id] = line

    return problems


def validate_students(df):
    """Return a clean copy of the data, or raise DataValidationError.

    The returned DataFrame has only the required columns, trimmed text, and
    numeric marks/attendance.
    """
    problems = find_data_problems(df)
    if problems:
        raise DataValidationError(problems)

    clean = df[REQUIRED_COLUMNS].copy()
    for column in TEXT_COLUMNS:
        clean[column] = clean[column].astype(str).str.strip()
    for column in SUBJECT_COLUMNS + [ATTENDANCE_COLUMN]:
        clean[column] = pd.to_numeric(clean[column])
    return clean.reset_index(drop=True)


def load_students(file_path=DEFAULT_DATA_FILE):
    """Read the CSV file with pandas, validate it and return a DataFrame.

    Raises DataValidationError with a readable message if the file is
    missing, empty, malformed or contains invalid data.
    """
    path = Path(file_path)
    if not path.is_file():
        raise DataValidationError(
            f"The data file '{path.name}' was not found. "
            "Place it in the same folder as app.py."
        )

    try:
        # Everything is read as text first so that invalid entries such as
        # "abc" are detected by validation instead of being changed silently.
        raw = pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
            skipinitialspace=True,
        )
    except pd.errors.EmptyDataError:
        raise DataValidationError(f"The file '{path.name}' is empty.") from None
    except pd.errors.ParserError as error:
        raise DataValidationError(
            f"The file '{path.name}' is not a well-formed CSV file: {error}"
        ) from None
    except UnicodeDecodeError:
        raise DataValidationError(
            f"The file '{path.name}' could not be read. Save it as a UTF-8 CSV file."
        ) from None

    raw.columns = [str(name).strip() for name in raw.columns]
    return validate_students(raw)


# =============================================================================
# 2-5. TOTAL, AVERAGE, GRADE, RESULT
# =============================================================================
def calculate_total_marks(df):
    """Total marks of each student = sum of the four subject marks (max 400)."""
    marks = df[SUBJECT_COLUMNS].to_numpy()  # 2D NumPy array: one row per student
    totals = np.sum(marks, axis=1)  # add up each row
    return pd.Series(totals, index=df.index, name="Total")


def calculate_average_marks(df):
    """Average marks of each student = total marks / 4."""
    averages = calculate_total_marks(df) / NUMBER_OF_SUBJECTS
    return averages.rename("Average")


def assign_grade(average):
    """Return the grade letter for one student's average marks."""
    if not (MIN_VALUE <= average <= MAX_VALUE):  # also catches NaN
        raise ValueError(f"Average must be between {MIN_VALUE} and {MAX_VALUE}, got {average}.")
    for minimum_average, grade in GRADE_BOUNDARIES:
        if average >= minimum_average:
            return grade
    return LOWEST_GRADE


def get_fail_reasons(subject_marks, average):
    """Return a list of reasons why a student fails (empty list = passes).

    subject_marks: dict (or Series) of {subject name: marks}.
    """
    reasons = []
    for subject, marks in subject_marks.items():
        if marks < PASS_MARK_PER_SUBJECT:
            reasons.append(
                f"{subject.replace('_', ' ')}: {marks:g} is below the "
                f"subject pass mark of {PASS_MARK_PER_SUBJECT}."
            )
    if average < PASS_AVERAGE:
        reasons.append(
            f"Overall average {average:.2f} is below the required average of {PASS_AVERAGE}."
        )
    return reasons


def determine_result(subject_marks, average):
    """Return "Pass" or "Fail" using the provisional pass policy."""
    if get_fail_reasons(subject_marks, average):
        return "Fail"
    return "Pass"


def calculate_ranks(averages):
    """Rank students by average (1 = best). Equal averages share a rank.

    Example: averages 95, 95, 90 give ranks 1, 1, 3 ("competition ranking").
    """
    rounded = averages.round(COMPARISON_DECIMALS)
    return rounded.rank(method="min", ascending=False).astype(int)


def _check_threshold(threshold):
    """Make sure an attendance threshold is a number from 0 to 100."""
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float, np.integer, np.floating)):
        raise ValueError("The attendance threshold must be a number.")
    if not (MIN_VALUE <= threshold <= MAX_VALUE):
        raise ValueError(f"The attendance threshold must be between {MIN_VALUE} and {MAX_VALUE}.")


def process_students(df, attendance_threshold=LOW_ATTENDANCE_THRESHOLD):
    """Validate the data and add all calculated columns.

    Added columns: Total, Average, Grade, Result, Rank, Low_Attendance.
    The input DataFrame is not modified.
    """
    _check_threshold(attendance_threshold)
    results = validate_students(df)  # raises an error if the data is invalid

    results["Total"] = calculate_total_marks(results)
    results["Average"] = calculate_average_marks(results)

    # Grade and result are worked out student by student with a loop.
    marks_per_student = results[SUBJECT_COLUMNS].to_dict("records")
    grades = []
    outcomes = []
    for marks, average in zip(marks_per_student, results["Average"]):
        grades.append(assign_grade(average))
        outcomes.append(determine_result(marks, average))
    results["Grade"] = grades
    results["Result"] = outcomes

    results["Rank"] = calculate_ranks(results["Average"])

    # Attendance is only flagged; it never changes the Pass/Fail result.
    results["Low_Attendance"] = np.where(
        results[ATTENDANCE_COLUMN] < attendance_threshold, "Yes", "No"
    )
    return results[RESULT_COLUMNS]


# =============================================================================
# 6-9. HIGHEST/LOWEST, CLASS AVERAGE, SUBJECT AVERAGES, TOP STUDENTS
# =============================================================================
def _require_students(df):
    """Stop with a clear message if there are no students to analyse."""
    if df is None or len(df) == 0:
        raise ValueError("At least one student is required for this calculation.")


def find_highest_and_lowest_students(df):
    """Find the highest and lowest student averages, handling ties.

    Returns a dictionary:
        highest_average, highest_students (DataFrame, all tied students),
        lowest_average,  lowest_students  (DataFrame, all tied students)
    """
    _require_students(df)
    comparable = df["Average"].round(COMPARISON_DECIMALS)

    highest_rows = df[comparable == comparable.max()].sort_values("Student_ID")
    lowest_rows = df[comparable == comparable.min()].sort_values("Student_ID")

    return {
        "highest_average": float(highest_rows["Average"].iloc[0]),
        "highest_students": highest_rows,
        "lowest_average": float(lowest_rows["Average"].iloc[0]),
        "lowest_students": lowest_rows,
    }


def calculate_class_average(df):
    """Overall class average = mean of all student averages."""
    _require_students(df)
    return float(np.mean(df["Average"].to_numpy(dtype=float)))


def calculate_subject_averages(df):
    """Average marks of each subject across all students (a Series)."""
    _require_students(df)
    marks = df[SUBJECT_COLUMNS].to_numpy(dtype=float)
    return pd.Series(np.mean(marks, axis=0), index=SUBJECT_COLUMNS, name="Average")


def find_best_and_worst_subjects(df):
    """Find the subject(s) with the highest and lowest average, handling ties.

    Returns a dictionary:
        highest_average, highest_subjects (list of names),
        lowest_average,  lowest_subjects  (list of names)
    """
    subject_averages = calculate_subject_averages(df)
    comparable = subject_averages.round(COMPARISON_DECIMALS)

    best = comparable.max()
    worst = comparable.min()
    return {
        "highest_average": float(subject_averages[comparable == best].iloc[0]),
        "highest_subjects": list(subject_averages.index[comparable == best]),
        "lowest_average": float(subject_averages[comparable == worst].iloc[0]),
        "lowest_subjects": list(subject_averages.index[comparable == worst]),
    }


def rank_top_students(df, top_n=5):
    """Return the top-ranked students in order, handling ties.

    Students with equal averages share a rank. Every student whose rank is
    within the top `top_n` is included, so tied students at the cut-off are
    all shown (the table may then hold more than `top_n` rows).
    """
    if isinstance(top_n, bool) or not isinstance(top_n, (int, np.integer)) or top_n < 1:
        raise ValueError("top_n must be a whole number of at least 1.")
    _require_students(df)

    ranked = df.copy()
    ranked["Rank"] = calculate_ranks(ranked["Average"])
    ranked = ranked[ranked["Rank"] <= top_n]
    ranked = ranked.sort_values(["Rank", "Name", "Student_ID"])

    columns = ["Rank", "Student_ID", "Name", "Department", "Total", "Average", "Grade", "Result"]
    return ranked[columns].reset_index(drop=True)


# =============================================================================
# 10. PASS / FAIL STATISTICS
# =============================================================================
def calculate_pass_statistics(df):
    """Student count, pass count, fail count and pass percentage."""
    total_students = len(df)
    passed = int((df["Result"] == "Pass").sum())
    failed = int((df["Result"] == "Fail").sum())

    if total_students == 0:
        pass_percentage = 0.0  # avoid dividing by zero
    else:
        pass_percentage = passed / total_students * 100

    return {
        "total_students": total_students,
        "passed": passed,
        "failed": failed,
        "pass_percentage": pass_percentage,
    }


# =============================================================================
# 11. ATTENDANCE
# =============================================================================
def summarize_attendance(df, threshold=LOW_ATTENDANCE_THRESHOLD):
    """Average, highest and lowest attendance, and how many are below threshold."""
    _check_threshold(threshold)
    _require_students(df)
    attendance = df[ATTENDANCE_COLUMN].to_numpy(dtype=float)
    return {
        "average_attendance": float(np.mean(attendance)),
        "highest_attendance": float(np.max(attendance)),
        "lowest_attendance": float(np.min(attendance)),
        "low_attendance_count": int(np.sum(attendance < threshold)),
        "threshold": threshold,
    }


def find_low_attendance_students(df, threshold=LOW_ATTENDANCE_THRESHOLD):
    """Students whose attendance is BELOW the threshold, lowest first.

    A student with attendance exactly equal to the threshold is not flagged.
    """
    _check_threshold(threshold)
    low = df[df[ATTENDANCE_COLUMN] < threshold]
    return low.sort_values([ATTENDANCE_COLUMN, "Student_ID"]).reset_index(drop=True)


# =============================================================================
# FILTERING AND EXPORT (used by the Student Records page)
# =============================================================================
def filter_students(df, departments=None, result="All", search_text=""):
    """Filter the results table.

    departments: list of department names to keep. None = no department
                 filter; an empty list = no department selected (no rows).
    result:      "All", "Pass" or "Fail".
    search_text: keeps students whose Name or Student_ID contains the text
                 (not case-sensitive).
    """
    if result not in ("All", "Pass", "Fail"):
        raise ValueError("result must be 'All', 'Pass' or 'Fail'.")

    filtered = df
    if departments is not None:
        filtered = filtered[filtered["Department"].isin(departments)]
    if result != "All":
        filtered = filtered[filtered["Result"] == result]

    text = (search_text or "").strip()
    if text:
        in_name = filtered["Name"].str.contains(text, case=False, regex=False)
        in_id = filtered["Student_ID"].str.contains(text, case=False, regex=False)
        filtered = filtered[in_name | in_id]

    return filtered.copy()


def results_to_csv(df):
    """Convert a results table to CSV text (Average rounded to 2 decimals)."""
    return df.round({"Average": 2}).to_csv(index=False)
