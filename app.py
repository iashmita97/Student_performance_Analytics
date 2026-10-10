"""
app.py - Streamlit web application for the Student Performance Analytics System.

This file only builds the user interface. All calculations are done by the
functions in functions.py, which can be tested separately (test_functions.py).

Run locally with:  streamlit run app.py
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import functions as fn

# Path relative to this file, so the app works on any computer.
DATA_FILE = Path(__file__).resolve().parent / "students.csv"

# Colours used in the charts
PRIMARY_COLOR = "#1F4E79"
PASS_COLOR = "#2E7D6B"
FAIL_COLOR = "#C0392B"

st.set_page_config(
    page_title="Student Performance Analytics System",
    page_icon="🎓",
    layout="wide",
)


# -----------------------------------------------------------------------------
# Small helper functions for display
# -----------------------------------------------------------------------------
def pretty(column_name):
    """Show 'Computer_Science' as 'Computer Science'."""
    return column_name.replace("_", " ")


def number(value):
    """Format a number without useless '.0' (85.0 -> '85', 85.5 -> '85.5')."""
    return f"{value:g}"


def show_student_list(students):
    """Print each student of a (possibly tied) group on its own line."""
    for _, student in students.iterrows():
        st.markdown(
            f"- **{student['Name']}** ({student['Student_ID']}, "
            f"{student['Department']}) - Grade {student['Grade']}"
        )


# Table formatting shared by all tables that show calculated columns
TABLE_COLUMNS = {
    "Total": st.column_config.NumberColumn(f"Total (/{fn.MAX_TOTAL_MARKS})", format="%g"),
    "Average": st.column_config.NumberColumn("Average", format="%.2f"),
    "Attendance": st.column_config.NumberColumn("Attendance (%)", format="%g"),
    "Rank": st.column_config.NumberColumn("Rank", format="%d"),
}


def bar_chart_of_averages(results):
    """Bar chart of every student's average, highest first, coloured by result."""
    chart_data = results.copy()
    # Name + ID keeps bars separate even if two students share a name.
    chart_data["Student"] = chart_data["Name"] + " (" + chart_data["Student_ID"] + ")"
    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X("Student:N", sort="-y", title=None, axis=alt.Axis(labelAngle=-60, labelLimit=220)),
            y=alt.Y("Average:Q", title="Average marks", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color(
                "Result:N",
                scale=alt.Scale(domain=["Pass", "Fail"], range=[PASS_COLOR, FAIL_COLOR]),
            ),
            tooltip=["Student_ID", "Name", "Department", "Total",
                     alt.Tooltip("Average:Q", format=".2f"), "Grade", "Result"],
        )
        .properties(height=420)
    )
    return chart


def bar_chart_of_subjects(subject_averages):
    """Bar chart comparing the average marks of each subject."""
    chart_data = pd.DataFrame({
        "Subject": [pretty(name) for name in subject_averages.index],
        "Average": subject_averages.to_numpy(),
    })
    bars = (
        alt.Chart(chart_data)
        .mark_bar(color=PRIMARY_COLOR)
        .encode(
            x=alt.X("Subject:N", sort="-y", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Average:Q", title="Average marks", scale=alt.Scale(domain=[0, 100])),
            tooltip=["Subject", alt.Tooltip("Average:Q", format=".2f")],
        )
    )
    labels = bars.mark_text(dy=-8, color="#1F2933").encode(text=alt.Text("Average:Q", format=".2f"))
    return (bars + labels).properties(height=360)


def bar_chart_of_attendance(results, threshold):
    """Bar chart of attendance with a red line at the low-attendance threshold."""
    chart_data = results.copy()
    chart_data["Student"] = chart_data["Name"] + " (" + chart_data["Student_ID"] + ")"
    chart_data["Status"] = chart_data["Low_Attendance"].map(
        {"Yes": "Below threshold", "No": "At or above threshold"}
    )
    bars = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X("Student:N", sort="-y", title=None, axis=alt.Axis(labelAngle=-60, labelLimit=220)),
            y=alt.Y("Attendance:Q", title="Attendance (%)", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color(
                "Status:N",
                scale=alt.Scale(domain=["At or above threshold", "Below threshold"],
                                range=[PRIMARY_COLOR, "#E08E0B"]),
            ),
            tooltip=["Student_ID", "Name", "Department", "Attendance", "Status", "Result"],
        )
    )
    line = alt.Chart(pd.DataFrame({"threshold": [threshold]})).mark_rule(
        color=FAIL_COLOR, strokeDash=[6, 4], size=2
    ).encode(y="threshold:Q")
    return (bars + line).properties(height=400)


# -----------------------------------------------------------------------------
# Page header
# -----------------------------------------------------------------------------
st.title("🎓 Student Performance Analytics System")
st.caption(
    "A beginner-friendly academic project built with Python, NumPy, Pandas and Streamlit."
)

