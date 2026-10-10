🎓 Student Performance Analytics System

A web dashboard that analyses student marks and attendance. Built with Python, NumPy, Pandas and Streamlit as an academic project for a Python with AI course.

	
🌐 Live website	https://student-performance-analytics-ashmita06.streamlit.app/
💻 GitHub repository	https://github.com/iashmita97/Student_performance_Analytics
👩‍🎓 Author	Ashmita

Fictional data: every student in students.csv is invented for this project. No real student information is used.

Provisional rules: the grade boundaries, pass policy and attendance threshold are assumptions made for this project. They are not verified official college rules.

📌 Table of Contents
Project Overview
Features
Technologies Used and How
How the Project Works
Folder Structure
Dataset
Grading and Pass Rules
Calculations
Data Validation
Run Locally on Windows
Automated Tests
Deployment
1. Project Overview

The app reads 28 fictional student records from students.csv, checks that the data is valid, and then calculates totals, averages, grades, pass/fail results, ranks and attendance flags. Everything is shown in an interactive dashboard.

No machine learning, database, API key or paid service is used.

2. Features
Tab	What it shows
Overview	Student count, class average, pass percentage, passed/failed counts, and the highest-performing student(s). Ties are handled.
Student Records	The original dataset, a calculated results table, department filter, pass/fail filter, name/ID search, and a CSV download of the filtered rows.
Subject Analysis	Average marks of each subject, a comparison chart, and the highest and lowest subject.
Student Performance	Highest and lowest student averages, a ranked top-student table, and a chart of every student's average.
Attendance	Average, highest and lowest attendance, a chart with a threshold line, and students below an adjustable threshold. Low attendance is kept separate from academic failure.
Individual Student	Pick a student to see marks, total, average, grade, rank, pass/fail (with the reason for a fail) and attendance.
Downloads	A CSV of all results, including the calculated fields.

The sidebar also has a low-attendance slider and a panel showing the grading rules in use.

3. Technologies Used and How
Technology	Where it is used	How it is used
Python	app.py, functions.py, test_functions.py	Variables and data types for the configuration. if statements for grading and pass/fail rules. for loops to find a grade and to build tables and lists. Reusable functions for every calculation. A custom DataValidationError class for clear error messages.
NumPy	functions.py	np.sum(axis=1) gives each student's total. np.mean(axis=0) gives each subject's average. np.mean, np.max, np.min and np.sum summarise attendance. np.where creates the Low_Attendance Yes/No column. np.isfinite rejects invalid numbers.
Pandas	functions.py, app.py	read_csv loads students.csv into a DataFrame. to_numeric converts marks during validation. New columns hold Total, Average, Grade, Result, Rank and Low_Attendance. Boolean filtering, isin and str.contains power the filters and search. rank(method="min") gives tied students the same rank. to_csv creates the downloads.
Streamlit	app.py	Builds the web page: tabs, columns, metric cards, tables with number formatting, sidebar, slider, multiselect, radio buttons, text search, dropdown, download buttons, and error and info messages.
Altair	app.py	Draws the bar charts: subject averages with labels, student averages coloured green (pass) or red (fail), and attendance with a dashed threshold line. Comes with Streamlit and is listed in requirements.txt.
unittest	test_functions.py	Tests grade boundaries, pass/fail rules, ties, validation, filters and CSV export. Also uses Streamlit's built-in AppTest to check that the app starts and shows errors for bad data.
Git and GitHub	Repository	Stores the code and tracks changes.
Streamlit Community Cloud	Live website	Deploys the app from the main branch using app.py as the entry point and installs the packages in requirements.txt.
4. How the Project Works

The calculations and the web page are kept in separate files, so the calculations can be tested without opening the website.

students.csv  ──►  functions.py  ──►  app.py  ──►  Dashboard in the browser
 (the data)       (load, validate,    (Streamlit      (tabs, charts, tables,
                   calculate)          interface)      CSV downloads)
                        ▲
                        │
                 test_functions.py
                 (automated tests)
app.py asks functions.py to load and validate students.csv.
If the data is invalid, the app shows every problem and stops. It never replaces bad values with invented ones.
If the data is valid, functions.py adds the calculated columns.
app.py displays the results in tabs, charts and tables.
5. Folder Structure
Student_performance_Analytics/
├── app.py                    # Streamlit web app (entry point)
├── functions.py              # Calculations, validation, grading settings
├── students.csv              # 28 fictional student records
├── requirements.txt          # Python packages needed
├── test_functions.py         # Automated tests
├── README.md                 # This file
├── Project_Documentation.md  # Academic project documentation
├── .gitignore                # Files Git ignores
└── .streamlit/
    └── config.toml           # Colour theme only (no secrets)
6. Dataset

students.csv has one row per student:

Column	Meaning
Student_ID	Unique ID such as S001
Name	Fictional student name
Department	Computer Science, Information Technology, Electronics or Mechanical
Mathematics, Python, Computer_Science, English	Marks out of 100 each
Attendance	Attendance percentage (0 to 100)

The data has no missing values and no duplicate IDs. It includes a wide range of performance (grades A to F) and a few deliberate special cases:

two students tied for the highest average
a student who fails because of one subject even though the average is above 40
students with low attendance who pass, and others who fail
a student whose attendance is exactly on the threshold
7. Grading and Pass Rules

Each of the 4 subjects is worth 100 marks, so the maximum total is 400.

Grade	Average marks
A	90 to 100
B	80 to below 90
C	70 to below 80
D	60 to below 70
E	40 to below 60
F	below 40
Pass: at least 35 marks in every subject and an overall average of at least 40. Otherwise the result is Fail.
Low attendance: attendance below 75%. Attendance is never used for pass/fail.
Grade and result are separate: a student can have grade E but still fail, for example with only 30 marks in one subject.

These rules are stored in one configuration section at the top of functions.py, so they are easy to change.

8. Calculations
Calculation	Formula or rule
Total marks	Sum of the four subject marks
Average marks	Total ÷ 4
Class average	Mean of all student averages
Subject average	Mean of one subject across all students
Pass percentage	Passed students ÷ total students × 100
Rank	Equal averages share a rank (for example 1, 1, 3)
Highest and lowest	All tied students are listed, never just one
Low attendance	Attendance below the threshold (exactly equal is not low)
9. Data Validation

The app checks students.csv and reports every problem it finds, with line numbers:

file missing, empty or not a well-formed CSV
missing columns
missing values
marks or attendance that are not numbers
marks or attendance outside 0 to 100
duplicate student IDs
10. Run Locally on Windows

Open the project folder in VS Code, open a terminal, and run:

py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py

The app opens at http://localhost:8501. Press Ctrl+C in the terminal to stop it.

If PowerShell says scripts are disabled, run Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned and then .venv\Scripts\activate again.

11. Automated Tests
python -m unittest -v

The project includes 102 tests. Every test should show ok, and the run should end with OK.

12. Deployment

The app is deployed on Streamlit Community Cloud from the main branch with app.py as the main file.

To update the live website after changing the code:

git add .
git commit -m "Describe your change"
git push

Streamlit Community Cloud redeploys automatically after a minute or two. If it does not, open the app's menu on Streamlit Cloud and choose Reboot app.
