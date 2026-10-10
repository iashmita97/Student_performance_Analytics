# Project Documentation: Student Performance Analytics System

> Items in `[square brackets]` are placeholders. Replace them with your own information before submitting.

---

## 1. Project Title and Student Details

| Field | Details |
|---|---|
| **Project title** | Student Performance Analytics System |
| **Student name** | Ashmita Chatterjee |
| **Roll / enrolment number** | 10800223055 |
| **College / institution** | Asansol Engineering College/ MAKAUT |
| **Course** | Bachelor of Technology |
| **Department / semester** | Information Technology/ 7th Semester |
| **Trainer / guide** | `[Trainer's Name]` |
| **Submission date** | 14-10-26 |

## 2. Objective

The objective of this project is to build a simple web application that analyses the academic performance of students using Python, NumPy and Pandas. The application reads fictional student records (marks in four subjects and attendance), validates them, calculates totals, averages, grades, pass/fail results, rankings and attendance flags, and presents the results in an interactive Streamlit dashboard that can be deployed on Streamlit Community Cloud.

The project is also used to practise:

- Python fundamentals (variables, data types, conditions, loops, functions);
- numerical work with NumPy and data analysis with Pandas;
- separating calculation logic from the user interface;
- testing calculations and handling invalid data;
- publishing a project through GitHub and Streamlit Community Cloud.

## 3. Technologies Used

| Technology | Use in the project |
|---|---|
| Python | Main programming language (developed with Python 3.12) |
| NumPy | Totals, means, minimum and maximum calculations |
| Pandas | Reading the CSV file, DataFrames, filtering and analysis |
| Streamlit | Web interface (metrics, tabs, tables, filters, download button) |
| Altair | Bar charts (installed with Streamlit) |
| `unittest` | Automated tests |
| Git and GitHub | Version control and code hosting |
| Streamlit Community Cloud | Free public deployment |
| VS Code | Code editor |

No machine learning, database, external API or paid service is used.

## 4. Dataset Description

**File:** `students.csv`. **Type:** fictional sample data created for this project (no real students).

| Column | Description |
|---|---|
| `Student_ID` | Unique identifier (S001 to S028) |
| `Name` | Fictional name |
| `Department` | Computer Science, Information Technology, Electronics or Mechanical |
| `Mathematics`, `Python`, `Computer_Science`, `English` | Marks out of 100 for each subject |
| `Attendance` | Attendance percentage between 0 and 100 |

- **Records:** 28 students across 4 departments.
- All marks and attendance values are between 0 and 100; there are no missing values and no duplicate IDs.
- The records cover a wide range of performance (grades A to F) and include special cases for testing and demonstration: a tie for the highest average, a fail caused by one subject only, a fail caused by a low overall average, low attendance with and without academic failure, attendance exactly on the threshold, and a subject mark exactly on the pass mark.

### Provisional rules used (assumptions, not official college rules)

| Rule | Value used |
|---|---|
| Subjects and marks | 4 subjects x 100 marks = 400 maximum |
| Grades (by average) | A 90-100, B 80 to below 90, C 70 to below 80, D 60 to below 70, E 40 to below 60, F below 40 |
| Pass | At least 35 in every subject **and** average of at least 40 |
| Low attendance | Below 75% (not used for pass/fail) |

These values were chosen for this project because no official rules were provided. They are stored in one configuration section in `functions.py` and can be changed easily.

## 5. Implementation Methodology

1. **Planning:** the required calculations and dashboard sections were listed, and the project was split into a calculation module (`functions.py`), a web interface (`app.py`), the data (`students.csv`) and tests (`test_functions.py`).
2. **Dataset creation:** 28 fictional records were written with varied performance and deliberate edge cases.
3. **Calculation module:** configuration constants and reusable functions were written, with no Streamlit code in them so they can be tested independently.
4. **Validation:** the data is read as text and checked for missing columns, missing values, non-numeric values, values outside 0-100 and duplicate IDs. Problems are reported with CSV line numbers; invalid values are never replaced.
5. **Web interface:** a Streamlit dashboard with seven tabs was built on top of the functions.
6. **Testing:** unit tests cover the calculations, grade and pass boundaries, ties, validation, filtering, CSV export and the start-up of the app.
7. **Deployment:** the project is uploaded to GitHub and deployed on Streamlit Community Cloud (see `README.md`).

### Project structure

```
student-performance-analytics/
├── app.py, functions.py, students.csv, requirements.txt
├── test_functions.py, README.md, Project_Documentation.md
├── .gitignore
└── .streamlit/config.toml
```

## 6. Explanation of NumPy and Pandas Usage

### Pandas

- `pd.read_csv` loads `students.csv` into a DataFrame. All values are first read as text so that invalid entries can be detected rather than silently converted.
- `pd.to_numeric` converts marks and attendance to numbers during validation.
- DataFrame columns are added for `Total`, `Average`, `Grade`, `Result`, `Rank` and `Low_Attendance`.
- Boolean filtering selects rows (for example attendance below the threshold, or a chosen department/result).
- `rank(method="min")` ranks students so equal averages share a rank.
- `DataFrame.to_csv` creates the downloadable results file.

### NumPy

- `DataFrame.to_numpy()` converts the four subject columns into a 2D array.
- `np.sum(marks, axis=1)` gives each student's total marks.
- `np.mean(..., axis=0)` gives each subject's average across all students.
- `np.mean`, `np.max`, `np.min` and `np.sum` summarise attendance.
- `np.where` creates the `Low_Attendance` Yes/No column.
- `np.isfinite` helps reject invalid numbers during validation.