# -----------------------------------------------------------------------------
# Load and validate the data (clear error messages if anything is wrong)
# -----------------------------------------------------------------------------
try:
    students = fn.load_students(DATA_FILE)
except fn.DataValidationError as error:
    st.error("The student data could not be loaded, so the dashboard cannot be shown.")
    MAX_PROBLEMS_SHOWN = 15
    for problem in error.problems[:MAX_PROBLEMS_SHOWN]:
        st.markdown(f"- {problem}")
    if len(error.problems) > MAX_PROBLEMS_SHOWN:
        st.markdown(f"- ...and {len(error.problems) - MAX_PROBLEMS_SHOWN} more problem(s).")
    st.info(
        "Fix `students.csv` (it must be in the same folder as `app.py`) and reload the page. "
        "Required columns: " + ", ".join(fn.REQUIRED_COLUMNS) + ". "
        f"Marks and attendance must be numbers from {fn.MIN_VALUE} to {fn.MAX_VALUE}, "
        "and every Student_ID must be unique."
    )
    st.stop()

# -----------------------------------------------------------------------------
# Sidebar: notes, rules and the configurable attendance threshold
# -----------------------------------------------------------------------------
st.sidebar.header("About this data")
st.sidebar.info(
    "**Fictional sample data.** All names and marks in `students.csv` were "
    "invented for this academic project. They are not real students."
)

st.sidebar.header("Settings")
attendance_threshold = st.sidebar.slider(
    "Low-attendance threshold (%)",
    min_value=fn.MIN_VALUE,
    max_value=fn.MAX_VALUE,
    value=int(fn.LOW_ATTENDANCE_THRESHOLD),
    help="Students with attendance BELOW this value are flagged. "
         "Attendance never affects the Pass/Fail result.",
)

with st.sidebar.expander("Provisional grading and pass rules"):
    st.caption(
        "These rules are assumptions for this project, **not verified official "
        "college rules**. They are defined in one place at the top of `functions.py`."
    )
    # Build the grade table from the settings with a loop
    grade_lines = []
    upper_limit = fn.MAX_MARKS_PER_SUBJECT
    for lower_limit, grade in fn.GRADE_BOUNDARIES:
        grade_lines.append(f"- **{grade}**: average {lower_limit} to {upper_limit}")
        upper_limit = lower_limit
    grade_lines.append(f"- **{fn.LOWEST_GRADE}**: average below {upper_limit}")
    st.markdown("**Grades (based on the average)**")
    st.markdown("\n".join(grade_lines))
    st.markdown(
        f"**Pass:** at least {fn.PASS_MARK_PER_SUBJECT} marks in every subject **and** "
        f"an overall average of at least {fn.PASS_AVERAGE}."
    )
    st.markdown(f"**Low attendance:** below {attendance_threshold}% (setting above).")

# -----------------------------------------------------------------------------
# All calculations happen here (functions.py)
# -----------------------------------------------------------------------------
results = fn.process_students(students, attendance_threshold)
pass_stats = fn.calculate_pass_statistics(results)
class_average = fn.calculate_class_average(results)
extremes = fn.find_highest_and_lowest_students(results)
subject_averages = fn.calculate_subject_averages(results)
subject_extremes = fn.find_best_and_worst_subjects(results)
attendance_summary = fn.summarize_attendance(results, attendance_threshold)
low_attendance = fn.find_low_attendance_students(results, attendance_threshold)

tab_overview, tab_records, tab_subjects, tab_performance, tab_attendance, tab_individual, tab_download = st.tabs(
    ["Overview", "Student Records", "Subject Analysis", "Student Performance",
     "Attendance", "Individual Student", "Downloads"]
)

