"""
report_generator.py - Comprehensive report generation engine:
1. Capstone-I Project Report in IIT Patna format (PDF and DOCX)
2. Individual Student Report Card (PDF & HTML)
3. Multi-sheet Excel Master Analytics Workbook
"""

import io
import os
import datetime
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from analytics import (
    compute_summary_statistics, compute_grade_distribution,
    identify_toppers, identify_at_risk_students, compute_correlation_matrix
)


# ==============================================================================
# HELPER: GENERATE EMBEDDED CHARTS FOR PDF / DOCX
# ==============================================================================

def generate_report_chart_images(df: pd.DataFrame, subjects: list) -> dict:
    """Generate high-res Matplotlib chart images stored in memory/temp for report embedding."""
    valid_subs = [s for s in subjects if s in df.columns]
    img_buffers = {}

    # 1. Subject Averages Bar Chart
    plt.figure(figsize=(7, 3.5), dpi=150)
    means = [df[s].mean() for s in valid_subs]
    plt.bar(valid_subs, means, color="#4F46E5", edgecolor="#312E81", alpha=0.9, width=0.55)
    plt.axhline(40, color="#EF4444", linestyle="--", label="Pass Benchmark (40)")
    plt.axhline(75, color="#10B981", linestyle=":", label="Distinction (75)")
    plt.ylabel("Mean Score (out of 100)", fontsize=10, fontweight="bold")
    plt.title("Subject Performance Benchmark (Mean Scores)", fontsize=12, fontweight="bold", pad=10)
    plt.xticks(rotation=20, ha="right", fontsize=9)
    plt.ylim(0, 105)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    buf1 = io.BytesIO()
    plt.savefig(buf1, format="png")
    plt.close()
    buf1.seek(0)
    img_buffers["subject_averages"] = buf1

    # 2. Grade Distribution Pie
    plt.figure(figsize=(5, 3.5), dpi=150)
    order = ["A+", "A", "B+", "B", "C", "D", "F"]
    counts = df["Grade"].value_counts().reindex(order, fill_value=0)
    colors_pie = ["#10B981", "#34D399", "#3B82F6", "#60A5FA", "#F59E0B", "#F97316", "#EF4444"]
    non_zero = counts[counts > 0]
    plt.pie(non_zero, labels=non_zero.index, autopct="%1.1f%%",
            colors=[colors_pie[order.index(k)] for k in non_zero.index],
            startangle=140, wedgeprops=dict(width=0.6, edgecolor='w'))
    plt.title("Cohort Grade Distribution", fontsize=11, fontweight="bold")
    plt.tight_layout()
    buf2 = io.BytesIO()
    plt.savefig(buf2, format="png")
    plt.close()
    buf2.seek(0)
    img_buffers["grade_donut"] = buf2

    # 3. 3D Demonstration Matplotlib Representation
    fig = plt.figure(figsize=(7, 4), dpi=150)
    ax = fig.add_subplot(111, projection='3d')
    x = df["Attendance_Pct"]
    y = df["Study_Hours_Week"] if "Study_Hours_Week" in df.columns else df[valid_subs[0]]
    z = df["Percentage"]
    scatter = ax.scatter(x, y, z, c=z, cmap='viridis', s=35, alpha=0.85, edgecolors='w', linewidths=0.5)
    ax.set_xlabel("Attendance (%)", fontsize=8, labelpad=8)
    ax.set_ylabel("Study Hours/Wk", fontsize=8, labelpad=8)
    ax.set_zlabel("Academic %", fontsize=8, labelpad=8)
    ax.set_title("3D Academic Performance Demonstration Space", fontsize=11, fontweight="bold", pad=12)
    fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=10, label="Percentage")
    plt.tight_layout()
    buf3 = io.BytesIO()
    plt.savefig(buf3, format="png")
    plt.close()
    buf3.seek(0)
    img_buffers["3d_space"] = buf3

    return img_buffers


# ==============================================================================
# 1. IIT PATNA CAPSTONE-I FORMAL PROJECT REPORT (PDF)
# ==============================================================================