## 7. Functions and Calculation Logic

All functions are in `functions.py`.

| Function | Purpose and logic |
|---|---|
| `load_students(file_path)` | Reads the CSV, reports a missing, empty or malformed file, and returns validated data. |
| `find_data_problems(df)` / `validate_students(df)` | Check columns, missing values, numeric values, range 0-100 and duplicate IDs; raise `DataValidationError` with all problems. |
| `calculate_total_marks(df)` | Sum of the four subject marks (maximum 400). |
| `calculate_average_marks(df)` | Total divided by 4. |
| `assign_grade(average)` | Loops through the grade boundaries from highest to lowest and returns the first grade whose minimum is met; below 40 gives F. |
| `get_fail_reasons(marks, average)` / `determine_result(marks, average)` | A student fails if any subject is below 35 or the average is below 40; otherwise passes. |
| `calculate_ranks(averages)` | Competition ranking: equal averages share a rank (1, 1, 3). Comparisons round to 6 decimals to avoid floating-point noise. |
| `process_students(df, threshold)` | Validates the data and adds Total, Average, Grade, Result, Rank and Low_Attendance. |
| `find_highest_and_lowest_students(df)` | Returns all students tied for the highest and the lowest average. |
| `calculate_class_average(df)` | Mean of all student averages. |
| `calculate_subject_averages(df)` | Mean of each subject across all students. |
| `find_best_and_worst_subjects(df)` | Subject(s) with the highest and lowest average, including ties. |
| `rank_top_students(df, top_n)` | Students within the top ranks in order; tied students at the cut-off are all included. |
| `calculate_pass_statistics(df)` | Student count, passed, failed, and pass percentage = passed / total x 100. |
| `summarize_attendance(df, threshold)` | Average, highest and lowest attendance and the number of students below the threshold. |
| `find_low_attendance_students(df, threshold)` | Students with attendance below the threshold (equal to the threshold is not low). |
| `filter_students(...)` | Filters by department, result and a name/ID search. |
| `results_to_csv(df)` | Converts results to CSV text, with Average rounded to 2 decimals. |

## 8. Key Features

- Dashboard overview with student count, class average, pass percentage, passed/failed counts and highest performer(s).
- Student records page showing the original data, calculated results, department/result filters, name or ID search, and a CSV download of the filtered rows.
- Subject analysis with subject averages, a comparison chart, and the highest and lowest subject.
- Student performance page with highest and lowest averages, a ranked top-student table and a chart of all averages.
- Attendance analysis with summary statistics, a chart, an adjustable threshold and a list of low-attendance students, clearly separated from academic failure.
- Individual student view with marks, total, average, grade, rank, result (and the reason for a fail) and attendance.
- Download of all calculated results as a CSV file.
- Clear error messages for missing or invalid data; the dashboard is not shown for invalid data.
- Provisional grading rules stored in one place and shown in the sidebar.

## 9. Output Screenshots

> Run the app with `streamlit run app.py`, take a screenshot of each page, and replace each placeholder below with the image (for example `![Overview](screenshots/overview.png)`).

| No. | Screenshot | Placeholder |
|---|---|---|
| 1 | Overview tab (metrics and highest performers) | `[INSERT SCREENSHOT]` |
| 2 | Student Records tab (original dataset and filters) | `[INSERT SCREENSHOT]` |
| 3 | Student Records tab with a filter applied | `[INSERT SCREENSHOT]` |
| 4 | Subject Analysis tab (chart and averages) | `[INSERT SCREENSHOT]` |
| 5 | Student Performance tab (top students and chart) | `[INSERT SCREENSHOT]` |
| 6 | Attendance tab (chart and low-attendance list) | `[INSERT SCREENSHOT]` |
| 7 | Individual Student tab | `[INSERT SCREENSHOT]` |
| 8 | Downloads tab | `[INSERT SCREENSHOT]` |
| 9 | Terminal output of `python -m unittest -v` (your own run) | `[INSERT SCREENSHOT]` |
| 10 | The deployed website in the browser | `[INSERT SCREENSHOT]` |

## 10. Final Outcome

The finished project is a working Streamlit web application that loads the fictional dataset, validates it, performs all the required academic calculations, and presents them in an interactive dashboard with filters, charts, individual student details and a CSV download. The calculation code is separated from the interface and covered by automated unit tests, which can be run with `python -m unittest -v`.

**Deployment status:** `[Write "Deployed on Streamlit Community Cloud on DD/MM/YYYY" after you have actually deployed it]`

**Your test result:** `[After running python -m unittest -v, write the number of tests that passed here]`

## 11. Challenges and Learning

> The points below describe the real design problems in this project. Edit them so they reflect your own experience.

- **Handling ties:** several students can share the highest average, so the program reports every tied student and uses shared ranks (1, 1, 3) instead of picking one name.
- **Pass/fail versus grade:** pass/fail needs two conditions (each subject and the average), so a student can have a grade of E but still fail. A "reason" message was added to explain this.
- **Data validation:** reading values as text first made it possible to detect invalid entries instead of silently turning them into zeros or missing numbers.
- **Floating-point comparison:** averages are rounded to 6 decimals only when comparing students, so tiny arithmetic differences do not break ties.
- **Separating logic from the interface:** keeping calculations in `functions.py` made them easy to test without running the website.
- **Learning:** `[Write what you learned about Python, NumPy, Pandas, Streamlit, testing, GitHub and deployment]`

## 12. GitHub Repository Link

[(https://github.com/iashmita97/Student_performance_Analytics)]

## 13. Live Website Link

[https://share.streamlit.io/]