# -----------------------------------------------------------------------------
# A. Dashboard overview
# -----------------------------------------------------------------------------
with tab_overview:
    st.subheader("Dashboard overview")
    st.write(
        "This dashboard analyses the marks and attendance of students in four subjects "
        f"(each out of {fn.MAX_MARKS_PER_SUBJECT}, so the maximum total is {fn.MAX_TOTAL_MARKS}). "
        "Use the tabs above to explore records, subjects, rankings, attendance and "
        "individual students."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total students", pass_stats["total_students"], border=True)
    col2.metric("Class average", f"{class_average:.2f}", help=f"Out of {fn.MAX_MARKS_PER_SUBJECT}", border=True)
    col3.metric("Pass percentage", f"{pass_stats['pass_percentage']:.1f}%", border=True)
    col4.metric("Passed / Failed", f"{pass_stats['passed']} / {pass_stats['failed']}", border=True)

    top_students = extremes["highest_students"]
    if len(top_students) == 1:
        st.success(f"🏆 **Highest-performing student** - average {extremes['highest_average']:.2f}")
    else:
        st.success(
            f"🏆 **{len(top_students)} students share the highest average** "
            f"of {extremes['highest_average']:.2f} (joint top performers)"
        )
    show_student_list(top_students)

    st.caption(
        f"Departments in the dataset: {', '.join(sorted(results['Department'].unique()))}. "
        "Data is fictional sample data; grading rules are provisional."
    )

# -----------------------------------------------------------------------------
# B. Student records
# -----------------------------------------------------------------------------
with tab_records:
    st.subheader("Original dataset")
    st.caption("Exactly as stored in `students.csv` (before any calculations).")
    st.dataframe(students, hide_index=True, height=250)

    st.subheader("Calculated results")
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 2])
    with filter_col1:
        all_departments = sorted(results["Department"].unique())
        chosen_departments = st.multiselect("Department", all_departments, default=all_departments)
    with filter_col2:
        chosen_result = st.radio("Result", ["All", "Pass", "Fail"], horizontal=True)
    with filter_col3:
        search_text = st.text_input("Search by name or student ID", placeholder="e.g. Sen or S012")

    filtered = fn.filter_students(results, chosen_departments, chosen_result, search_text)
    st.caption(f"Showing {len(filtered)} of {len(results)} students. "
               "Rank is the position in the whole class.")

    if len(chosen_departments) == 0:
        st.warning("No department is selected, so no students are shown.")
    elif len(filtered) == 0:
        st.info("No students match the current filters.")
    st.dataframe(filtered, hide_index=True, column_config=TABLE_COLUMNS)

    st.download_button(
        "⬇️ Download these filtered rows (CSV)",
        data=fn.results_to_csv(filtered),
        file_name="filtered_student_results.csv",
        mime="text/csv",
        disabled=len(filtered) == 0,
    )

# -----------------------------------------------------------------------------
# C. Subject analysis
# -----------------------------------------------------------------------------
with tab_subjects:
    st.subheader("Subject-wise analysis")

    best_names = ", ".join(pretty(name) for name in subject_extremes["highest_subjects"])
    worst_names = ", ".join(pretty(name) for name in subject_extremes["lowest_subjects"])
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.metric("Highest subject average", best_names)
            st.caption(f"Average marks: {subject_extremes['highest_average']:.2f} out of {fn.MAX_MARKS_PER_SUBJECT}")
    with col2:
        with st.container(border=True):
            st.metric("Lowest subject average", worst_names)
            st.caption(f"Average marks: {subject_extremes['lowest_average']:.2f} out of {fn.MAX_MARKS_PER_SUBJECT}")
    if len(subject_extremes["highest_subjects"]) > 1:
        st.info("More than one subject shares the highest average, so all of them are listed.")
    if len(subject_extremes["lowest_subjects"]) > 1:
        st.info("More than one subject shares the lowest average, so all of them are listed.")

    st.altair_chart(bar_chart_of_subjects(subject_averages))

    subject_table = pd.DataFrame({
        "Subject": [pretty(name) for name in subject_averages.index],
        "Average marks": subject_averages.to_numpy(),
    })
    st.dataframe(
        subject_table,
        hide_index=True,
        column_config={"Average marks": st.column_config.NumberColumn(format="%.2f")},
    )

# -----------------------------------------------------------------------------
# D. Student performance
# -----------------------------------------------------------------------------
with tab_performance:
    st.subheader("Student performance")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            label = "Highest average" if len(extremes["highest_students"]) == 1 else "Highest average (tie)"
            st.metric(label, f"{extremes['highest_average']:.2f}")
            show_student_list(extremes["highest_students"])
    with col2:
        with st.container(border=True):
            label = "Lowest average" if len(extremes["lowest_students"]) == 1 else "Lowest average (tie)"
            st.metric(label, f"{extremes['lowest_average']:.2f}")
            show_student_list(extremes["lowest_students"])

    st.markdown("#### Top-performing students")
    top_n = st.slider("Number of top ranks to show", min_value=1, max_value=10, value=5)
    top_table = fn.rank_top_students(results, top_n)
    st.caption(
        "Students with the same average share the same rank (for example 1, 1, 3). "
        "Everyone tied within the chosen ranks is shown, so the table can be longer than the "
        "number selected."
    )
    st.dataframe(top_table, hide_index=True, column_config=TABLE_COLUMNS)

    st.markdown("#### Average marks of all students")
    st.altair_chart(bar_chart_of_averages(results))

