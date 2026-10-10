"""
test_functions.py - automated tests for the Student Performance Analytics System.

Run all tests from the project folder with:
    python -m unittest -v

Most tests check the calculations in functions.py against values worked out
independently (plain Python or small hand-checked examples). The last test
class runs the Streamlit app in a test harness to make sure it starts and
shows clear errors for bad data.
"""

import csv
import logging
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

import functions as fn

PROJECT_DIR = Path(__file__).resolve().parent
CSV_PATH = PROJECT_DIR / "students.csv"
APP_PATH = PROJECT_DIR / "app.py"


# -----------------------------------------------------------------------------
# Helpers that build small test datasets
# -----------------------------------------------------------------------------
def student_row(student_id, marks=(70, 70, 70, 70), attendance=90, name=None,
                department="Computer Science"):
    """One student as a tuple in the same column order as students.csv."""
    return (student_id, name or f"Student {student_id}", department, *marks, attendance)


def make_students(rows):
    """Build a DataFrame from a list of student_row(...) tuples."""
    return pd.DataFrame(rows, columns=fn.REQUIRED_COLUMNS)


def make_processed(rows, threshold=fn.LOW_ATTENDANCE_THRESHOLD):
    """Build and fully process a small dataset."""
    return fn.process_students(make_students(rows), threshold)


