"""
data_manager.py - Data generation, loading, validation, and export utilities
for Student Marks Report Analysis Program.
"""

import pandas as pd
import numpy as np
import io
from typing import Tuple, List, Dict

SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Biology", "Computer_Science", "English"]

FIRST_NAMES = [
    "Aarav", "Diya", "Rohan", "Ananya", "Vivaan", "Isha", "Aditya", "Sneha",
    "Kabir", "Pooja", "Arjun", "Tanvi", "Dev", "Meera", "Rahul", "Kavya",
    "Liam", "Sophia", "Ethan", "Emma", "Lucas", "Olivia", "Noah", "Ava",
    "Mason", "Mia", "Alexander", "Isabella", "James", "Charlotte"
]

LAST_NAMES = [
    "Sharma", "Patel", "Verma", "Iyer", "Gupta", "Reddy", "Nair", "Mehta",
    "Chopra", "Deshmukh", "Smith", "Johnson", "Williams", "Brown", "Jones",
    "Garcia", "Miller", "Davis", "Chen", "Wong", "Khan", "Ahmed", "Taylor"
]

CLASSES = ["Grade 10", "Grade 11", "Grade 12"]
SECTIONS = ["Section A", "Section B"]
TERMS = ["Term 1 (Mid-Year)", "Term 2 (Final)"]


def calculate_grade_and_gpa(percentage: float) -> Tuple[str, float, str]:
    """Return (Grade, GPA on 4.0 scale, Performance Label)."""
    if percentage >= 90:
        return "A+", 4.0, "Outstanding"
    elif percentage >= 80:
        return "A", 3.7, "Excellent"
    elif percentage >= 70:
        return "B+", 3.3, "Very Good"
    elif percentage >= 60:
        return "B", 3.0, "Good"
    elif percentage >= 50:
        return "C", 2.3, "Satisfactory"
    elif percentage >= 40:
        return "D", 1.7, "Pass / Needs Improvement"
    else:
        return "F", 0.0, "Fail / Remedial Needed"