# -----------------------------------------------------------------------------
# E. Attendance analysis
# -----------------------------------------------------------------------------
with tab_attendance:
    st.subheader("Attendance analysis")
    st.info(
        "**Low attendance is not the same as failing.** Pass/Fail depends only on marks. "
        "Attendance is shown here as extra information, and the threshold can be changed "
        "in the sidebar."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average attendance", f"{attendance_summary['average_attendance']:.1f}%", border=True)
    col2.metric("Highest attendance", f"{number(attendance_summary['highest_attendance'])}%", border=True)
    col3.metric("Lowest attendance", f"{number(attendance_summary['lowest_attendance'])}%", border=True)
    col4.metric("Below attendance threshold", attendance_summary["low_attendance_count"],
                help=f"Attendance below {attendance_threshold}%", border=True)

    st.altair_chart(bar_chart_of_attendance(results, attendance_threshold))
    st.caption(f"The dashed red line marks the {attendance_threshold}% threshold.")

    st.markdown(f"#### Students with attendance below {attendance_threshold}%")
    if len(low_attendance) == 0:
        st.success("No student is below the attendance threshold.")
    else:
        low_and_failed = int((low_attendance["Result"] == "Fail").sum())
        low_and_passed = len(low_attendance) - low_and_failed
        st.write(
            f"{len(low_attendance)} student(s) have low attendance: "
            f"{low_and_passed} still pass academically and {low_and_failed} fail because of their marks."
        )
        st.dataframe(
            low_attendance[["Student_ID", "Name", "Department", "Attendance", "Average", "Result"]],
            hide_index=True,
            column_config=TABLE_COLUMNS,
        )

# -----------------------------------------------------------------------------
# F. Individual student details
# -----------------------------------------------------------------------------
with tab_individual:
    st.subheader("Individual student details")

    # Build a "S001 - Aarav Sen" label for every student (loop)
    labels = {}
    for _, row in results.iterrows():
        labels[f"{row['Student_ID']} - {row['Name']}"] = row["Student_ID"]

    chosen_label = st.selectbox("Select a student", list(labels.keys()))
    student = results[results["Student_ID"] == labels[chosen_label]].iloc[0]

    st.markdown(f"### {student['Name']}")
    st.caption(f"Student ID: {student['Student_ID']}  |  Department: {student['Department']}")

    mark_columns = st.columns(len(fn.SUBJECT_COLUMNS))
    for column, subject in zip(mark_columns, fn.SUBJECT_COLUMNS):
        column.metric(pretty(subject), f"{number(student[subject])} / {fn.MAX_MARKS_PER_SUBJECT}", border=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total marks", f"{number(student['Total'])} / {fn.MAX_TOTAL_MARKS}", border=True)
    col2.metric("Average", f"{student['Average']:.2f}", border=True)
    col3.metric("Grade", student["Grade"], border=True)
    col4.metric("Class rank", f"{student['Rank']} of {len(results)}", border=True)

    marks_of_student = {subject: student[subject] for subject in fn.SUBJECT_COLUMNS}
    if student["Result"] == "Pass":
        st.success("**Result: Pass**")
    else:
        st.error("**Result: Fail**")
        for reason in fn.get_fail_reasons(marks_of_student, student["Average"]):
            st.markdown(f"- {reason}")

    if student["Low_Attendance"] == "Yes":
        st.warning(
            f"**Attendance: {number(student['Attendance'])}%** - below the {attendance_threshold}% "
            "threshold (this does not change the Pass/Fail result)."
        )
    else:
        st.info(f"**Attendance: {number(student['Attendance'])}%** - at or above the "
                f"{attendance_threshold}% threshold.")

    detail_rows = []
    for subject in fn.SUBJECT_COLUMNS:
        mark = student[subject]
        detail_rows.append({
            "Subject": pretty(subject),
            "Marks": mark,
            "Class average": subject_averages[subject],
            "Subject pass mark": "Met" if mark >= fn.PASS_MARK_PER_SUBJECT else "Not met",
        })
    st.dataframe(
        pd.DataFrame(detail_rows),
        hide_index=True,
        column_config={
            "Marks": st.column_config.NumberColumn(format="%g"),
            "Class average": st.column_config.NumberColumn(format="%.2f"),
        },
    )

# -----------------------------------------------------------------------------
# G. Downloadable results
# -----------------------------------------------------------------------------
with tab_download:
    st.subheader("Download results")
    st.write(
        "The CSV file contains every student with the original data plus the calculated "
        "fields: **Total, Average (2 decimals), Grade, Result, Rank and Low_Attendance**. "
        f"Low_Attendance uses the current threshold of {attendance_threshold}%."
    )
    st.download_button(
        "⬇️ Download all student results (CSV)",
        data=fn.results_to_csv(results),
        file_name="student_results.csv",
        mime="text/csv",
        type="primary",
    )
    st.caption("To download only some students, use the filters in the 'Student Records' tab.")
    st.dataframe(results, hide_index=True, column_config=TABLE_COLUMNS)