def read_csv_with_python(path):
    """Read students.csv using only Python's csv module (independent of pandas)."""
    with open(path, newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


# -----------------------------------------------------------------------------
class TestConfiguration(unittest.TestCase):
    def test_four_subjects_worth_100_each(self):
        self.assertEqual(fn.NUMBER_OF_SUBJECTS, 4)
        self.assertEqual(fn.MAX_MARKS_PER_SUBJECT, 100)
        self.assertEqual(fn.MAX_TOTAL_MARKS, 400)

    def test_provisional_rules(self):
        self.assertEqual(fn.PASS_MARK_PER_SUBJECT, 35)
        self.assertEqual(fn.PASS_AVERAGE, 40)
        self.assertEqual(fn.LOW_ATTENDANCE_THRESHOLD, 75)
        self.assertEqual(fn.GRADE_BOUNDARIES, [(90, "A"), (80, "B"), (70, "C"), (60, "D"), (40, "E")])
        self.assertEqual(fn.LOWEST_GRADE, "F")

    def test_grade_boundaries_are_in_descending_order(self):
        minimums = [minimum for minimum, _ in fn.GRADE_BOUNDARIES]
        self.assertEqual(minimums, sorted(minimums, reverse=True))


# -----------------------------------------------------------------------------
class TestDefaultDataset(unittest.TestCase):
    """Checks on the students.csv file that ships with the project."""

    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv_with_python(CSV_PATH)
        cls.students = fn.load_students(CSV_PATH)
        cls.results = fn.process_students(cls.students)

    def test_file_has_expected_columns_in_order(self):
        self.assertEqual(list(self.rows[0].keys()), fn.REQUIRED_COLUMNS)

    def test_record_count_is_between_24_and_30(self):
        self.assertGreaterEqual(len(self.rows), 24)
        self.assertLessEqual(len(self.rows), 30)
        self.assertEqual(len(self.students), len(self.rows))

    def test_student_ids_are_unique(self):
        ids = [row["Student_ID"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_missing_values_and_all_numbers_in_range(self):
        for row in self.rows:
            for column in fn.REQUIRED_COLUMNS:
                self.assertNotEqual(row[column].strip(), "", f"{row['Student_ID']} {column}")
            for column in fn.SUBJECT_COLUMNS + [fn.ATTENDANCE_COLUMN]:
                value = float(row[column])
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 100)

    def test_file_passes_validation_with_no_problems(self):
        self.assertEqual(fn.find_data_problems(self.students), [])

    def test_has_several_departments(self):
        self.assertGreaterEqual(self.students["Department"].nunique(), 3)

    def test_has_varied_performance(self):
        self.assertGreaterEqual(self.results["Grade"].nunique(), 4)
        self.assertIn("Pass", set(self.results["Result"]))
        self.assertIn("Fail", set(self.results["Result"]))

    def test_dataset_contains_the_designed_edge_cases(self):
        # A tie for the highest average
        top = fn.find_highest_and_lowest_students(self.results)
        self.assertGreaterEqual(len(top["highest_students"]), 2)
        # A student who fails a subject although the average is at least 40
        subject_fail = self.results[
            (self.results["Result"] == "Fail") & (self.results["Average"] >= fn.PASS_AVERAGE)
        ]
        self.assertGreaterEqual(len(subject_fail), 1)
        # Low attendance, both for passing and for failing students
        low = fn.find_low_attendance_students(self.results)
        self.assertIn("Pass", set(low["Result"]))
        self.assertIn("Fail", set(low["Result"]))
        # Someone with good marks but attendance exactly on the threshold
        self.assertIn(fn.LOW_ATTENDANCE_THRESHOLD, set(self.results["Attendance"]))

    def test_every_total_equals_sum_of_four_subjects(self):
        by_id = self.results.set_index("Student_ID")
        for row in self.rows:
            expected_total = sum(float(row[subject]) for subject in fn.SUBJECT_COLUMNS)
            self.assertEqual(by_id.loc[row["Student_ID"], "Total"], expected_total)

    def test_every_average_equals_total_divided_by_four(self):
        by_id = self.results.set_index("Student_ID")
        for row in self.rows:
            expected_total = sum(float(row[subject]) for subject in fn.SUBJECT_COLUMNS)
            self.assertAlmostEqual(by_id.loc[row["Student_ID"], "Average"], expected_total / 4)

    def test_class_average_matches_independent_calculation(self):
        all_marks = [float(row[s]) for row in self.rows for s in fn.SUBJECT_COLUMNS]
        expected = sum(all_marks) / len(all_marks)  # 4 subjects per student
        self.assertAlmostEqual(fn.calculate_class_average(self.results), expected)

    def test_subject_averages_match_independent_calculation(self):
        subject_averages = fn.calculate_subject_averages(self.results)
        for subject in fn.SUBJECT_COLUMNS:
            expected = sum(float(row[subject]) for row in self.rows) / len(self.rows)
            self.assertAlmostEqual(subject_averages[subject], expected)

    def test_pass_statistics_match_independent_calculation(self):
        expected_passed = 0
        for row in self.rows:
            marks = [float(row[s]) for s in fn.SUBJECT_COLUMNS]
            if min(marks) >= 35 and sum(marks) / 4 >= 40:
                expected_passed += 1
        stats = fn.calculate_pass_statistics(self.results)
        self.assertEqual(stats["total_students"], len(self.rows))
        self.assertEqual(stats["passed"], expected_passed)
        self.assertEqual(stats["failed"], len(self.rows) - expected_passed)
        self.assertAlmostEqual(stats["pass_percentage"], expected_passed / len(self.rows) * 100)

    def test_highest_and_lowest_match_independent_calculation(self):
        averages = {row["Student_ID"]: sum(float(row[s]) for s in fn.SUBJECT_COLUMNS) / 4
                    for row in self.rows}
        highest_ids = sorted(i for i, a in averages.items() if a == max(averages.values()))
        lowest_ids = sorted(i for i, a in averages.items() if a == min(averages.values()))
        found = fn.find_highest_and_lowest_students(self.results)
        self.assertEqual(list(found["highest_students"]["Student_ID"]), highest_ids)
        self.assertEqual(list(found["lowest_students"]["Student_ID"]), lowest_ids)
        self.assertAlmostEqual(found["highest_average"], max(averages.values()))
        self.assertAlmostEqual(found["lowest_average"], min(averages.values()))


# -----------------------------------------------------------------------------
class TestTotalsAndAverages(unittest.TestCase):
    def test_total_and_average_for_known_students(self):
        df = make_students([
            student_row("A1", marks=(100, 100, 100, 100)),
            student_row("A2", marks=(0, 0, 0, 0)),
            student_row("A3", marks=(80, 70, 60, 50)),
        ])
        self.assertEqual(list(fn.calculate_total_marks(df)), [400, 0, 260])
        self.assertEqual(list(fn.calculate_average_marks(df)), [100.0, 0.0, 65.0])

    def test_decimal_marks_are_supported(self):
        df = make_students([student_row("A1", marks=(85.5, 90.5, 70, 80))])
        self.assertAlmostEqual(fn.calculate_total_marks(df).iloc[0], 326.0)
        self.assertAlmostEqual(fn.calculate_average_marks(df).iloc[0], 81.5)

    def test_process_students_does_not_change_the_input(self):
        df = make_students([student_row("A1")])
        before = df.copy()
        fn.process_students(df)
        pd.testing.assert_frame_equal(df, before)

    def test_processed_table_has_all_expected_columns(self):
        results = make_processed([student_row("A1")])
        self.assertEqual(list(results.columns), fn.RESULT_COLUMNS)


# -----------------------------------------------------------------------------
class TestGrades(unittest.TestCase):
    def test_exact_boundaries_and_values_just_below(self):
        cases = [
            (100, "A"), (95, "A"), (90, "A"), (89.99, "B"),
            (80, "B"), (79.99, "C"), (70, "C"), (69.99, "D"),
            (60, "D"), (59.99, "E"), (40, "E"), (39.99, "F"),
            (0, "F"),
        ]
        for average, expected in cases:
            with self.subTest(average=average):
                self.assertEqual(fn.assign_grade(average), expected)

    def test_invalid_averages_are_rejected(self):
        for bad_value in (-0.01, 100.01, float("nan")):
            with self.subTest(value=bad_value):
                with self.assertRaises(ValueError):
                    fn.assign_grade(bad_value)

    def test_grades_in_processed_table(self):
        rows = [
            student_row("A", marks=(90, 90, 90, 90)),  # 90 -> A
            student_row("B", marks=(80, 80, 80, 80)),  # 80 -> B
            student_row("C", marks=(70, 70, 70, 70)),  # 70 -> C
            student_row("D", marks=(60, 60, 60, 60)),  # 60 -> D
            student_row("E", marks=(40, 40, 40, 40)),  # 40 -> E
            student_row("F", marks=(39, 39, 39, 39)),  # 39 -> F
        ]
        results = make_processed(rows)
        self.assertEqual(list(results["Grade"]), ["A", "B", "C", "D", "E", "F"])


# -----------------------------------------------------------------------------
class TestPassFail(unittest.TestCase):
    def marks(self, *values):
        return dict(zip(fn.SUBJECT_COLUMNS, values))

    def test_pass_when_all_conditions_met(self):
        self.assertEqual(fn.determine_result(self.marks(60, 60, 60, 60), 60), "Pass")

    def test_subject_boundary_35_passes_and_34_fails(self):
        self.assertEqual(fn.determine_result(self.marks(35, 60, 60, 60), 53.75), "Pass")
        self.assertEqual(fn.determine_result(self.marks(34.99, 60, 60, 60), 53.7475), "Fail")

    def test_average_boundary_40_passes_and_just_below_fails(self):
        self.assertEqual(fn.determine_result(self.marks(40, 40, 40, 40), 40), "Pass")
        self.assertEqual(fn.determine_result(self.marks(40, 40, 40, 39.99), 39.9975), "Fail")

    def test_fails_on_average_even_if_every_subject_is_35_or_more(self):
        marks = self.marks(36, 38, 37, 35)  # average 36.5
        self.assertEqual(fn.determine_result(marks, 36.5), "Fail")

    def test_fails_on_one_subject_even_if_average_is_high(self):
        marks = self.marks(30, 100, 100, 100)  # average 82.5
        self.assertEqual(fn.determine_result(marks, 82.5), "Fail")

    def test_fail_reasons_are_explained(self):
        reasons = fn.get_fail_reasons(self.marks(30, 100, 100, 100), 82.5)
        self.assertEqual(len(reasons), 1)
        self.assertIn("Mathematics", reasons[0])
        self.assertEqual(fn.get_fail_reasons(self.marks(60, 60, 60, 60), 60), [])
        self.assertEqual(len(fn.get_fail_reasons(self.marks(10, 10, 10, 10), 10)), 5)

    def test_attendance_never_affects_result(self):
        rows = [
            student_row("A", marks=(70, 70, 70, 70), attendance=0),
            student_row("B", marks=(70, 70, 70, 70), attendance=100),
        ]
        results = make_processed(rows)
        self.assertEqual(list(results["Result"]), ["Pass", "Pass"])


# -----------------------------------------------------------------------------
class TestPassStatistics(unittest.TestCase):
    def test_counts_and_percentage(self):
        rows = [
            student_row("A", marks=(80, 80, 80, 80)),
            student_row("B", marks=(60, 60, 60, 60)),
            student_row("C", marks=(10, 10, 10, 10)),
            student_row("D", marks=(50, 50, 50, 20)),  # fails on one subject
        ]
        stats = fn.calculate_pass_statistics(make_processed(rows))
        self.assertEqual(stats["total_students"], 4)
        self.assertEqual(stats["passed"], 2)
        self.assertEqual(stats["failed"], 2)
        self.assertEqual(stats["pass_percentage"], 50.0)

    def test_percentage_with_non_round_result(self):
        rows = [student_row("A"), student_row("B"), student_row("C", marks=(0, 0, 0, 0))]
        stats = fn.calculate_pass_statistics(make_processed(rows))
        self.assertAlmostEqual(stats["pass_percentage"], 2 / 3 * 100)

    def test_empty_table_gives_zero_percentage(self):
        empty = make_processed([student_row("A")]).iloc[0:0]
        stats = fn.calculate_pass_statistics(empty)
        self.assertEqual(stats["total_students"], 0)
        self.assertEqual(stats["pass_percentage"], 0.0)


# -----------------------------------------------------------------------------
class TestClassAndSubjectAverages(unittest.TestCase):
    def setUp(self):
        self.results = make_processed([
            student_row("A", marks=(100, 80, 60, 40)),
            student_row("B", marks=(50, 60, 70, 80)),
        ])

    def test_class_average(self):
        # Student A: 280 / 4 = 70. Student B: 260 / 4 = 65. Class average = 67.5
        self.assertAlmostEqual(fn.calculate_class_average(self.results), 67.5)

    def test_subject_averages(self):
        averages = fn.calculate_subject_averages(self.results)
        self.assertEqual(averages["Mathematics"], 75.0)
        self.assertEqual(averages["Python"], 70.0)
        self.assertEqual(averages["Computer_Science"], 65.0)
        self.assertEqual(averages["English"], 60.0)

    def test_best_and_worst_subject(self):
        found = fn.find_best_and_worst_subjects(self.results)
        self.assertEqual(found["highest_subjects"], ["Mathematics"])
        self.assertEqual(found["highest_average"], 75.0)
        self.assertEqual(found["lowest_subjects"], ["English"])
        self.assertEqual(found["lowest_average"], 60.0)

    def test_tied_subjects_are_all_reported(self):
        results = make_processed([student_row("A", marks=(80, 80, 60, 60))])
        found = fn.find_best_and_worst_subjects(results)
        self.assertEqual(found["highest_subjects"], ["Mathematics", "Python"])
        self.assertEqual(found["lowest_subjects"], ["Computer_Science", "English"])

    def test_empty_data_is_rejected(self):
        empty = self.results.iloc[0:0]
        with self.assertRaises(ValueError):
            fn.calculate_class_average(empty)
        with self.assertRaises(ValueError):
            fn.calculate_subject_averages(empty)


# -----------------------------------------------------------------------------
class TestHighestLowestAndTies(unittest.TestCase):
    def test_single_highest_and_lowest(self):
        results = make_processed([
            student_row("A", marks=(90, 90, 90, 90)),
            student_row("B", marks=(70, 70, 70, 70)),
            student_row("C", marks=(50, 50, 50, 50)),
        ])
        found = fn.find_highest_and_lowest_students(results)
        self.assertEqual(list(found["highest_students"]["Student_ID"]), ["A"])
        self.assertEqual(list(found["lowest_students"]["Student_ID"]), ["C"])
        self.assertEqual(found["highest_average"], 90.0)
        self.assertEqual(found["lowest_average"], 50.0)

    def test_tied_highest_with_different_marks_but_same_average(self):
        results = make_processed([
            student_row("A", marks=(100, 80, 90, 90)),  # total 360
            student_row("B", marks=(90, 90, 90, 90)),  # total 360
            student_row("C", marks=(50, 50, 50, 50)),
        ])
        found = fn.find_highest_and_lowest_students(results)
        self.assertEqual(list(found["highest_students"]["Student_ID"]), ["A", "B"])
        self.assertEqual(len(found["lowest_students"]), 1)

    def test_tied_lowest(self):
        results = make_processed([
            student_row("A", marks=(90, 90, 90, 90)),
            student_row("B", marks=(40, 40, 40, 40)),
            student_row("C", marks=(40, 40, 40, 40)),
        ])
        found = fn.find_highest_and_lowest_students(results)
        self.assertEqual(list(found["lowest_students"]["Student_ID"]), ["B", "C"])

    def test_everyone_tied_is_both_highest_and_lowest(self):
        results = make_processed([student_row("A"), student_row("B")])
        found = fn.find_highest_and_lowest_students(results)
        self.assertEqual(len(found["highest_students"]), 2)
        self.assertEqual(len(found["lowest_students"]), 2)

    def test_tiny_floating_point_differences_still_tie(self):
        # Both averages are 85.25, but adding these decimals can differ slightly.
        results = make_processed([
            student_row("A", marks=(85.1, 85.2, 85.3, 85.4)),
            student_row("B", marks=(85.25, 85.25, 85.25, 85.25)),
            student_row("C", marks=(10, 10, 10, 10)),
        ])
        found = fn.find_highest_and_lowest_students(results)
        self.assertEqual(list(found["highest_students"]["Student_ID"]), ["A", "B"])
        self.assertEqual(list(results["Rank"]), [1, 1, 3])

    def test_empty_data_is_rejected(self):
        with self.assertRaises(ValueError):
            fn.find_highest_and_lowest_students(make_processed([student_row("A")]).iloc[0:0])


# -----------------------------------------------------------------------------
class TestRanking(unittest.TestCase):
    def setUp(self):
        self.results = make_processed([
            student_row("A", marks=(90, 90, 90, 90), name="Asha"),
            student_row("B", marks=(90, 90, 90, 90), name="Bela"),
            student_row("C", marks=(80, 80, 80, 80), name="Chitra"),
            student_row("D", marks=(70, 70, 70, 70), name="Dev"),
            student_row("E", marks=(70, 70, 70, 70), name="Esha"),
            student_row("F", marks=(60, 60, 60, 60), name="Farah"),
        ])

    def test_ranks_share_value_for_ties_and_skip_next_rank(self):
        self.assertEqual(list(self.results["Rank"]), [1, 1, 3, 4, 4, 6])

    def test_top_students_are_in_ranked_order(self):
        top = fn.rank_top_students(self.results, 3)
        self.assertEqual(list(top["Student_ID"]), ["A", "B", "C"])
        self.assertEqual(list(top["Rank"]), [1, 1, 3])

    def test_tied_students_at_the_cutoff_are_all_included(self):
        top = fn.rank_top_students(self.results, 4)  # D and E are both rank 4
        self.assertEqual(list(top["Student_ID"]), ["A", "B", "C", "D", "E"])

    def test_top_one_with_a_tie_returns_both_toppers(self):
        top = fn.rank_top_students(self.results, 1)
        self.assertEqual(list(top["Student_ID"]), ["A", "B"])

    def test_top_n_larger_than_class_returns_everyone(self):
        self.assertEqual(len(fn.rank_top_students(self.results, 50)), 6)

    def test_invalid_top_n_is_rejected(self):
        for bad_value in (0, -1, 2.5, "3", True):
            with self.subTest(top_n=bad_value):
                with self.assertRaises(ValueError):
                    fn.rank_top_students(self.results, bad_value)

    def test_ranking_does_not_modify_the_input(self):
        before = self.results.copy()
        fn.rank_top_students(self.results, 2)
        pd.testing.assert_frame_equal(self.results, before)


# -----------------------------------------------------------------------------
class TestAttendance(unittest.TestCase):
    def setUp(self):
        self.results = make_processed([
            student_row("A", attendance=100),
            student_row("B", attendance=75),  # exactly on the threshold
            student_row("C", attendance=74.9),
            student_row("D", attendance=50),
        ])

    def test_summary_values(self):
        summary = fn.summarize_attendance(self.results)
        self.assertAlmostEqual(summary["average_attendance"], (100 + 75 + 74.9 + 50) / 4)
        self.assertEqual(summary["highest_attendance"], 100.0)
        self.assertEqual(summary["lowest_attendance"], 50.0)
        self.assertEqual(summary["low_attendance_count"], 2)

    def test_exact_threshold_is_not_low_attendance(self):
        low = fn.find_low_attendance_students(self.results)
        self.assertEqual(list(low["Student_ID"]), ["D", "C"])  # lowest attendance first
        self.assertEqual(list(self.results["Low_Attendance"]), ["No", "No", "Yes", "Yes"])

    def test_threshold_is_configurable(self):
        low = fn.find_low_attendance_students(self.results, 90)
        self.assertEqual(list(low["Student_ID"]), ["D", "C", "B"])
        self.assertEqual(fn.summarize_attendance(self.results, 90)["low_attendance_count"], 3)
        results_90 = fn.process_students(make_students([student_row("A", attendance=89)]), 90)
        self.assertEqual(results_90["Low_Attendance"].iloc[0], "Yes")

    def test_zero_and_hundred_thresholds(self):
        self.assertEqual(len(fn.find_low_attendance_students(self.results, 0)), 0)
        self.assertEqual(len(fn.find_low_attendance_students(self.results, 100)), 3)

    def test_low_attendance_is_not_failure(self):
        # D has the worst attendance but good marks, so the result is Pass.
        row = self.results[self.results["Student_ID"] == "D"].iloc[0]
        self.assertEqual(row["Low_Attendance"], "Yes")
        self.assertEqual(row["Result"], "Pass")

    def test_invalid_thresholds_are_rejected(self):
        for bad_value in (-1, 101, "75", None, True):
            with self.subTest(threshold=bad_value):
                with self.assertRaises(ValueError):
                    fn.find_low_attendance_students(self.results, bad_value)
        with self.assertRaises(ValueError):
            fn.process_students(make_students([student_row("A")]), 150)


# -----------------------------------------------------------------------------
class TestValidation(unittest.TestCase):
    def test_valid_data_has_no_problems(self):
        df = make_students([student_row("A"), student_row("B")])
        self.assertEqual(fn.find_data_problems(df), [])

    def test_extreme_valid_values_0_and_100_are_accepted(self):
        df = make_students([student_row("A", marks=(0, 0, 0, 0), attendance=0),
                            student_row("B", marks=(100, 100, 100, 100), attendance=100)])
        self.assertEqual(fn.find_data_problems(df), [])

    def test_missing_columns_are_reported(self):
        df = make_students([student_row("A")]).drop(columns=["Python", "Attendance"])
        problems = fn.find_data_problems(df)
        self.assertEqual(len(problems), 1)
        self.assertIn("Python", problems[0])
        self.assertIn("Attendance", problems[0])

    def test_missing_values_are_reported_with_line_numbers(self):
        df = make_students([student_row("A"), student_row("B"), student_row("C")])
        df.loc[1, "English"] = np.nan  # second student -> CSV line 3
        df.loc[2, "Name"] = "   "  # blank text counts as missing too
        problems = fn.find_data_problems(df)
        self.assertTrue(any("Line 3" in p and "English" in p for p in problems))
        self.assertTrue(any("Line 4" in p and "Name" in p for p in problems))

    def test_marks_outside_0_to_100_are_reported(self):
        for bad_mark in (-1, 100.5, 101, 250):
            with self.subTest(mark=bad_mark):
                df = make_students([student_row("A", marks=(bad_mark, 70, 70, 70))])
                problems = fn.find_data_problems(df)
                self.assertEqual(len(problems), 1)
                self.assertIn("Mathematics", problems[0])

    def test_attendance_outside_0_to_100_is_reported(self):
        for bad_value in (-5, 100.1, 120):
            with self.subTest(attendance=bad_value):
                df = make_students([student_row("A", attendance=bad_value)])
                problems = fn.find_data_problems(df)
                self.assertEqual(len(problems), 1)
                self.assertIn("Attendance", problems[0])

    def test_non_numeric_text_is_reported(self):
        for bad_text in ("abc", "N/A", "eighty", "nan", "inf"):
            with self.subTest(text=bad_text):
                df = make_students([student_row("A", marks=(70, bad_text, 70, 70))]).astype(str)
                problems = fn.find_data_problems(df)
                self.assertEqual(len(problems), 1)
                self.assertIn("not a valid number", problems[0])

    def test_duplicate_student_ids_are_reported(self):
        df = make_students([student_row("A"), student_row("B"), student_row("A", name="Other")])
        problems = fn.find_data_problems(df)
        self.assertEqual(len(problems), 1)
        self.assertIn("duplicate", problems[0])
        self.assertIn("'A'", problems[0])

    def test_duplicate_ids_with_extra_spaces_are_still_duplicates(self):
        df = make_students([student_row("A"), student_row(" A ")])
        self.assertEqual(len(fn.find_data_problems(df)), 1)

    def test_empty_table_is_reported(self):
        df = make_students([])
        self.assertEqual(len(fn.find_data_problems(df)), 1)

    def test_all_problems_are_reported_together(self):
        df = make_students([
            student_row("A", marks=(120, 70, 70, 70)),
            student_row("A", marks=(70, -3, 70, 70)),
        ])
        self.assertEqual(len(fn.find_data_problems(df)), 3)  # 2 bad marks + 1 duplicate

    def test_invalid_data_raises_instead_of_being_replaced(self):
        df = make_students([student_row("A", marks=(70, np.nan, 70, 70))])
        with self.assertRaises(fn.DataValidationError) as context:
            fn.validate_students(df)
        self.assertEqual(len(context.exception.problems), 1)
        with self.assertRaises(fn.DataValidationError):
            fn.process_students(df)

    def test_validate_returns_clean_numeric_copy(self):
        df = make_students([student_row("  A ", name=" Asha ")]).astype(str)
        clean = fn.validate_students(df)
        self.assertEqual(clean["Student_ID"].iloc[0], "A")
        self.assertEqual(clean["Name"].iloc[0], "Asha")
        self.assertTrue(pd.api.types.is_numeric_dtype(clean["Mathematics"]))


# -----------------------------------------------------------------------------
class TestLoadingCsvFiles(unittest.TestCase):
    HEADER = ",".join(fn.REQUIRED_COLUMNS)

    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder, ignore_errors=True)

    def write(self, text, name="test.csv", encoding="utf-8"):
        path = self.folder / name
        path.write_text(text, encoding=encoding)
        return path

    def test_missing_file_gives_clear_error(self):
        with self.assertRaises(fn.DataValidationError) as context:
            fn.load_students(self.folder / "nope.csv")
        self.assertIn("not found", str(context.exception))

    def test_empty_file_gives_clear_error(self):
        with self.assertRaises(fn.DataValidationError) as context:
            fn.load_students(self.write(""))
        self.assertIn("empty", str(context.exception))

    def test_header_only_file_gives_clear_error(self):
        with self.assertRaises(fn.DataValidationError) as context:
            fn.load_students(self.write(self.HEADER + "\n"))
        self.assertIn("no student rows", str(context.exception))

    def test_malformed_row_with_too_many_fields(self):
        text = self.HEADER + "\nS1,A,CS,90,90,90,90,90\nS2,B,CS,90,90,90,90,90,EXTRA\n"
        with self.assertRaises(fn.DataValidationError) as context:
            fn.load_students(self.write(text))
        self.assertIn("not a well-formed CSV", str(context.exception))

    def test_row_with_too_few_fields_is_reported_as_missing_value(self):
        text = self.HEADER + "\nS1,A,CS,90,90,90\n"
        with self.assertRaises(fn.DataValidationError) as context:
            fn.load_students(self.write(text))
        problems = context.exception.problems
        self.assertTrue(any("English" in p for p in problems))
        self.assertTrue(any("Attendance" in p for p in problems))

    def test_missing_column_in_file(self):
        header = ",".join(fn.REQUIRED_COLUMNS[:-1])
        with self.assertRaises(fn.DataValidationError) as context:
            fn.load_students(self.write(header + "\nS1,A,CS,90,90,90,90\n"))
        self.assertIn("Attendance", str(context.exception))

    def test_text_in_a_marks_column(self):
        text = self.HEADER + "\nS1,A,CS,abc,90,90,90,90\n"
        with self.assertRaises(fn.DataValidationError) as context:
            fn.load_students(self.write(text))
        self.assertIn("not a valid number", str(context.exception))

    def test_blank_value_is_not_replaced_with_zero(self):
        text = self.HEADER + "\nS1,A,CS,,90,90,90,90\n"
        with self.assertRaises(fn.DataValidationError) as context:
            fn.load_students(self.write(text))
        self.assertIn("missing value in 'Mathematics'", str(context.exception))

    def test_literal_na_text_is_not_treated_as_a_valid_value(self):
        text = self.HEADER + "\nS1,A,CS,NA,90,90,90,90\n"
        with self.assertRaises(fn.DataValidationError):
            fn.load_students(self.write(text))

    def test_duplicate_ids_in_file(self):
        text = self.HEADER + "\nS1,A,CS,90,90,90,90,90\nS1,B,CS,80,80,80,80,80\n"
        with self.assertRaises(fn.DataValidationError) as context:
            fn.load_students(self.write(text))
        self.assertIn("duplicate", str(context.exception))

    def test_extra_columns_are_ignored_and_bom_is_handled(self):
        text = self.HEADER + ",Notes\nS1,A,CS,90,80,70,60,95,hello\n"
        path = self.write(text, encoding="utf-8-sig")  # Excel-style file with BOM
        students = fn.load_students(path)
        self.assertEqual(list(students.columns), fn.REQUIRED_COLUMNS)
        self.assertEqual(students["Python"].iloc[0], 80)

    def test_marks_are_loaded_as_numbers(self):
        students = fn.load_students(CSV_PATH)
        for column in fn.SUBJECT_COLUMNS + [fn.ATTENDANCE_COLUMN]:
            self.assertTrue(pd.api.types.is_numeric_dtype(students[column]))


# -----------------------------------------------------------------------------
class TestFiltering(unittest.TestCase):
    def setUp(self):
        self.results = make_processed([
            student_row("S1", name="Asha Rao", department="Electronics", marks=(80, 80, 80, 80)),
            student_row("S2", name="Bela Sen", department="Mechanical", marks=(10, 10, 10, 10)),
            student_row("S3", name="Chitra Rao", department="Electronics", marks=(10, 10, 10, 10)),
            student_row("S4", name="Dev Das", department="Computer Science", marks=(90, 90, 90, 90)),
        ])

    def ids(self, df):
        return list(df["Student_ID"])

    def test_no_filters_returns_everyone(self):
        self.assertEqual(self.ids(fn.filter_students(self.results)), ["S1", "S2", "S3", "S4"])

    def test_department_filter(self):
        found = fn.filter_students(self.results, departments=["Electronics"])
        self.assertEqual(self.ids(found), ["S1", "S3"])
        found = fn.filter_students(self.results, departments=["Electronics", "Mechanical"])
        self.assertEqual(self.ids(found), ["S1", "S2", "S3"])

    def test_empty_department_list_means_no_students(self):
        self.assertEqual(len(fn.filter_students(self.results, departments=[])), 0)

    def test_result_filter(self):
        self.assertEqual(self.ids(fn.filter_students(self.results, result="Pass")), ["S1", "S4"])
        self.assertEqual(self.ids(fn.filter_students(self.results, result="Fail")), ["S2", "S3"])

    def test_search_by_name_and_id_ignores_case(self):
        self.assertEqual(self.ids(fn.filter_students(self.results, search_text="rao")), ["S1", "S3"])
        self.assertEqual(self.ids(fn.filter_students(self.results, search_text="s2")), ["S2"])
        self.assertEqual(self.ids(fn.filter_students(self.results, search_text="  DEV ")), ["S4"])

    def test_search_treats_special_characters_as_plain_text(self):
        self.assertEqual(len(fn.filter_students(self.results, search_text=".*")), 0)

    def test_filters_combine(self):
        found = fn.filter_students(self.results, ["Electronics"], "Fail", "chitra")
        self.assertEqual(self.ids(found), ["S3"])

    def test_no_match_returns_empty_table_with_columns(self):
        found = fn.filter_students(self.results, search_text="zzz")
        self.assertEqual(len(found), 0)
        self.assertEqual(list(found.columns), fn.RESULT_COLUMNS)

    def test_invalid_result_option_is_rejected(self):
        with self.assertRaises(ValueError):
            fn.filter_students(self.results, result="Maybe")

    def test_filtering_does_not_modify_original(self):
        before = self.results.copy()
        fn.filter_students(self.results, ["Electronics"], "Pass", "a")
        pd.testing.assert_frame_equal(self.results, before)


# -----------------------------------------------------------------------------
class TestCsvExport(unittest.TestCase):
    def test_exported_csv_contains_calculated_fields_and_correct_values(self):
        import io
        results = fn.process_students(fn.load_students(CSV_PATH))
        exported = pd.read_csv(io.StringIO(fn.results_to_csv(results)), dtype={"Student_ID": str})
        self.assertEqual(list(exported.columns), fn.RESULT_COLUMNS)
        self.assertEqual(len(exported), len(results))
        for column in ["Total", "Grade", "Result", "Rank", "Low_Attendance", "Student_ID"]:
            self.assertEqual(list(exported[column]), list(results[column]), column)
        np.testing.assert_allclose(exported["Average"], results["Average"], atol=0.005)

    def test_export_matches_independent_totals(self):
        import io
        exported = pd.read_csv(io.StringIO(fn.results_to_csv(
            fn.process_students(fn.load_students(CSV_PATH)))))
        for _, row in exported.iterrows():
            self.assertEqual(row["Total"], sum(row[s] for s in fn.SUBJECT_COLUMNS))
            self.assertAlmostEqual(row["Average"], row["Total"] / 4)

    def test_filtered_export_contains_only_filtered_rows(self):
        import io
        results = fn.process_students(fn.load_students(CSV_PATH))
        failed = fn.filter_students(results, result="Fail")
        exported = pd.read_csv(io.StringIO(fn.results_to_csv(failed)))
        self.assertEqual(len(exported), len(failed))
        self.assertEqual(set(exported["Result"]), {"Fail"})

    def test_average_is_rounded_to_two_decimals_in_export(self):
        import io
        results = make_processed([student_row("A", marks=(90, 90, 90, 91))])  # 90.25
        exported = fn.results_to_csv(results)
        self.assertIn("90.25", exported)
        results = make_processed([student_row("A", marks=(85.123, 85, 85, 85))])
        exported = pd.read_csv(io.StringIO(fn.results_to_csv(results)))
        self.assertEqual(exported["Average"].iloc[0], 85.03)


# -----------------------------------------------------------------------------
# Hide Streamlit's harmless "missing ScriptRunContext" warnings during tests
logging.getLogger("streamlit").setLevel(logging.ERROR)

try:
    from streamlit.testing.v1 import AppTest
except ImportError:  # Streamlit not installed: skip the app tests
    AppTest = None


@unittest.skipIf(AppTest is None, "Streamlit is not installed")
class TestStreamlitApp(unittest.TestCase):
    """Runs app.py inside Streamlit's built-in test harness (no browser needed)."""

    def make_app_folder(self, csv_text=None):
        """Copy the app into a temporary folder, optionally with a custom CSV."""
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, ignore_errors=True)
        shutil.copy(APP_PATH, folder / "app.py")
        shutil.copy(PROJECT_DIR / "functions.py", folder / "functions.py")
        if csv_text is not None:
            (folder / "students.csv").write_text(csv_text, encoding="utf-8")
        return folder

    def run_app(self, folder):
        return AppTest.from_file(str(folder / "app.py"), default_timeout=60).run()

    def test_default_app_starts_without_errors(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=60).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertIn("Student Performance Analytics System", app.title[0].value)

    def test_dashboard_numbers_match_the_calculations(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=60).run()
        results = fn.process_students(fn.load_students(CSV_PATH))
        stats = fn.calculate_pass_statistics(results)
        shown = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(shown["Total students"], str(stats["total_students"]))
        self.assertEqual(shown["Class average"], f"{fn.calculate_class_average(results):.2f}")
        self.assertEqual(shown["Pass percentage"], f"{stats['pass_percentage']:.1f}%")

    def test_changing_the_attendance_slider_works(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=60).run()
        app.sidebar.slider[0].set_value(90).run()
        self.assertEqual(len(app.exception), 0)
        results = fn.process_students(fn.load_students(CSV_PATH), 90)
        shown = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(shown["Below attendance threshold"],
                         str(int((results["Low_Attendance"] == "Yes").sum())))

    def test_missing_csv_shows_error_not_a_crash(self):
        folder = self.make_app_folder(csv_text=None)
        app = self.run_app(folder)
        self.assertEqual(len(app.exception), 0)
        self.assertGreaterEqual(len(app.error), 1)
        self.assertTrue(any("not found" in str(m.value) for m in app.markdown))

    def test_invalid_csv_shows_every_problem(self):
        text = (",".join(fn.REQUIRED_COLUMNS) + "\n"
                "S1,A,CS,120,90,90,90,90\n"
                "S1,B,CS,80,,80,80,80\n")
        app = self.run_app(self.make_app_folder(text))
        self.assertEqual(len(app.exception), 0)
        self.assertGreaterEqual(len(app.error), 1)
        page_text = " ".join(str(m.value) for m in app.markdown)
        self.assertIn("outside the allowed range", page_text)
        self.assertIn("missing value", page_text)
        self.assertIn("duplicate", page_text)
        self.assertEqual(len(app.metric), 0)  # dashboard is not shown for bad data


if __name__ == "__main__":
    unittest.main()