def generate_synthetic_student_data(num_students: int = 120, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic student marks data across multiple subjects and metrics."""
    np.random.seed(seed)
    records = []

    for i in range(1, num_students + 1):
        first = np.random.choice(FIRST_NAMES)
        last = np.random.choice(LAST_NAMES)
        student_name = f"{first} {last}"
        gender = np.random.choice(["Male", "Female", "Non-binary"], p=[0.48, 0.48, 0.04])
        cls = np.random.choice(CLASSES)
        sec = np.random.choice(SECTIONS)
        term = np.random.choice(TERMS, p=[0.4, 0.6])

        # Underlying aptitude & effort factor (latent traits for realistic correlations)
        aptitude = np.random.normal(70, 14)
        aptitude = np.clip(aptitude, 30, 98)

        # Attendance correlated with effort
        attendance = np.clip(np.random.normal(aptitude * 0.4 + 50, 8), 50.0, 99.5)
        
        # Study hours per week correlated with attendance and aptitude
        study_hours = np.clip(np.random.normal((aptitude / 100) * 22 + 4, 4), 3.0, 35.0)

        # Marks for subjects with realistic correlations and slight subject affinities
        math_bias = np.random.normal(0, 8)
        science_bias = np.random.normal(0, 7)
        lang_bias = np.random.normal(0, 6)

        math = np.clip(int(np.random.normal(aptitude + math_bias + (study_hours * 0.4), 6)), 15, 100)
        physics = np.clip(int(np.random.normal(aptitude * 0.85 + math * 0.15 + science_bias, 6)), 18, 100)
        chemistry = np.clip(int(np.random.normal(aptitude * 0.8 + physics * 0.2 + science_bias, 6)), 20, 100)
        biology = np.clip(int(np.random.normal(aptitude * 0.75 + chemistry * 0.15 + np.random.normal(0, 8), 7)), 20, 100)
        comp_sci = np.clip(int(np.random.normal(aptitude * 0.7 + math * 0.3 + np.random.normal(0, 7), 6)), 22, 100)
        english = np.clip(int(np.random.normal(aptitude * 0.6 + lang_bias + 25, 7)), 30, 100)

        subj_marks = [math, physics, chemistry, biology, comp_sci, english]
        total_marks = sum(subj_marks)
        max_marks = len(SUBJECTS) * 100
        percentage = round((total_marks / max_marks) * 100, 2)
        grade, gpa, remarks = calculate_grade_and_gpa(percentage)

        # Pass condition: all subjects >= 40
        passed = all(m >= 40 for m in subj_marks)
        status = "PASSED" if passed else "FAILED"

        # Teacher specific feedback
        if percentage >= 85 and attendance >= 85:
            teacher_note = "Consistently outstanding performance. Demonstrates deep conceptual understanding and leadership."
        elif percentage >= 70:
            teacher_note = "Strong analytical skills and steady participation. Capable of reaching the top tier with focused effort."
        elif percentage >= 50:
            teacher_note = "Shows good foundational knowledge. Needs more practice in problem-solving and structured revision."
        else:
            teacher_note = "Requires targeted remedial mentoring and consistent follow-up on coursework and attendance."

        record = {
            "Roll_No": f"STU-{1000 + i}",
            "Student_Name": student_name,
            "Gender": gender,
            "Class": cls,
            "Section": sec,
            "Term": term,
            "Attendance_Pct": round(float(attendance), 1),
            "Study_Hours_Week": round(float(study_hours), 1),
            "Mathematics": math,
            "Physics": physics,
            "Chemistry": chemistry,
            "Biology": biology,
            "Computer_Science": comp_sci,
            "English": english,
            "Total_Marks": total_marks,
            "Max_Marks": max_marks,
            "Percentage": percentage,
            "GPA": gpa,
            "Grade": grade,
            "Status": status,
            "Performance_Tier": remarks,
            "Teacher_Remarks": teacher_note
        }
        records.append(record)

    df = pd.DataFrame(records)
    # Add Rank within each Class & Term
    df["Rank"] = df.groupby(["Class", "Term"])["Total_Marks"].rank(ascending=False, method="min").astype(int)
    # Overall Rank
    df["Overall_Rank"] = df["Total_Marks"].rank(ascending=False, method="min").astype(int)
    
    return df


def validate_and_process_uploaded_file(uploaded_file) -> Tuple[pd.DataFrame, str]:
    """
    Validate and standardize custom uploaded CSV or Excel file.
    Returns (DataFrame, status_message).
    """
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith((".xls", ".xlsx")):
            df = pd.read_excel(uploaded_file)
        else:
            return pd.DataFrame(), "Unsupported file format. Please upload CSV or Excel (.xlsx)."

        # Standardize column names (strip whitespace)
        df.columns = [str(c).strip() for c in df.columns]

        # Identify roll no and name
        col_lower = {c.lower(): c for c in df.columns}
        
        # Roll No
        roll_candidate = next((c for c in df.columns if "roll" in c.lower() or "id" in c.lower()), None)
        if roll_candidate:
            df["Roll_No"] = df[roll_candidate].astype(str)
        else:
            df["Roll_No"] = [f"STU-{1000 + i}" for i in range(1, len(df) + 1)]

        # Student Name
        name_candidate = next((c for c in df.columns if "name" in c.lower() or "student" in c.lower()), None)
        if name_candidate:
            df["Student_Name"] = df[name_candidate].astype(str)
        else:
            df["Student_Name"] = [f"Student {i}" for i in range(1, len(df) + 1)]

        # Default class, section, term if missing
        if "Class" not in df.columns:
            df["Class"] = "Grade 10"
        if "Section" not in df.columns:
            df["Section"] = "Section A"
        if "Term" not in df.columns:
            df["Term"] = "Term 1"
        if "Gender" not in df.columns:
            df["Gender"] = "Not Specified"
        if "Attendance_Pct" not in df.columns:
            # Check for attendance
            att_col = next((c for c in df.columns if "attend" in c.lower()), None)
            if att_col:
                df["Attendance_Pct"] = pd.to_numeric(df[att_col], errors="coerce").fillna(80.0)
            else:
                df["Attendance_Pct"] = 85.0
        if "Study_Hours_Week" not in df.columns:
            hrs_col = next((c for c in df.columns if "hour" in c.lower() or "study" in c.lower()), None)
            if hrs_col:
                df["Study_Hours_Week"] = pd.to_numeric(df[hrs_col], errors="coerce").fillna(12.0)
            else:
                df["Study_Hours_Week"] = 14.0

        # Find subject columns (numeric columns excluding ID, rank, total, etc.)
        excluded = {"roll_no", "student_name", "class", "section", "term", "gender", 
                    "attendance_pct", "study_hours_week", "total_marks", "max_marks", 
                    "percentage", "gpa", "grade", "status", "rank", "overall_rank"}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        detected_subjects = [c for c in numeric_cols if c.lower() not in excluded and not c.startswith("Unnamed")]

        if len(detected_subjects) < 2:
            return pd.DataFrame(), "Could not detect at least 2 numerical subject score columns in the uploaded file."

        # Ensure values are within 0-100 or convert
        for s in detected_subjects:
            df[s] = pd.to_numeric(df[s], errors="coerce").fillna(0)

        # Recalculate metrics
        df["Total_Marks"] = df[detected_subjects].sum(axis=1)
        df["Max_Marks"] = len(detected_subjects) * 100
        df["Percentage"] = round((df["Total_Marks"] / df["Max_Marks"]) * 100, 2)

        grades, gpas, remarks_list = [], [], []
        for pct in df["Percentage"]:
            g, gpa, rem = calculate_grade_and_gpa(pct)
            grades.append(g)
            gpas.append(gpa)
            remarks_list.append(rem)

        df["Grade"] = grades
        df["GPA"] = gpas
        df["Performance_Tier"] = remarks_list
        df["Status"] = df.apply(lambda row: "PASSED" if all(row[s] >= 40 for s in detected_subjects) else "FAILED", axis=1)

        # Ranks
        df["Rank"] = df.groupby(["Class", "Term"])["Total_Marks"].rank(ascending=False, method="min").astype(int)
        df["Overall_Rank"] = df["Total_Marks"].rank(ascending=False, method="min").astype(int)
        
        if "Teacher_Remarks" not in df.columns:
            df["Teacher_Remarks"] = df["Performance_Tier"].apply(
                lambda t: "Excellent work, keep aiming high!" if "Outstanding" in t or "Excellent" in t
                else ("Good effort, continue consistent practice." if "Good" in t
                else "Needs regular revision and remedial support.")
            )

        return df, f"Successfully imported {len(df)} student records with {len(detected_subjects)} subjects: {', '.join(detected_subjects)}"
    except Exception as e:
        return pd.DataFrame(), f"Error processing file: {str(e)}"


def get_sample_csv_template() -> str:
    """Return CSV template content for user download."""
    sample_df = generate_synthetic_student_data(num_students=5, seed=10)
    cols_to_export = [
        "Roll_No", "Student_Name", "Gender", "Class", "Section", "Term",
        "Attendance_Pct", "Study_Hours_Week",
        "Mathematics", "Physics", "Chemistry", "Biology", "Computer_Science", "English"
    ]
    return sample_df[cols_to_export].to_csv(index=False)