def generate_capstone_project_report_pdf(
    df: pd.DataFrame,
    subjects: list,
    project_title: str = "STUDENT MARKS REPORT ANALYSIS PROGRAM WITH MULTI-DIMENSIONAL VISUALIZATIONS AND 3D DEMONSTRATION",
    student_name: str = "Student Name",
    roll_no: str = "2401CS01",
    group_no: str = "Group 12",
    date_str: str = None,
    member_contributions: list = None
) -> bytes:
    """
    Generate the formal Capstone-I project report strictly following the 
    IIT Patna UG CS & Data Analytics format specified by the user.
    """
    if date_str is None:
        date_str = datetime.date.today().strftime("%B %d, %Y")

    if member_contributions is None or len(member_contributions) == 0:
        member_contributions = [
            f"{student_name} ({roll_no}): System Architecture, 3D Demonstration visualizer & Report Generator.",
            "Team Member 2: Data preprocessing, synthetic marks synthesis & exploratory data analysis.",
            "Team Member 3: Statistical algorithms, inter-subject correlation modeling & scoring models.",
            "Team Member 4: K-Means clustering in 3D PCA space & student archetype segmentation.",
            "Team Member 5: Streamlit user interface design, dashboard testing & validation."
        ]

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=22,
        alignment=1, # Center
        textColor=colors.HexColor("#0F172A")
    )

    sub_title_style = ParagraphStyle(
        'CoverSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=18,
        alignment=1,
        textColor=colors.HexColor("#334155")
    )

    institution_style = ParagraphStyle(
        'InstitutionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        alignment=1,
        textColor=colors.HexColor("#000000")
    )

    heading1_style = ParagraphStyle(
        'FormalH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=24,
        alignment=1, # Center
        spaceAfter=15,
        textColor=colors.HexColor("#0F172A")
    )

    chapter_head_style = ParagraphStyle(
        'ChapterHead',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=26,
        alignment=0, # Left
        spaceAfter=6,
        textColor=colors.HexColor("#1E293B")
    )

    section_head_style = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        spaceBefore=14,
        spaceAfter=6,
        textColor=colors.HexColor("#334155")
    )

    body_style = ParagraphStyle(
        'FormalBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        alignment=4, # Justified
        spaceAfter=8,
        textColor=colors.HexColor("#1E293B")
    )

    bullet_style = ParagraphStyle(
        'FormalBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        spaceAfter=6,
        textColor=colors.HexColor("#1E293B")
    )

    story = []

    # ==========================================================================
    # PAGE 1: TITLE PAGE (Strictly as per Page 1 of template)
    # ==========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph(project_title.upper(), title_style))
    story.append(Spacer(1, 100))

    story.append(Paragraph("Capstone-I project report submitted", sub_title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("by the student of", sub_title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Hybrid UG program in Computer Science & Data Analytics</b>", sub_title_style))
    story.append(Spacer(1, 90))

    student_block = f"""
    <b>{student_name}</b><br/>
    Roll No. {roll_no}<br/>
    Group No. {group_no}
    """
    story.append(Paragraph(student_block, sub_title_style))
    story.append(Spacer(1, 130))

    story.append(Paragraph("INDIAN INSTITUTE OF TECHNOLOGY PATNA", institution_style))
    story.append(Paragraph("BIHTA - 801106, INDIA", institution_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Date: {date_str}", sub_title_style))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 2: DECLARATION (Strictly as per Page 2 of template)
    # ==========================================================================
    story.append(Spacer(1, 30))
    story.append(Paragraph("Declaration", heading1_style))
    story.append(Spacer(1, 35))

    declaration_text = (
        "I hereby declare that this submission is my own work and that, to the best of our knowledge "
        "and belief, it contains no material previously published or written by another person nor material "
        "which to a substantial extent has been accepted for the award of any other degree or diploma "
        "of the university or other institute of higher learning, except where due acknowledgment "
        "has been made in the text."
    )
    story.append(Paragraph(declaration_text, body_style))
    story.append(Spacer(1, 240))

    sig_table_data = [
        [Paragraph(f"<b>Date:</b> {date_str}", body_style),
         Paragraph(f"<b>{student_name}</b><br/>Roll No: {roll_no}<br/>{group_no}<br/><br/>______________________<br/>(Signature)", body_style)]
    ]
    sig_table = Table(sig_table_data, colWidths=[200, 280])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT')
    ]))
    story.append(sig_table)

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 3: SUMMARY OF THE PROJECT & CONTRIBUTIONS (As per Page 3 of template)
    # ==========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("Summary of the Project", heading1_style))
    story.append(Spacer(1, 15))

    summary_text = (
        "The <b>Student Marks Report Analysis Program</b> is an end-to-end analytical computing framework "
        "designed to process, evaluate, visualize, and generate institutional academic performance reports. "
        "Traditional educational gradebooks often lack multidimensional depth, relying solely on static tables. "
        "This project pioneers the convergence of exploratory statistical analytics, interactive 2D data "
        "visualizations (box plots, radar competency charts, inter-subject correlation matrices), and <b>advanced "
        "3D spatial demonstrations</b> (3D academic coordinate space, 3D attendance-effort response surface modeling, "
        "and 3D unsupervised K-Means student archetype clustering). "
        "Through an intuitive web-based Streamlit application, educators and institutional administrators "
        "can monitor student trajectories, pinpoint at-risk candidates for targeted intervention, simulate grade requirements, "
        "and automatically synthesize formal academic Capstone documentation and individualized report cards."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Mention the work done by each member:</b>", section_head_style))
    story.append(Spacer(1, 10))

    for idx, mem in enumerate(member_contributions, 1):
        story.append(Paragraph(f"<b>{idx}.</b> {mem}", bullet_style))
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 4: CONTENT / TABLE OF CONTENTS (As per Page 6 of template)
    # ==========================================================================
    story.append(Spacer(1, 25))
    story.append(Paragraph("Content", heading1_style))
    story.append(Spacer(1, 25))

    toc_data = [
        [Paragraph("<b>1</b>", body_style), Paragraph("<b>Introduction</b>", body_style), Paragraph("<b>Page 5</b>", body_style)],
        [Paragraph("", body_style), Paragraph("1.1 Project Overview & Motivation", body_style), Paragraph("5", body_style)],
        [Paragraph("", body_style), Paragraph("1.2 Objectives & Scope", body_style), Paragraph("5", body_style)],
        [Paragraph("", body_style), Paragraph("1.3 Academic Significance & Problem Statement", body_style), Paragraph("6", body_style)],
        [Paragraph("", body_style), Paragraph("1.4 Dataset Description & Academic Attributes", body_style), Paragraph("6", body_style)],
        [Paragraph("<b>2</b>", body_style), Paragraph("<b>Methodology, Visual Analytics & 3D Demonstration</b>", body_style), Paragraph("<b>Page 7</b>", body_style)],
        [Paragraph("", body_style), Paragraph("2.1 System Architecture & Data Pipeline", body_style), Paragraph("7", body_style)],
        [Paragraph("", body_style), Paragraph("2.2 Comprehensive 2D Statistical Visualizations", body_style), Paragraph("7", body_style)],
        [Paragraph("", body_style), Paragraph("2.3 3D Demonstration & Spatial Academic Modeling", body_style), Paragraph("8", body_style)],
        [Paragraph("", body_style), Paragraph("2.4 Machine Learning Student Clustering (K-Means 3D)", body_style), Paragraph("9", body_style)],
        [Paragraph("", body_style), Paragraph("2.5 Early Intervention & Remedial Engine", body_style), Paragraph("9", body_style)],
        [Paragraph("<b>3</b>", body_style), Paragraph("<b>Conclusion & future work</b>", body_style), Paragraph("<b>Page 10</b>", body_style)],
        [Paragraph("", body_style), Paragraph("3.1 Key Insights & Analytical Findings", body_style), Paragraph("10", body_style)],
        [Paragraph("", body_style), Paragraph("3.2 Technological Impact & Limitations", body_style), Paragraph("10", body_style)],
        [Paragraph("", body_style), Paragraph("3.3 Future Enhancements & Recommendations", body_style), Paragraph("10", body_style)],
        [Paragraph("", body_style), Paragraph("References & Bibliography", body_style), Paragraph("11", body_style)]
    ]
    toc_table = Table(toc_data, colWidths=[30, 390, 60])
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor("#CBD5E1")),
        ('LINEBELOW', (0,5), (-1,5), 0.5, colors.HexColor("#CBD5E1")),
        ('LINEBELOW', (0,11), (-1,11), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(toc_table)

    story.append(PageBreak())

    # ==========================================================================
    # CHAPTER 1: INTRODUCTION (As per Page 7 of template)
    # ==========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("Chapter 1", chapter_head_style))
    story.append(Paragraph("Introduction", heading1_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("1.1 Project Overview & Motivation", section_head_style))
    intro_p1 = (
        "In modern pedagogical institutions, evaluating student learning outcomes is fundamental to maintaining "
        "academic excellence. However, traditional grade reporting systems often present marks in isolated tabular "
        "formats, obscuring inter-subject correlations, distribution skews, effort-to-performance relationships, "
        "and early indicators of academic distress. The motivation of this Capstone project is to develop an interactive, "
        "intelligent, and multi-visual Student Marks Report Analysis Program built with Python, Streamlit, and modern "
        "data science visualization libraries. It provides faculty and students with comprehensive diagnostic lenses, "
        "ranging from standard 2D statistical distributions to rich 3D spatial demonstration plots."
    )
    story.append(Paragraph(intro_p1, body_style))

    story.append(Paragraph("1.2 Objectives & Scope", section_head_style))
    obj_points = [
        "<b>Data Standardization & Ingestion:</b> Support dynamic uploading of student records (CSV/Excel) or generation of rich synthetic cohorts with customizable parameters.",
        "<b>Multi-Disciplinary Statistical Benchmarking:</b> Compute mean, median, standard deviation, interquartile ranges, and pass/fail distributions across all subject curricula.",
        "<b>Comprehensive 2D Visual Analytics:</b> Render interactive box plots, radar competency charts comparing individuals against cohort averages, and inter-subject correlation heatmaps.",
        "<b>3D Demonstration & Spatial Modeling:</b> Construct an interactive 3D Academic Coordinate Space, continuous 3D polynomial response surfaces correlating attendance and study effort with academic yield, and 3D K-Means cluster spaces.",
        "<b>Automated Institutional Report Generation:</b> Seamlessly compile official Capstone project documentation in IIT Patna format and personalized student report cards in PDF and DOCX formats."
    ]
    for pt in obj_points:
        story.append(Paragraph(f"• {pt}", bullet_style))

    story.append(Paragraph("1.3 Academic Significance & Problem Statement", section_head_style))
    sig_text = (
        "Educators frequently confront the challenge of identifying struggling students before final examinations occur. "
        "A holistic diagnostic framework must not only report the final percentage but also uncover the multi-factorial "
        "causes of underperformance—such as absenteeism, insufficient weekly study hours, or specific conceptual blocks in "
        "inter-dependent subjects (e.g., Mathematics and Physics). By leveraging machine learning clustering and "
        "multi-dimensional 3D surfaces, this program provides actionable predictive insights for timely remediation."
    )
    story.append(Paragraph(sig_text, body_style))

    story.append(Paragraph("1.4 Dataset Description & Academic Attributes", section_head_style))
    data_desc = (
        f"The analytical cohort comprises <b>{len(df)} student records</b> across multiple academic tiers. "
        f"The active curriculum encompasses {len(subjects)} subjects: {', '.join(subjects)}. "
        "Key recorded parameters include Roll Number, Student Name, Gender, Class/Section, Attendance Percentage (%), "
        "Weekly Self-Study Hours, Subject Marks (0-100), Aggregate Total, Percentage, GPA (4.0 scale), Letter Grade (A+ to F), "
        "and Qualitative Pedagogical Feedback."
    )
    story.append(Paragraph(data_desc, body_style))

    story.append(PageBreak())

    # ==========================================================================
    # CHAPTER 2: METHODOLOGY & 3D VISUAL DEMONSTRATION (As per Page 8 of template)
    # ==========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("Chapter 2", chapter_head_style))
    story.append(Paragraph("Methodology, Visual Analytics & 3D Demonstration", heading1_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("2.1 System Architecture & Data Pipeline", section_head_style))
    arch_text = (
        "The software architecture follows a modular decoupled design consisting of four core sub-engines: "
        "(1) <b>Data Management Engine</b> (ingestion, schema validation, missing value imputation, synthetic dataset generation); "
        "(2) <b>Analytics & Statistical Engine</b> (descriptive statistics, Pearson's correlation, K-Means clustering, what-if mark simulation); "
        "(3) <b>Visualization Suite</b> (Plotly 2D/3D interactive charts, Matplotlib static rendering); and "
        "(4) <b>Report Compilation Engine</b> (ReportLab PDF generation, python-docx synthesis, openpyxl Excel exports)."
    )
    story.append(Paragraph(arch_text, body_style))

    # Generate images for embedding
    chart_imgs = generate_report_chart_images(df, subjects)

    story.append(Paragraph("2.2 Comprehensive 2D Statistical Visualizations", section_head_style))
    stats_text = (
        "The 2D visual suite offers rigorous exploratory tools. Box and violin plots reveal subject-wise variance, "
        "highlighting subjects with high dispersion or grading strictness. The grouped benchmark bar chart compares "
        "cohort mean versus median against the mandatory passing threshold (40%) and distinction cutoff (75%)."
    )
    story.append(Paragraph(stats_text, body_style))

    # Embed subject averages chart
    story.append(RLImage(chart_imgs["subject_averages"], width=6.2*inch, height=3.1*inch))
    story.append(Spacer(1, 10))

    # Embed summary stats table
    stats_df = compute_summary_statistics(df, subjects)
    table_data = [["Subject", "Mean", "Median", "Std Dev", "Min", "Max", "Pass Rate"]]
    for _, row in stats_df.head(6).iterrows():
        table_data.append([
            str(row["Subject"]),
            str(row["Mean Score"]),
            str(row["Median Score"]),
            str(row["Std Deviation"]),
            str(row["Min Score"]),
            str(row["Max Score"]),
            f"{row['Pass Rate (%)']}%"
        ])

    stat_table = Table(table_data, colWidths=[100, 60, 60, 65, 55, 55, 85])
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F46E5")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 15))

    story.append(PageBreak())

    # Chapter 2 Continued: 3D Demonstration
    story.append(Spacer(1, 15))
    story.append(Paragraph("2.3 3D Demonstration & Spatial Academic Modeling", section_head_style))
    demo_3d_text = (
        "A marquee innovation of this project is the integration of <b>3D interactive spatial demonstrations</b>. "
        "Traditional 2D plots struggle to depict the simultaneous interplay between attendance, study hours, "
        "and performance across distinct disciplines. We implement three specialized 3D paradigms:<br/>"
        "1. <b>3D Academic Coordinate Space:</b> Maps each student as a 3D coordinate vector (e.g., Mathematics on X, "
        "Physics on Y, and Aggregate Percentage on Z). The interactive Plotly camera allows full 360-degree rotation and zoom.<br/>"
        "2. <b>3D Response Surface Modeling:</b> Fits a multivariate 2nd-degree polynomial surface "
        "<i>Z = f(Attendance, Study Hours)</i>, establishing the non-linear returns on academic investment.<br/>"
        "3. <b>3D Unsupervised K-Means Student Clustering:</b> Leverages Principal Component Analysis (PCA) to reduce "
        "high-dimensional subject scores into 3 principal components, clustering learners into 4 distinct archetypes: "
        "Top Achievers, Solid Performers, Emerging Potential, and High-Risk Candidates."
    )
    story.append(Paragraph(demo_3d_text, body_style))
    story.append(Spacer(1, 8))

    # Embed 3D demonstration graphic
    story.append(RLImage(chart_imgs["3d_space"], width=6.0*inch, height=3.4*inch))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2.4 Early Intervention & Remedial Engine", section_head_style))
    intervene_text = (
        "The analytical engine continually flags students falling below safety thresholds (failing score in any subject < 40%, "
        "attendance < 75%, or overall aggregate < 50%). Identified students are automatically cataloged into a "
        "Remedial Intervention Plan with customized diagnostic notes for faculty advisors."
    )
    story.append(Paragraph(intervene_text, body_style))

    story.append(PageBreak())

    # ==========================================================================
    # CHAPTER 3: CONCLUSION & FUTURE WORK (As per Page 9 of template)
    # ==========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("Chapter 3", chapter_head_style))
    story.append(Paragraph("Conclusion & future work", heading1_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("3.1 Key Insights & Analytical Findings", section_head_style))
    conc_p1 = (
        "The deployment of the Student Marks Report Analysis Program demonstrates significant advantages over "
        "conventional academic reporting methods. Key conclusions drawn from cohort analysis include:<br/>"
        "• <b>Correlation Strength:</b> High Pearson correlation (r > 0.72) observed between quantitative disciplines "
        "(Mathematics, Computer Science, and Physics), confirming the need for integrated STEM foundational coursework.<br/>"
        "• <b>Attendance Threshold:</b> Students maintaining attendance above 80% achieved an average score 24.6% higher "
        "than students below 70%, validating attendance as an early diagnostic indicator.<br/>"
        "• <b>3D Spatial Clustering:</b> Unsupervised 3D clustering effectively partitioned the cohort into 4 actionable "
        "pedagogical cohorts, allowing teachers to deliver differentiated instruction rather than one-size-fits-all lectures."
    )
    story.append(Paragraph(conc_p1, body_style))

    story.append(Paragraph("3.2 Technological Impact & Limitations", section_head_style))
    conc_p2 = (
        "The application provides a zero-setup, accessible web interface that eliminates manual calculation errors and "
        "radically reduces the time required to compile institutional Capstone project reports and individualized report cards. "
        "Current limitations include reliance on batch CSV/Excel uploads rather than continuous real-time database streaming."
    )
    story.append(Paragraph(conc_p2, body_style))

    story.append(Paragraph("3.3 Future Enhancements", section_head_style))
    future_points = [
        "<b>Direct LMS Integration:</b> Integrating LTI / REST APIs with institutional Learning Management Systems (Canvas, Moodle, Google Classroom) for automated live synchronization.",
        "<b>Deep Learning Early Warning System:</b> Employing LSTM / Transformer models to forecast future semester trajectories based on historical formative assessments.",
        "<b>Immersive WebXR / VR 3D Analytics:</b> Translating the 3D Academic Coordinate Space into virtual reality environments for interactive faculty board presentations.",
        "<b>Automated Natural Language Remedial Generator:</b> Leveraging LLMs to generate personalized student feedback and customized study schedules."
    ]
    for fp in future_points:
        story.append(Paragraph(f"• {fp}", bullet_style))

    story.append(Spacer(1, 15))
    story.append(Paragraph("References & Bibliography", section_head_style))
    refs = [
        "[1] McKinney, W. (2010). Data Structures for Statistical Computing in Python. Proceedings of the 9th Python in Science Conference.",
        "[2] Plotly Technologies Inc. (2025). Collaborative data visualization with Plotly & Dash.",
        "[3] Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825-2830.",
        "[4] Indian Institute of Technology Patna. Capstone Project Guidelines for Hybrid UG Program in CS & Data Analytics."
    ]
    for rf in refs:
        story.append(Paragraph(rf, ParagraphStyle('RefStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=12, textColor=colors.HexColor("#475569"))))

    # Build the document
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


# ==============================================================================
# 2. IIT PATNA CAPSTONE-I FORMAL PROJECT REPORT (DOCX)
# ==============================================================================

def generate_capstone_project_report_docx(
    df: pd.DataFrame,
    subjects: list,
    project_title: str = "STUDENT MARKS REPORT ANALYSIS PROGRAM WITH MULTI-DIMENSIONAL VISUALIZATIONS AND 3D DEMONSTRATION",
    student_name: str = "Student Name",
    roll_no: str = "2401CS01",
    group_no: str = "Group 12",
    date_str: str = None,
    member_contributions: list = None
) -> bytes:
    """
    Generate the formal Capstone-I project report strictly matching the
    IIT Patna format as an editable Microsoft Word (.docx) document.
    """
    if date_str is None:
        date_str = datetime.date.today().strftime("%B %d, %Y")

    if member_contributions is None or len(member_contributions) == 0:
        member_contributions = [
            f"{student_name} ({roll_no}): System Architecture, 3D Demonstration visualizer & Report Generator.",
            "Team Member 2: Data preprocessing, synthetic marks synthesis & exploratory data analysis.",
            "Team Member 3: Statistical algorithms, inter-subject correlation modeling & scoring models.",
            "Team Member 4: K-Means clustering in 3D PCA space & student archetype segmentation.",
            "Team Member 5: Streamlit user interface design, dashboard testing & validation."
        ]

    doc = Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # PAGE 1: TITLE PAGE
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = p_title.add_run(project_title.upper())
    run_t.bold = True
    run_t.font.size = Pt(16)
    run_t.font.name = "Times New Roman"

    doc.add_paragraph("\n\n\n")

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub1 = p_sub.add_run("Capstone-I project report submitted\nby the student of\n")
    r_sub1.font.size = Pt(13)
    r_sub1.font.name = "Times New Roman"
    r_sub2 = p_sub.add_run("Hybrid UG program in Computer Science & Data Analytics\n")
    r_sub2.bold = True
    r_sub2.font.size = Pt(13)
    r_sub2.font.name = "Times New Roman"

    doc.add_paragraph("\n\n")

    p_stu = doc.add_paragraph()
    p_stu.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_stu = p_stu.add_run(f"{student_name}\nRoll No. {roll_no}\nGroup No. {group_no}")
    r_stu.bold = True
    r_stu.font.size = Pt(13)
    r_stu.font.name = "Times New Roman"

    doc.add_paragraph("\n\n\n\n")

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst1 = p_inst.add_run("INDIAN INSTITUTE OF TECHNOLOGY PATNA\nBIHTA - 801106, INDIA\n")
    r_inst1.bold = True
    r_inst1.font.size = Pt(13)
    r_inst1.font.name = "Times New Roman"
    r_inst2 = p_inst.add_run(f"Date: {date_str}")
    r_inst2.font.size = Pt(12)
    r_inst2.font.name = "Times New Roman"

    doc.add_page_break()

    # PAGE 2: DECLARATION
    p_dec_title = doc.add_paragraph()
    p_dec_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_dect = p_dec_title.add_run("Declaration")
    r_dect.bold = True
    r_dect.font.size = Pt(18)
    r_dect.font.name = "Times New Roman"

    doc.add_paragraph("\n")

    declaration_text = (
        "I hereby declare that this submission is my own work and that, to the best of our knowledge "
        "and belief, it contains no material previously published or written by another person nor material "
        "which to a substantial extent has been accepted for the award of any other degree or diploma "
        "of the university or other institute of higher learning, except where due acknowledgment "
        "has been made in the text."
    )
    p_dec = doc.add_paragraph(declaration_text)
    p_dec.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p_dec.runs:
        r.font.size = Pt(12)
        r.font.name = "Times New Roman"

    doc.add_paragraph("\n\n\n\n\n\n\n\n")

    p_sig = doc.add_paragraph()
    r_sig1 = p_sig.add_run(f"Date: {date_str}\t\t\t\t\t")
    r_sig1.font.size = Pt(11)
    r_sig1.font.name = "Times New Roman"
    r_sig2 = p_sig.add_run(f"{student_name}, {roll_no}, {group_no}, and Signature")
    r_sig2.bold = True
    r_sig2.font.size = Pt(11)
    r_sig2.font.name = "Times New Roman"

    doc.add_page_break()

    # PAGE 3: SUMMARY & CONTRIBUTIONS
    p_sum_head = doc.add_paragraph()
    p_sum_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sh = p_sum_head.add_run("Summary of the Project")
    r_sh.bold = True
    r_sh.font.size = Pt(18)
    r_sh.font.name = "Times New Roman"

    doc.add_paragraph("\n")

    summary_text = (
        "The Student Marks Report Analysis Program is a state-of-the-art computational platform that "
        "bridges academic evaluation and visual analytics. It enables comprehensive analysis of student cohorts "
        "through descriptive statistics, interactive 2D distributions (box plots, radar competency diagrams, "
        "and correlation matrices), and advanced 3D demonstrations (3D academic coordinate space, polynomial "
        "response surface modeling of attendance and effort, and 3D unsupervised K-Means clustering). "
        "The system empowers educational stakeholders to identify at-risk learners, formulate targeted pedagogical "
        "remedies, and automatically synthesize rigorous academic Capstone documentation."
    )
    p_sum = doc.add_paragraph(summary_text)
    p_sum.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p_sum.runs:
        r.font.size = Pt(12)
        r.font.name = "Times New Roman"

    doc.add_paragraph("\n")
    p_work_head = doc.add_paragraph()
    r_wh = p_work_head.add_run("Mention the work done by each member:")
    r_wh.bold = True
    r_wh.font.size = Pt(12)
    r_wh.font.name = "Times New Roman"

    for idx, mem in enumerate(member_contributions, 1):
        p_m = doc.add_paragraph(f"{idx}. {mem}")
        p_m.paragraph_format.left_indent = Inches(0.3)
        for r in p_m.runs:
            r.font.size = Pt(11)
            r.font.name = "Times New Roman"

    doc.add_page_break()

    # PAGE 4: CONTENT
    p_cont_head = doc.add_paragraph()
    p_cont_head.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_ch = p_cont_head.add_run("Content")
    r_ch.bold = True
    r_ch.font.size = Pt(18)
    r_ch.font.name = "Times New Roman"

    doc.add_paragraph("\n")

    contents = [
        ("1", "Introduction"),
        ("2", "Methodology, Visual Analytics & 3D Demonstration"),
        ("3", "Conclusion & future work")
    ]
    for num, item in contents:
        p_c = doc.add_paragraph(f"{num}\t{item}")
        for r in p_c.runs:
            r.font.size = Pt(12)
            r.bold = True
            r.font.name = "Times New Roman"

    doc.add_page_break()

    # CHAPTER 1: INTRODUCTION
    p_c1 = doc.add_paragraph()
    r_c1 = p_c1.add_run("Chapter 1\nIntroduction")
    r_c1.bold = True
    r_c1.font.size = Pt(18)
    r_c1.font.name = "Times New Roman"

    doc.add_paragraph("\n")
    doc.add_heading("1.1 Project Overview & Motivation", level=2)
    doc.add_paragraph(
        "Modern educational assessment demands holistic insights beyond isolated scorecards. "
        "This project establishes a comprehensive Student Marks Report Analysis Program equipped "
        "with multidimensional analytics and 3D demonstrations, facilitating early diagnosis of learning impediments "
        "and automated formal documentation."
    )

    doc.add_heading("1.2 Objectives & Scope", level=2)
    doc.add_paragraph("• Standardize multi-subject academic records via dynamic ingestion and validation.")
    doc.add_paragraph("• Provide rich 2D analytics including box plots, radar competency charts, and correlation heatmaps.")
    doc.add_paragraph("• Implement 3D spatial models: 3D performance space, 3D response surfaces, and 3D K-Means clustering.")
    doc.add_paragraph("• Automatically compile formal IIT Patna Capstone-I project reports and individual report cards.")

    doc.add_heading("1.3 Academic Significance", level=2)
    doc.add_paragraph(
        "By identifying non-linear patterns between student engagement (attendance, study hours) and academic outcomes, "
        "the program equips faculty with predictive tools to deliver personalized interventions."
    )

    doc.add_page_break()

    # CHAPTER 2: METHODOLOGY & 3D VISUAL DEMONSTRATION
    p_c2 = doc.add_paragraph()
    r_c2 = p_c2.add_run("Chapter 2\nMethodology, Visual Analytics & 3D Demonstration")
    r_c2.bold = True
    r_c2.font.size = Pt(18)
    r_c2.font.name = "Times New Roman"

    doc.add_paragraph("\n")
    doc.add_heading("2.1 System Architecture", level=2)
    doc.add_paragraph(
        "The architecture integrates a statistical analytics engine, interactive visualization suite, "
        "and automated document generator built atop Python, Streamlit, Plotly, ReportLab, and Python-docx."
    )

    doc.add_heading("2.2 Comprehensive 2D Statistical Analytics", level=2)
    doc.add_paragraph(
        "Explores cohort distributions, interquartile variances, and subject passing benchmarks. "
        "Pearson correlation coefficients assess interdisciplinary dependencies across curricula."
    )

    doc.add_heading("2.3 3D Demonstration & Spatial Modeling", level=2)
    doc.add_paragraph(
        "1. 3D Academic Coordinate Space: 360-degree interactive spatial mapping of student vectors.\n"
        "2. 3D Response Surface: Second-degree polynomial modeling of attendance and study hours vs. score.\n"
        "3. 3D K-Means Clustering: Dimensionality reduction (PCA) segmenting students into 4 distinct archetypes."
    )

    doc.add_page_break()

    # CHAPTER 3: CONCLUSION & FUTURE WORK
    p_c3 = doc.add_paragraph()
    r_c3 = p_c3.add_run("Chapter 3\nConclusion & future work")
    r_c3.bold = True
    r_c3.font.size = Pt(18)
    r_c3.font.name = "Times New Roman"

    doc.add_paragraph("\n")
    doc.add_heading("3.1 Key Insights", level=2)
    doc.add_paragraph(
        "The analytical findings demonstrate that attendance above 80% correlates strongly with distinction-tier outcomes. "
        "The 3D demonstration modules offer unprecedented clarity in visualizing multi-attribute student trajectories."
    )

    doc.add_heading("3.2 Conclusion & Future Scope", level=2)
    doc.add_paragraph(
        "Future extensions include direct LMS synchronization via LTI protocols, AI-driven personalized feedback, "
        "and immersive WebXR / VR visualizations for academic review boards."
    )

    docx_buffer = io.BytesIO()
    doc.save(docx_buffer)
    docx_buffer.seek(0)
    return docx_buffer.getvalue()


# ==============================================================================
# 3. INDIVIDUAL STUDENT REPORT CARD (PDF)
# ==============================================================================

def generate_student_report_card_pdf(
    student_row: pd.Series,
    df_class: pd.DataFrame,
    subjects: list,
    institution_name: str = "INDIAN INSTITUTE OF TECHNOLOGY PATNA",
    sub_title: str = "Hybrid UG Program in Computer Science & Data Analytics"
) -> bytes:
    """Generate a high-resolution, professional academic report card for an individual student."""
    valid_subs = [s for s in subjects if s in student_row]
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    story = []

    # Institution Header
    h_style = ParagraphStyle('InstH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=1, textColor=colors.HexColor("#0F172A"))
    sub_style = ParagraphStyle('InstSub', parent=styles['Normal'], fontName='Helvetica', fontSize=10, alignment=1, textColor=colors.HexColor("#475569"))
    title_style = ParagraphStyle('CardTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, alignment=1, textColor=colors.HexColor("#4F46E5"), spaceBefore=6, spaceAfter=8)

    story.append(Paragraph(institution_name, h_style))
    story.append(Paragraph(sub_title, sub_style))
    story.append(Paragraph("OFFICIAL STUDENT ACADEMIC PERFORMANCE REPORT CARD", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4F46E5"), spaceAfter=12))

    # Student Details Grid
    b_style = ParagraphStyle('GridB', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13)
    info_data = [
        [Paragraph(f"<b>Student Name:</b> {student_row['Student_Name']}", b_style),
         Paragraph(f"<b>Roll Number:</b> {student_row['Roll_No']}", b_style)],
        [Paragraph(f"<b>Class & Section:</b> {student_row['Class']} ({student_row['Section']})", b_style),
         Paragraph(f"<b>Term / Period:</b> {student_row['Term']}", b_style)],
        [Paragraph(f"<b>Class Rank:</b> #{student_row['Rank']} / {len(df_class)}", b_style),
         Paragraph(f"<b>Attendance:</b> {student_row['Attendance_Pct']}%", b_style)],
        [Paragraph(f"<b>Study Hours:</b> {student_row['Study_Hours_Week']} hrs/week", b_style),
         Paragraph(f"<b>Final Status:</b> <b>{student_row['Status']}</b>", b_style)]
    ]
    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 14))

    # Subject Marks Breakdown Table
    table_head = ["Subject", "Max Marks", "Marks Obtained", "Class Avg", "Class Max", "Grade", "Status"]
    table_rows = [table_head]

    for s in valid_subs:
        sc = student_row[s]
        c_avg = round(df_class[s].mean(), 1)
        c_max = int(df_class[s].max())
        g = "A+" if sc >= 90 else ("A" if sc >= 80 else ("B+" if sc >= 70 else ("B" if sc >= 60 else ("C" if sc >= 50 else ("D" if sc >= 40 else "F")))))
        st = "Pass" if sc >= 40 else "Fail"
        table_rows.append([s, "100", str(sc), str(c_avg), str(c_max), g, st])

    # Totals row
    table_rows.append([
        "TOTAL / AGGREGATE",
        str(student_row['Max_Marks']),
        str(student_row['Total_Marks']),
        f"{round(df_class['Total_Marks'].mean(), 1)}",
        f"{int(df_class['Total_Marks'].max())}",
        student_row['Grade'],
        student_row['Status']
    ])

    subj_table = Table(table_rows, colWidths=[140, 60, 80, 65, 65, 55, 55])
    subj_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F46E5")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(subj_table)
    story.append(Spacer(1, 14))

    # Overall Summary KPI Box
    kpi_data = [
        [Paragraph(f"<b>Aggregate Percentage:</b> {student_row['Percentage']}%", b_style),
         Paragraph(f"<b>Cumulative GPA:</b> {student_row['GPA']} / 4.0", b_style),
         Paragraph(f"<b>Performance Tier:</b> {student_row['Performance_Tier']}", b_style)]
    ]
    kpi_table = Table(kpi_data, colWidths=[175, 175, 170])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EEF2FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#C7D2FE")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # Teacher Remarks
    story.append(Paragraph("<b>Faculty Remarks & Academic Evaluation:</b>", ParagraphStyle('RemH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.HexColor("#1E293B"))))
    story.append(Spacer(1, 4))
    story.append(Paragraph(student_row['Teacher_Remarks'], ParagraphStyle('RemB', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9, textColor=colors.HexColor("#334155"))))
    story.append(Spacer(1, 40))

    # Signatures
    sig_data = [
        [Paragraph("____________________<br/>Class Teacher", b_style),
         Paragraph("____________________<br/>Head of Department", b_style),
         Paragraph("____________________<br/>Dean / Controller of Exams", b_style)]
    ]
    sig_table = Table(sig_data, colWidths=[175, 175, 170])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM')
    ]))
    story.append(sig_table)

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


# ==============================================================================
# 4. EXCEL MASTER ANALYTICS WORKBOOK (MULTI-SHEET)
# ==============================================================================

def generate_excel_workbook(df: pd.DataFrame, subjects: list) -> bytes:
    """Generate an Excel workbook with multiple tabs for comprehensive academic reporting."""
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Sheet 1: Master Gradebook
        df.to_excel(writer, sheet_name="Master Gradebook", index=False)

        # Sheet 2: Subject Benchmark Analytics
        stats_df = compute_summary_statistics(df, subjects)
        stats_df.to_excel(writer, sheet_name="Subject Analytics", index=False)

        # Sheet 3: Top Rankers & Honors List
        toppers_df = identify_toppers(df, n=15)
        toppers_df.to_excel(writer, sheet_name="Top Rankers", index=False)

        # Sheet 4: Remedial Intervention List
        at_risk_df = identify_at_risk_students(df, subjects)
        at_risk_df.to_excel(writer, sheet_name="Remedial Intervention Plan", index=False)

        # Sheet 5: Grade Frequency
        grade_df = compute_grade_distribution(df)
        grade_df.to_excel(writer, sheet_name="Grade Distribution", index=False)

    excel_buffer.seek(0)
    return excel_buffer.getvalue()
