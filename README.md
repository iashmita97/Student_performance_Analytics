# Student Performance Analytics System

A beginner-friendly web dashboard that analyses the marks and attendance of students using **Python, NumPy and Pandas**, presented with **Streamlit**. It is an academic project for a *Python with AI* course.

> **Fictional data:** every student in `students.csv` is invented for this project. No real student information is used.
>
> **Provisional rules:** the grade boundaries, pass policy and attendance threshold are **assumptions for this project, not verified official college rules** (see [section 7](#7-provisional-grading-and-passing-rules)).

| | |
|---|---|
| **GitHub repository** | `[PASTE YOUR GITHUB REPOSITORY URL HERE]` |
| **Live website** | `[PASTE YOUR STREAMLIT COMMUNITY CLOUD URL HERE]` |
| **Author** | `[Your Name]` - `[Your College]` - `[Your Course]` |

---

## 1. Project overview

The application reads 28 fictional student records from `students.csv`, checks that the data is valid, calculates totals, averages, grades, pass/fail results, rankings and attendance flags, and shows everything in an interactive dashboard. No machine learning, database, API key or paid service is used.

## 2. Project objectives

- Practise Python fundamentals: variables, data types, conditions, loops and functions.
- Use **NumPy** for numerical calculations and **Pandas** for loading, filtering and analysing tabular data.
- Keep calculation logic (`functions.py`) separate from the user interface (`app.py`) so it can be tested.
- Validate input data and report problems clearly instead of hiding them.
- Publish the finished app on GitHub and Streamlit Community Cloud.

## 3. Key features

- **Overview:** student count, class average, pass percentage, passed/failed counts, highest-performing student(s) (ties handled).
- **Student Records:** original dataset, calculated results table, department filter, pass/fail filter, name/ID search, CSV download of the filtered rows.
- **Subject Analysis:** average of each subject, comparison chart, highest and lowest subject (ties handled).
- **Student Performance:** highest and lowest student averages, ranked top-N table (tied students share a rank), chart of all student averages.
- **Attendance:** average, highest and lowest attendance, chart with threshold line, list of students below an adjustable threshold, clearly separated from academic failure.
- **Individual Student:** choose a student to see marks, total, average, grade, rank, result (with the reason for a fail) and attendance.
- **Downloads:** CSV of all results including the calculated fields.
- **Error handling:** clear messages for a missing file, malformed CSV, missing columns, missing values, non-numeric or out-of-range marks/attendance, and duplicate student IDs. Invalid data is never silently replaced.

## 4. Technologies used

| Technology | Purpose |
|---|---|
| Python 3.10 or newer (developed and tested with Python 3.12) | Programming language |
| NumPy | Sums, means, minimum and maximum |
| Pandas | Loading the CSV, DataFrames, filtering |
| Streamlit | Web interface |
| Altair | Charts (installed together with Streamlit; listed in `requirements.txt`) |
| `unittest` | Automated tests (part of Python) |

## 5. Folder structure

```
student-performance-analytics/
├── app.py                    # Streamlit web application (the entry point)
├── functions.py              # Calculations, validation and the grading configuration
├── students.csv              # 28 fictional student records
├── requirements.txt          # Python packages needed
├── test_functions.py         # Automated tests
├── README.md                 # This file
├── Project_Documentation.md  # Academic project documentation
├── .gitignore                # Files Git should ignore
└── .streamlit/
    └── config.toml           # Colour theme only (no secrets)
```

## 6. Dataset description

`students.csv` has one row per student and these columns:

| Column | Meaning |
|---|---|
| `Student_ID` | Unique ID such as `S001` |
| `Name` | Fictional student name |
| `Department` | Computer Science, Information Technology, Electronics or Mechanical |
| `Mathematics`, `Python`, `Computer_Science`, `English` | Marks out of 100 each |
| `Attendance` | Attendance percentage (0-100) |

The data contains no missing values or duplicate IDs. It deliberately includes varied performance levels and some special cases useful for demonstration: two students tied for the highest average, a student who fails because of a single subject despite an average above 40, students with low attendance who pass and who fail, a student with attendance exactly on the threshold, and a student with exactly 35 marks in one subject.

To use your own data, edit `students.csv` and keep the same column names. If anything is invalid the app lists every problem instead of showing wrong results.

## 7. Provisional grading and passing rules

Maximum total = 4 subjects x 100 = **400**. Student average = total / 4. Pass percentage = passed students / total students x 100.

| Grade | Average |
|---|---|
| A | 90 - 100 |
| B | 80 to below 90 |
| C | 70 to below 80 |
| D | 60 to below 70 |
| E | 40 to below 60 |
| F | below 40 |

- **Pass:** at least **35** marks in **every** subject **and** an overall average of at least **40**. Otherwise **Fail**.
- **Low attendance:** attendance **below 75%**. Attendance is **never** used for pass/fail.
- The grade depends only on the average, so a student can have grade E but still fail (for example, with 30 marks in one subject).
- Students with equal averages share the same rank (1, 1, 3, ...), and all tied students are shown as joint highest, lowest or top performers.

These are **assumptions, not official college rules**. To change them, edit only the *CONFIGURATION* section at the top of `functions.py` (`GRADE_BOUNDARIES`, `PASS_MARK_PER_SUBJECT`, `PASS_AVERAGE`, `LOW_ATTENDANCE_THRESHOLD`). The attendance threshold can also be changed live with the sidebar slider.

---

## 8. Windows installation (run on your own computer)

1. **Install Python** from <https://www.python.org/downloads/>. On the first installer screen tick **"Add python.exe to PATH"**. Check it with `py --version`.
2. **Download and extract** the project ZIP (right-click, *Extract All*).
3. **Open the folder in VS Code:** *File > Open Folder...* and choose `student-performance-analytics`. Open a terminal with *Terminal > New Terminal* (the terminal should already be inside the project folder).

### 9. Create a virtual environment

```
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
```

When it works, the terminal prompt starts with `(.venv)`.

> **PowerShell says "running scripts is disabled"?** Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`, then run `.venv\Scripts\activate` again. Alternatively, open a *Command Prompt* terminal in VS Code instead of PowerShell.

### 10. Install the dependencies

```
pip install -r requirements.txt
```

### 11. Run the application locally

```
streamlit run app.py
```

Your browser opens at <http://localhost:8501>. Press `Ctrl+C` in the terminal to stop the app.

### 12. Run the automated tests

```
python -m unittest -v
```

Every test should be listed as `ok`, ending with `OK`. If a test fails, read the message: it names the calculation or check that failed.

---

## 13. Upload the project to GitHub

**One-time setup:** create a free account at <https://github.com> and install Git for Windows from <https://git-scm.com/download/win>. Then, in the VS Code terminal:

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**Create the repository**

1. On GitHub click **+ > New repository**.
2. Repository name: `student-performance-analytics`. Set it to **Public** (the simplest option for Streamlit Community Cloud).
3. **Do not** tick "Add a README", ".gitignore" or a licence (the project already has its files). Click **Create repository**.

**Upload the files** (from the project folder, with the virtual environment still active or not - it does not matter):

```
git init
git add .
git commit -m "Student Performance Analytics System"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/student-performance-analytics.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. GitHub may ask you to sign in in a browser the first time.

**Verify the upload:** refresh the repository page and check that you can see `app.py`, `functions.py`, `students.csv`, `requirements.txt`, `test_functions.py`, `README.md`, `Project_Documentation.md`, `.gitignore` and the `.streamlit` folder, and that there is **no** `.venv` folder (the `.gitignore` file prevents it).

*No Git?* Alternative: on the repository page choose **Add file > Upload files**, drag in the project files and the `.streamlit` folder (not `.venv`), and click **Commit changes**.

## 14. Deploy on Streamlit Community Cloud

1. Go to <https://share.streamlit.io> and sign in with your GitHub account (authorise access when asked).
2. Click **Create app** and choose to deploy from an existing GitHub repository.
3. Select your repository `student-performance-analytics`, branch `main`, and set **Main file path** to `app.py`.
4. Optionally choose a custom app URL (subdomain), then click **Deploy**.
5. Wait for the build (it installs `requirements.txt`). When it finishes, your public website opens.
6. **Test it:** open every tab, try the filters and the sidebar slider, and download a CSV.

No secrets, API keys or database are needed, so nothing needs to be entered in *Advanced settings* (unless you want to pick a Python version; use 3.10 or newer).

> Menu names on share.streamlit.io may change slightly over time; the idea stays the same: repository + branch + `app.py`.

## 15. Update the deployed application

1. Edit the code or `students.csv` on your computer and test locally (`streamlit run app.py` and `python -m unittest -v`).
2. Upload the changes:
   ```
   git add .
   git commit -m "Describe your change"
   git push
   ```
3. Streamlit Community Cloud detects the new commit and redeploys automatically (refresh the page after a minute). If it does not, open the app's menu on Streamlit Cloud and choose **Reboot app**.

## 16-17. Add your real links

After deployment, paste your real GitHub repository URL and live website URL into:

- the table at the top of this `README.md`, and
- sections 12 and 13 of `Project_Documentation.md`,

then commit and push the change (`git add .`, `git commit -m "Add links"`, `git push`).

---

## Troubleshooting

| Problem | What to do |
|---|---|
| `py` is not recognised | Reinstall Python with *Add python.exe to PATH* ticked, or use `python` instead of `py`. |
| `streamlit` is not recognised | Activate the virtual environment first (`.venv\Scripts\activate`) and run `pip install -r requirements.txt`. |
| The app shows "The student data could not be loaded" | Read the listed problems and fix `students.csv`. |
| Deployment fails with a missing module | Make sure `requirements.txt` is in the repository root and lists all packages. |
