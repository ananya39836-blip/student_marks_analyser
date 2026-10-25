# 🎓 Student Marks Report Analysis Program
### With Comprehensive 2D Analytics, 3D Spatial Demonstration & IIT Patna Capstone Report Compiler

---

## 🌟 Overview
The **Student Marks Report Analysis Program** is a state-of-the-art academic analytics and report generation platform built using **Python** and **Streamlit**. Designed for modern educators, academic committees, and researchers, the application provides an end-to-end pipeline from exploratory data analysis and 3D spatial demonstration to automated institutional report compilation.

---

## 🚀 Key Features

### 1. 🌐 Advanced 3D Spatial Demonstration
- **3D Academic Coordinate Space:** Full 360-degree interactive 3D scatter plot (Plotly) allowing exploration across three user-selectable subject axes simultaneously.
- **3D Response Surface Modeling:** Multivariate 2nd-degree polynomial regression surface ($Z = f(\text{Attendance}, \text{Study Hours})$) illustrating the non-linear relationship between effort, attendance, and academic yield.
- **3D Machine Learning Clustering (PCA + K-Means):** Unsupervised dimensionality reduction into 3 principal components, categorizing students into 4 distinct learning archetypes (*Top Achievers*, *Solid Performers*, *Emerging Potential*, and *High Risk*).
- **3D Topographical Score Terrain:** 3D elevation landscape mapping student percentile deciles across academic disciplines.

### 2. 📊 Multi-Dimensional 2D Visualizations of All Kinds
- **Grade Distribution Donut Chart** with percentage breakdowns.
- **Cohort Score Histogram** with KDE and mean/median indicators.
- **Subject Benchmark Grouped Bar Charts** with passing (40%) and distinction (75%) thresholds.
- **Box & Violin Dispersion Plots** illustrating score spreads, medians, and outliers.
- **Inter-Disciplinary Correlation Heatmap** (Pearson's $r$).
- **Attendance vs. Marks Scatter Plot** with OLS regression trendline and marginal rugs.
- **Individual Competency Radar (Spider) Charts** comparing individual marks against class averages and toppers.
- **Individual Score Gauge (Speedometer)** showing percentile standing.

### 3. 🎓 IIT Patna Capstone-I Project Report Generator (Strict Template Compliance)
Directly generates and compiles the official **Capstone-I Project Report** for the **Hybrid UG Program in Computer Science & Data Analytics** at **Indian Institute of Technology Patna (Bihta - 801106)**:
- **Page 1: Title Page:** Project title in capital letters, program specification, student credentials, and institutional footer.
- **Page 2: Declaration:** Exact required legal declaration wording with signature and date blocks.
- **Page 3: Summary of the Project & Work Done by Each Member:** Detailed project summary with numbered work breakdown for all team members (1 to 5).
- **Page 4: Content (Table of Contents):** Chapter 1 (Introduction), Chapter 2 (Methodology, Visual Analytics & 3D Demonstration), Chapter 3 (Conclusion & future work).
- **Chapter 1: Introduction:** Overview, motivation, objectives, scope, academic significance, and dataset attributes.
- **Chapter 2: Methodology, Visual Analytics & 3D Demonstration:** Technical architecture, 2D statistical tables, embedded high-resolution figures, 3D demonstration paradigms, and remedial engines.
- **Chapter 3: Conclusion & future work:** Insights, correlation findings, technological impact, and future scope.
- **Formats Supported:** High-resolution **PDF** (via ReportLab) and editable **Microsoft Word (.docx)** (via python-docx).

### 4. 👤 Individual Student Report Card Studio
- Generates official, printable **PDF Report Cards** with school branding, student bio, subject marks, class average comparison, GPA, letter grade, and faculty evaluation notes.

### 5. 🔮 Target Score / What-If Simulator
- Computes the required score on future exams to achieve target honors or grades ($A+, A, B+$), incorporating customizable term weights.

### 6. 📁 Master Excel Gradebook (.xlsx)
- Multi-sheet workbook export with:
  1. *Master Gradebook*
  2. *Subject Analytics & Benchmarks*
  3. *Top Rankers & Honors List*
  4. *Remedial Intervention Plan*
  5. *Grade Distribution*

---

## 💻 Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Pip package manager

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Streamlit Application
```bash
cd C:/Users/HP/.gemini/antigravity/scratch/student_marks_analyzer
streamlit run app.py
```

The application will launch automatically in your default browser at `http://localhost:8501`.

---

## 📁 Project Directory Structure
```
student_marks_analyzer/
│
├── app.py                   # Main Streamlit UI, navigation, and state manager
├── data_manager.py          # Data generation, CSV/Excel parsing, validation, template
├── analytics.py             # Descriptive statistics, correlation, K-Means clustering, what-if models
├── visualizations.py        # Complete Plotly 2D and 3D visual demonstration suite
├── report_generator.py      # IIT Patna Capstone PDF/DOCX, Report Card PDF, Excel generators
├── requirements.txt         # Python package dependencies
├── README.md                # Project documentation and guide
└── .streamlit/
    └── config.toml          # Custom theme and server configuration
```

---

## 🏛️ Academic Affiliation
- **Institution:** Indian Institute of Technology Patna (Bihta - 801106, India)
- **Program:** Hybrid UG Program in Computer Science & Data Analytics
- **Curriculum:** Capstone-I Project Report
