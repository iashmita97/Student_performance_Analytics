# 🎓 Student Performance Analytics System

A web dashboard that analyzes student marks and attendance using **Python, NumPy, Pandas, and Streamlit**. Developed as an academic project for a *Python with AI* course.

| Resource | Link |
|---|---|
| 🌐 **Live Website** | [Open Dashboard](https://student-performance-analytics-ashmita06.streamlit.app/) |
| 💻 **GitHub Repository** | [View Source Code](https://github.com/iashmita97/Student_performance_Analytics) |
| 👩‍🎓 **Author** | Ashmita |

> **Data notice:** All student records in `students.csv` are fictional. No real student information is used.
>
> **Rules notice:** Grade boundaries, pass criteria, and attendance thresholds are provisional assumptions for this project, not verified official college rules.

---

## 📌 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Features](#2-features)
3. [Technologies Used](#3-technologies-used)
4. [How the Project Works](#4-how-the-project-works)
5. [Folder Structure](#5-folder-structure)
6. [Dataset](#6-dataset)
7. [Grading and Pass Rules](#7-grading-and-pass-rules)
8. [Calculations](#8-calculations)
9. [Data Validation](#9-data-validation)
10. [Run Locally on Windows](#10-run-locally-on-windows)
11. [Automated Tests](#11-automated-tests)
12. [Deployment](#12-deployment)

---

## 1. Project Overview

The application reads **28 fictional student records** from `students.csv`, validates the data, and calculates:

- Total and average marks
- Grades and pass/fail results
- Student ranks
- Subject-wise performance
- Attendance statistics and low-attendance flags

The results are presented through an interactive Streamlit dashboard with tables, charts, filters, and downloadable CSV files.

**No machine learning model, database, API key, or paid service is required.**

---

## 2. Features

| Dashboard Section | Description |
|---|---|
| **Overview** | Student count, class average, pass percentage, passed/failed counts, and highest-performing students. Ties are handled. |
| **Student Records** | Original dataset, calculated results, department and result filters, name/ID search, and filtered CSV download. |
| **Subject Analysis** | Subject-wise average marks, comparison chart, and highest- and lowest-performing subjects. |
| **Student Performance** | Highest and lowest student averages, ranked top performers, and a chart of student averages. |
| **Attendance** | Average, highest and lowest attendance, attendance chart, threshold line, and a list of students below the selected threshold. |
| **Individual Student** | Selected student's marks, total, average, grade, rank, result, reason for failure, and attendance. |
| **Downloads** | Download all student results, including calculated fields, as a CSV file. |

**Additional controls:** The sidebar includes a low-attendance threshold slider and a panel displaying the grading and pass/fail rules currently in use.

---

## 3. Technologies Used

| Technology | Files Used | Purpose |
|---|---|---|
| **Python** | `app.py`, `functions.py`, `test_functions.py` | Variables, conditions, loops, reusable functions, calculations, and custom validation errors. |
| **NumPy** | `functions.py` | Calculates totals and averages and summarizes attendance using functions such as `np.sum()`, `np.mean()`, `np.max()`, `np.min()`, and `np.where()`. `np.isfinite()` helps detect invalid numerical values. |
| **Pandas** | `functions.py`, `app.py` | Reads CSV data into DataFrames, validates values, adds calculated columns, filters records, ranks students, searches names, and exports results using `to_csv()`. |
| **Streamlit** | `app.py` | Creates the interactive web dashboard, tabs, metric cards, tables, filters, sliders, dropdowns, charts, and download buttons. |
| **Altair** | `app.py` | Creates charts for subject averages, student performance, and attendance. |
| **unittest** | `test_functions.py` | Tests grade boundaries, pass/fail rules, ties, data validation, filtering, CSV export, and application behavior using Streamlit's `AppTest`. |
| **Git and GitHub** | Repository | Stores the project source code and tracks changes. |
| **Streamlit Community Cloud** | Live website | Hosts the application using `app.py` and installs dependencies from `requirements.txt`. |

---

## 4. How the Project Works

The calculation logic and the web interface are kept in separate files, making the calculations easier to test and maintain.

```text
             students.csv
                  |
                  v
             functions.py
          (Load and validate
             the data)
                  |
                  v
               app.py
        (Streamlit dashboard)
                  |
                  v
          Interactive Website
       (Tables, charts, filters,
           and downloads)

          test_functions.py
       (Automated testing)
```

### Workflow

1. `app.py` asks `functions.py` to load and validate `students.csv`.
2. If the data is invalid, the application displays the detected problems and stops processing the invalid dataset.
3. If the data is valid, the calculation functions generate totals, averages, grades, results, ranks, and attendance flags.
4. Streamlit displays the calculated information through interactive tabs, charts, and tables.
5. Users can filter student records and download the results as CSV files.
6. Automated tests check the calculation logic and selected application behaviors.

---

## 5. Folder Structure

```text
Student_performance_Analytics/
│
├── app.py                    # Streamlit dashboard
├── functions.py              # Calculations and validation
├── students.csv              # 28 fictional student records
├── requirements.txt          # Required Python packages
├── test_functions.py         # Automated tests
├── README.md                 # Project overview and instructions
├── Project_Documentation.md  # Academic project documentation
├── .gitignore                # Files excluded from Git
│
└── .streamlit/
    └── config.toml            # Streamlit theme configuration
```

---

## 6. Dataset

The `students.csv` file contains one row per student and includes the following columns:

| Column | Description |
|---|---|
| `Student_ID` | Unique student identifier, such as `S001`. |
| `Name` | Fictional student name. |
| `Department` | Student's department: Computer Science, Information Technology, Electronics, or Mechanical. |
| `Mathematics` | Mathematics marks out of 100. |
| `Python` | Python programming marks out of 100. |
| `Computer_Science` | Computer Science marks out of 100. |
| `English` | English marks out of 100. |
| `Attendance` | Attendance percentage, from 0 to 100. |

### Dataset Highlights

- Contains 28 fictional student records.
- Has no missing values or duplicate student IDs in the supplied dataset.
- Includes a range of academic performance levels, from grades A to F.
- Contains two students tied for the highest average.
- Includes a student who fails one subject despite having an overall average above 40.
- Includes students with low attendance who pass, as well as students who fail academically.
- Includes a student whose attendance is exactly at the threshold.

These examples help demonstrate how the application handles different scenarios.

---

## 7. Grading and Pass Rules

Each of the four subjects carries a maximum of 100 marks. Therefore, the maximum total is **400 marks**.

### Grade Boundaries

| Grade | Average Marks |
|---|---:|
| A | 90 to 100 |
| B | 80 to below 90 |
| C | 70 to below 80 |
| D | 60 to below 70 |
| E | 40 to below 60 |
| F | Below 40 |

### Pass/Fail Criteria

A student passes only when both conditions are satisfied:

1. At least **35 marks in every subject**.
2. An overall average of at least **40 marks**.

Otherwise, the result is **Fail**.

### Attendance Criteria

- Low attendance means attendance is **below 75%** by default.
- Attendance exactly equal to 75% is not classified as low.
- Attendance does not determine academic pass/fail status.
- The attendance threshold can be adjusted through the dashboard.

**Note:** These are configurable project assumptions, not official college grading rules. The grade and pass/fail result are calculated separately. For example, a student can receive grade E based on the average but still fail because one subject has fewer than 35 marks.

The rules are stored in the configuration section of `functions.py`, making them easy to modify.

---

## 8. Calculations

| Calculation | Formula or Rule |
|---|---|
| **Total Marks** | Sum of marks in the four subjects. |
| **Average Marks** | Total marks ÷ 4. |
| **Class Average** | Mean of all student averages. |
| **Subject Average** | Mean marks for an individual subject across all students. |
| **Pass Percentage** | (Number of passed students ÷ Total students) × 100. |
| **Rank** | Students with equal averages share the same rank; for example, 1, 1, 3. |
| **Highest and Lowest Performance** | All students tied for the highest or lowest value are included. |
| **Low Attendance** | Attendance below the selected threshold. A value exactly equal to the threshold is not low. |

---

## 9. Data Validation

Before performing calculations, the application checks the dataset and reports detected problems, including line numbers where available.

Validation covers:

- Missing, empty, or malformed CSV files.
- Missing required columns.
- Missing values.
- Non-numeric marks or attendance.
- Marks or attendance outside the valid range of 0 to 100.
- Duplicate student IDs.

The application reports invalid data rather than silently replacing it with invented values.

---

## 10. Run Locally on Windows

Follow these steps to run the project on your computer.

### Step 1: Open the Project

Clone your repository and open the project folder in VS Code.

```bash
git clone https://github.com/iashmita97/Student_performance_Analytics.git
cd Student_performance_Analytics
```

### Step 2: Create a Virtual Environment

```bash
py -m venv .venv
```

### Step 3: Activate the Environment

```powershell
.venv\Scripts\activate
```

If PowerShell blocks script execution, run the following command in the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate the environment again.

### Step 4: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Start the Application

```bash
streamlit run app.py
```

The dashboard should open in your browser at:

**http://localhost:8501**

To stop the application, press `Ctrl + C` in the terminal.

---

## 11. Automated Tests

The project includes automated tests for important calculations and application behavior.

Run the test suite from the project directory:

```bash
python -m unittest -v
```

The expected result is for all **102 tests** to pass, with the final output ending in:

```text
OK
```

If any test fails, review the error message and fix the issue before submitting the project.

---

## 12. Deployment

The application is hosted on **Streamlit Community Cloud** and uses the main GitHub branch, with `app.py` as the application entry point.

### Live Links

- **Live Dashboard:** https://student-performance-analytics-ashmita06.streamlit.app/
- **GitHub Repository:** https://github.com/iashmita97/Student_performance_Analytics

### Updating the Live Website

After making changes to the project, run the following commands in the terminal:

```bash
git add .
git commit -m "Update student performance analytics"
git push
```

Streamlit Community Cloud can redeploy the application after the changes are pushed to the connected branch. If the update does not appear, check the deployment logs and app status in the Streamlit Community Cloud dashboard.

---

## 🎯 Project Outcome

The Student Performance Analytics System demonstrates how Python, NumPy, Pandas, and Streamlit can be combined to process student data and present useful academic insights through an interactive dashboard.

The project applies core Python programming concepts, data validation, numerical calculations, tabular data processing, visualization, automated testing, GitHub version control, and cloud deployment in one practical application.

**Developed by Ashmita**  
*Python with AI — Academic Project, 2026*
