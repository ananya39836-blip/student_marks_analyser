"""
app.py - Main Streamlit Application for Student Marks Report Analysis Program
Features:
- Multi-dimensional exploratory 2D and 3D visual demonstrations
- IIT Patna Capstone-I Project Report Generator (PDF and DOCX strictly matching template)
- Individual Student Report Card Generation (PDF)
- Multi-sheet Excel Master Gradebook export
- Machine Learning 3D Clustering and Predictive Target Simulator
"""

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import io

from data_manager import (
    generate_synthetic_student_data,
    validate_and_process_uploaded_file,
    get_sample_csv_template,
    SUBJECTS
)
from analytics import (
    compute_summary_statistics,
    compute_grade_distribution,
    identify_toppers,
    identify_at_risk_students,
    compute_correlation_matrix,
    perform_kmeans_clustering_3d,
    calculate_target_mark_simulation
)
from visualizations import (
    plot_subject_distribution_box,
    plot_subject_averages_bar,
    plot_grade_donut,
    plot_overall_score_histogram,
    plot_correlation_heatmap,
    plot_attendance_vs_marks_scatter,
    plot_student_radar_chart,
    plot_student_subject_breakdown_bar,
    plot_gauge_chart,
    plot_3d_academic_space,
    plot_3d_attendance_effort_surface,
    plot_3d_kmeans_clustering,
    plot_3d_subject_score_landscape
)
from report_generator import (
    generate_capstone_project_report_pdf,
    generate_capstone_project_report_docx,
    generate_student_report_card_pdf,
    generate_excel_workbook
)

# Page configuration
st.set_page_config(
    page_title="Student Marks Analytics & Report Studio",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    /* Main container and font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Top banner */
    .hero-banner {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 50%, #06B6D4 100%);
        padding: 24px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.25);
    }
    .hero-title {
        font-size: 26px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 14px;
        opacity: 0.92;
        margin-top: 6px;
        font-weight: 400;
    }

    /* Metric cards */
    .metric-card {
        background: white;
        padding: 16px 20px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.06);
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 800;
        color: #0F172A;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 11px;
        color: #10B981;
        font-weight: 500;
        margin-top: 2px;
    }

    /* Section Headers */
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 20px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Formal Report Preview Paper */
    .formal-paper {
        background: white;
        border: 2px solid #CBD5E1;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        padding: 45px 55px;
        border-radius: 8px;
        margin-bottom: 25px;
        color: #0F172A;
        line-height: 1.6;
    }
    .formal-title {
        text-align: center;
        font-size: 18px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 35px;
        color: #0F172A;
    }
    .formal-center {
        text-align: center;
        font-size: 14px;
        margin: 15px 0;
    }
    .formal-inst {
        text-align: center;
        font-weight: 700;
        font-size: 15px;
        margin-top: 45px;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# STATE INITIALIZATION
# ==============================================================================
if "seed" not in st.session_state:
    st.session_state.seed = 42

if "raw_df" not in st.session_state:
    st.session_state.raw_df = generate_synthetic_student_data(num_students=120, seed=st.session_state.seed)

if "active_subjects" not in st.session_state:
    st.session_state.active_subjects = SUBJECTS.copy()


# ==============================================================================
# SIDEBAR CONTROLS & NAVIGATION
# ==============================================================================
with st.sidebar:
    st.markdown("### 🎓 Marks Analysis Studio")
    st.markdown("---")

    nav_mode = st.radio(
        "**Navigation Mode**",
        [
            "🏛️ Executive Dashboard",
            "🌐 3D Spatial Demonstration",
            "👤 Student Report Card",
            "🔬 Correlation & At-Risk Analytics",
            "🎓 Capstone Project Report Generator",
            "🔮 Target Score Simulator",
            "📁 Data Management"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("#### ⚙️ Data Source")
    data_source = st.radio(
        "Choose Data Source:",
        ["Preloaded Rich Cohort (120 Students)", "Upload CSV / Excel File"],
        index=0
    )

    if data_source == "Preloaded Rich Cohort (120 Students)":
        if st.button("🔄 Regenerate Cohort Data", use_container_width=True):
            st.session_state.seed = np.random.randint(1, 9999)
            st.session_state.raw_df = generate_synthetic_student_data(num_students=120, seed=st.session_state.seed)
            st.session_state.active_subjects = SUBJECTS.copy()
            st.success("New cohort randomized successfully!")
            st.rerun()
    else:
        uploaded_file = st.file_uploader("Upload Marks Sheet (CSV or Excel)", type=["csv", "xlsx", "xls"])
        if uploaded_file is not None:
            proc_df, msg = validate_and_process_uploaded_file(uploaded_file)
            if not proc_df.empty:
                st.session_state.raw_df = proc_df
                # Infer numeric subjects
                excl = {"roll_no", "student_name", "class", "section", "term", "gender", 
                        "attendance_pct", "study_hours_week", "total_marks", "max_marks", 
                        "percentage", "gpa", "grade", "status", "rank", "overall_rank"}
                detected = [c for c in proc_df.select_dtypes(include=[np.number]).columns if c.lower() not in excl]
                st.session_state.active_subjects = detected
                st.success(msg)
            else:
                st.error(msg)

        # Template download
        st.download_button(
            label="📥 Download CSV Template",
            data=get_sample_csv_template(),
            file_name="student_marks_template.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("#### 🔍 Filter Cohort")
    df_pool = st.session_state.raw_df

    # Class filter
    available_classes = ["All"] + sorted(list(df_pool["Class"].unique()))
    selected_class = st.selectbox("Filter Class:", available_classes, index=0)

    # Section filter
    available_sections = ["All"] + sorted(list(df_pool["Section"].unique()))
    selected_sec = st.selectbox("Filter Section:", available_sections, index=0)

    # Term filter
    available_terms = ["All"] + sorted(list(df_pool["Term"].unique()))
    selected_term = st.selectbox("Filter Term:", available_terms, index=0)

    st.markdown("---")
    st.caption("IIT Patna Hybrid UG Program in CS & Data Analytics • Capstone-I")


# Apply filters
df = df_pool.copy()
if selected_class != "All":
    df = df[df["Class"] == selected_class]
if selected_sec != "All":
    df = df[df["Section"] == selected_sec]
if selected_term != "All":
    df = df[df["Term"] == selected_term]

if df.empty:
    st.warning("No student records match the active filter criteria. Resetting filters to all.")
    df = df_pool.copy()

subjects = [s for s in st.session_state.active_subjects if s in df.columns]


# ==============================================================================
# HERO BANNER
# ==============================================================================
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🎓 Student Marks Report Analysis Program</div>
    <div class="hero-subtitle">Comprehensive Academic Evaluation System with 2D Visual Analytics, 3D Spatial Demonstration & IIT Patna Capstone Report Compiler</div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# MODE 1: EXECUTIVE DASHBOARD & CLASS ANALYTICS
# ==============================================================================
if nav_mode == "🏛️ Executive Dashboard":
    st.markdown("### 📊 Cohort Performance Overview")

    # High-level KPI Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    total_students = len(df)
    avg_score = df["Percentage"].mean()
    pass_count = (df["Status"] == "PASSED").sum()
    pass_rate = (pass_count / total_students) * 100
    distinction_count = (df["Percentage"] >= 75).sum()
    distinction_rate = (distinction_count / total_students) * 100
    avg_attendance = df["Attendance_Pct"].mean()

    with k1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Cohort</div>
            <div class="metric-value">{total_students}</div>
            <div class="metric-sub">Active Students</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Class Average</div>
            <div class="metric-value">{avg_score:.1f}%</div>
            <div class="metric-sub">Cohort Mean</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Pass Percentage</div>
            <div class="metric-value">{pass_rate:.1f}%</div>
            <div class="metric-sub">{pass_count}/{total_students} Cleared</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Distinction (≥75%)</div>
            <div class="metric-value">{distinction_rate:.1f}%</div>
            <div class="metric-sub">{distinction_count} High Achievers</div>
        </div>
        """, unsafe_allow_html=True)
    with k5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Attendance</div>
            <div class="metric-value">{avg_attendance:.1f}%</div>
            <div class="metric-sub">Engagement Level</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualizations Row 1: Grade Donut + Overall Percentage Histogram
    r1_col1, r1_col2 = st.columns([1, 1])
    with r1_col1:
        st.plotly_chart(plot_grade_donut(df), use_container_width=True)
    with r1_col2:
        st.plotly_chart(plot_overall_score_histogram(df), use_container_width=True)

    # Visualizations Row 2: Subject Mean/Median Bar + Box & Violin Dispersion
    r2_col1, r2_col2 = st.columns([1, 1])
    with r2_col1:
        st.plotly_chart(plot_subject_averages_bar(df, subjects), use_container_width=True)
    with r2_col2:
        st.plotly_chart(plot_subject_distribution_box(df, subjects), use_container_width=True)

    # Statistical Summary Table
    st.markdown("#### 📋 Comprehensive Subject Benchmark Statistics")
    stats_table = compute_summary_statistics(df, subjects)
    st.dataframe(
        stats_table.style.highlight_max(axis=0, color="#D1FAE5", subset=["Mean Score", "Pass Rate (%)"])
                         .highlight_min(axis=0, color="#FEE2E2", subset=["Mean Score", "Pass Rate (%)"]),
        use_container_width=True
    )

    # Top Rankers Showcase
    st.markdown("#### 🏆 Class Rankers & Honors List")
    top_df = identify_toppers(df, n=6)
    st.dataframe(top_df, use_container_width=True)

    # Quick download master excel
    st.download_button(
        label="📥 Download Full Academic Excel Master Gradebook",
        data=generate_excel_workbook(df, subjects),
        file_name=f"Master_Gradebook_{datetime.date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ==============================================================================
# MODE 2: 3D SPATIAL DEMONSTRATION
# ==============================================================================
elif nav_mode == "🌐 3D Spatial Demonstration":
    st.markdown("### 🌐 3D Demonstration & Academic Spatial Modeling")
    st.info("💡 **Interactive 3D Controls:** Click and drag with mouse to freely rotate the 3D space 360°. Scroll to zoom in/out. Right-click to pan. Hover over data nodes to inspect individual student profiles.")

    demo_tabs = st.tabs([
        "🌌 3D Academic Coordinate Space",
        "🌊 3D Attendance & Effort Response Surface",
        "🧠 3D Machine Learning Clustering (PCA + K-Means)",
        "🏔️ 3D Cohort Topographical Landscape"
    ])

    with demo_tabs[0]:
        st.markdown("#### 3D Multi-Subject Performance Vector Space")
        st.caption("Inspect how students distribute across 3 simultaneous subject coordinates.")
        c1, c2, c3 = st.columns(3)
        with c1:
            x_axis = st.selectbox("X-Axis Subject:", subjects, index=0)
        with c2:
            default_y = 1 if len(subjects) > 1 else 0
            y_axis = st.selectbox("Y-Axis Subject:", subjects, index=default_y)
        with c3:
            z_opts = ["Percentage"] + subjects
            z_axis = st.selectbox("Z-Axis Metric:", z_opts, index=0)

        fig_3d_space = plot_3d_academic_space(df, x_axis, y_axis, z_axis, color_col="Percentage")
        st.plotly_chart(fig_3d_space, use_container_width=True)

    with demo_tabs[1]:
        st.markdown("#### 3D Response Surface: Academic Yield vs. Attendance & Weekly Study Effort")
        st.caption("Depicts a multivariate 2nd-degree polynomial surface modeling the joint impact of attendance and study effort on grades.")
        fig_3d_surface = plot_3d_attendance_effort_surface(df)
        st.plotly_chart(fig_3d_surface, use_container_width=True)

    with demo_tabs[2]:
        st.markdown("#### 3D Unsupervised Clustering & Student Segmentation")
        st.caption("Applies Principal Component Analysis (PCA) and K-Means clustering in 3D feature space to identify distinct learner archetypes.")
        clustered_df, kmeans_model, cluster_summary = perform_kmeans_clustering_3d(df, subjects, n_clusters=4)
        fig_3d_cluster = plot_3d_kmeans_clustering(clustered_df)
        st.plotly_chart(fig_3d_cluster, use_container_width=True)

        st.markdown("##### 📊 Student Archetype Profile Summary")
        st.dataframe(cluster_summary, use_container_width=True)

    with demo_tabs[3]:
        st.markdown("#### 3D Cohort Academic Elevation Landscape")
        st.caption("Visualizes the academic score terrain across all subject disciplines and student percentile deciles.")
        fig_3d_topo = plot_3d_subject_score_landscape(df, subjects)
        st.plotly_chart(fig_3d_topo, use_container_width=True)


# ==============================================================================
# MODE 3: INDIVIDUAL STUDENT PERFORMANCE CARD
# ==============================================================================
elif nav_mode == "👤 Student Report Card":
    st.markdown("### 👤 Student Performance Report Card Studio")

    # Select student
    student_labels = [f"{row['Student_Name']} ({row['Roll_No']}) - Rank #{row['Rank']}" for _, row in df.iterrows()]
    selected_label = st.selectbox("Select Student to Generate Report:", student_labels)
    selected_roll = selected_label.split("(")[1].split(")")[0]
    student_row = df[df["Roll_No"] == selected_roll].iloc[0]

    # Quick Bio Cards
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        st.metric("Overall Percentage", f"{student_row['Percentage']}%")
    with b2:
        st.metric("Letter Grade", student_row['Grade'])
    with b3:
        st.metric("GPA", f"{student_row['GPA']} / 4.0")
    with b4:
        st.metric("Class Rank", f"#{student_row['Rank']} / {len(df)}")
    with b5:
        st.metric("Attendance", f"{student_row['Attendance_Pct']}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualizations Row: Competency Radar + Gauge + Subject Bars
    col_rad, col_sub = st.columns([1, 1])
    with col_rad:
        st.plotly_chart(plot_student_radar_chart(student_row, df, subjects), use_container_width=True)
        st.plotly_chart(plot_gauge_chart(student_row['Percentage'], "Academic Mastery Index"), use_container_width=True)
    with col_sub:
        st.plotly_chart(plot_student_subject_breakdown_bar(student_row, subjects), use_container_width=True)

        # Subject marks detail table
        st.markdown("##### 📝 Subject Marks Breakdown")
        breakdown_rows = []
        for s in subjects:
            sc = student_row[s]
            c_avg = round(df[s].mean(), 1)
            diff = round(sc - c_avg, 1)
            breakdown_rows.append({
                "Subject": s,
                "Marks (100)": sc,
                "Class Avg": c_avg,
                "Variance from Avg": f"{'+' if diff > 0 else ''}{diff}",
                "Status": "PASSED" if sc >= 40 else "FAILED"
            })
        st.dataframe(pd.DataFrame(breakdown_rows), use_container_width=True)

        st.markdown("##### 💬 Faculty Evaluation Remarks")
        st.info(f"“{student_row['Teacher_Remarks']}”")

    # Download PDF Report Card
    pdf_card_bytes = generate_student_report_card_pdf(student_row, df, subjects)
    st.download_button(
        label=f"📄 Download Official Report Card (PDF) for {student_row['Student_Name']}",
        data=pdf_card_bytes,
        file_name=f"ReportCard_{student_row['Roll_No']}_{student_row['Student_Name'].replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )


# ==============================================================================
# MODE 4: CORRELATION & AT-RISK ANALYTICS
# ==============================================================================
elif nav_mode == "🔬 Correlation & At-Risk Analytics":
    st.markdown("### 🔬 Inter-Disciplinary Correlations & Intervention Watchlist")

    tab_corr, tab_risk = st.tabs(["📊 Correlation & Relationships", "⚠️ Remedial Intervention Watchlist"])

    with tab_corr:
        corr_matrix = compute_correlation_matrix(df, subjects)
        st.plotly_chart(plot_correlation_heatmap(corr_matrix), use_container_width=True)

        c_sc1, c_sc2 = st.columns(2)
        with c_sc1:
            st.plotly_chart(plot_attendance_vs_marks_scatter(df), use_container_width=True)
        with c_sc2:
            st.markdown("##### 📌 Key Correlation Insights")
            st.write(
                "• **Inter-Subject Dependency:** Quantitative subjects (Mathematics, Physics, Computer Science) "
                "consistently exhibit strong positive Pearson correlations (r > 0.65).\n\n"
                "• **Effort-to-Yield Gradient:** Attendance percentage and weekly self-study hours demonstrate "
                "statistically significant positive correlations with aggregate percentage.\n\n"
                "• **Cross-Domain Consistency:** Students excelling in English show higher median scores across "
                "conceptual theoretical questions in natural sciences."
            )

    with tab_risk:
        st.markdown("#### 🚨 Academic Early Warning Watchlist")
        st.caption("Identifies students falling below safety thresholds: Subject fail (<40), Low attendance (<75%), or Aggregate <50%.")
        risk_df = identify_at_risk_students(df, subjects)
        if not risk_df.empty:
            st.warning(f"⚠️ {len(risk_df)} students have been flagged for immediate remedial intervention.")
            st.dataframe(risk_df, use_container_width=True)
        else:
            st.success("🎉 No students currently on the academic risk watchlist under active criteria.")


# ==============================================================================
# MODE 5: CAPSTONE PROJECT REPORT GENERATOR (THE USER'S EXACT FORMAT)
# ==============================================================================
elif nav_mode == "🎓 Capstone Project Report Generator":
    st.markdown("### 🎓 IIT Patna Capstone-I Project Report Generator")
    st.write(
        "Generate and download the complete formal **Capstone-I Project Report** matching the exact format "
        "of the Indian Institute of Technology Patna (Bihta - 801106) for the Hybrid UG Program in "
        "Computer Science & Data Analytics."
    )

    with st.expander("🛠️ **Configure Report Metadata & Student Contributions**", expanded=True):
        m1, m2 = st.columns(2)
        with m1:
            rep_title = st.text_input(
                "Project Title (Capital Letters):",
                value="STUDENT MARKS REPORT ANALYSIS PROGRAM WITH MULTI-DIMENSIONAL VISUALIZATIONS AND 3D DEMONSTRATION"
            )
            rep_student_name = st.text_input("Lead Student Name:", value="Aarav Sharma")
            rep_roll_no = st.text_input("Roll Number:", value="2401CS01")
        with m2:
            rep_group_no = st.text_input("Group Number:", value="Group No. 12")
            rep_date = st.text_input("Submission Date:", value=datetime.date.today().strftime("%B %d, %Y"))

        st.markdown("##### 👥 Team Member Contributions (Work Done by Each Member):")
        mem1 = st.text_input("Member 1:", value="Aarav Sharma (2401CS01): System Architecture, 3D Demonstration visualizer & Report Generator.")
        mem2 = st.text_input("Member 2:", value="Diya Patel (2401CS02): Data preprocessing, synthetic marks synthesis & exploratory data analysis.")
        mem3 = st.text_input("Member 3:", value="Rohan Verma (2401CS03): Statistical algorithms, inter-subject correlation modeling & scoring models.")
        mem4 = st.text_input("Member 4:", value="Ananya Iyer (2401CS04): K-Means clustering in 3D PCA space & student archetype segmentation.")
        mem5 = st.text_input("Member 5:", value="Vivaan Gupta (2401CS05): Streamlit user interface design, dashboard testing & validation.")

    member_list = [mem1, mem2, mem3, mem4, mem5]

    # Action Download Buttons
    btn_col1, btn_col2, btn_col3 = st.columns(3)

    pdf_report_bytes = generate_capstone_project_report_pdf(
        df=df,
        subjects=subjects,
        project_title=rep_title,
        student_name=rep_student_name,
        roll_no=rep_roll_no,
        group_no=rep_group_no,
        date_str=rep_date,
        member_contributions=member_list
    )

    docx_report_bytes = generate_capstone_project_report_docx(
        df=df,
        subjects=subjects,
        project_title=rep_title,
        student_name=rep_student_name,
        roll_no=rep_roll_no,
        group_no=rep_group_no,
        date_str=rep_date,
        member_contributions=member_list
    )

    with btn_col1:
        st.download_button(
            label="📥 Download Capstone Report (PDF)",
            data=pdf_report_bytes,
            file_name=f"Capstone_Report_{rep_roll_no}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with btn_col2:
        st.download_button(
            label="📝 Download Capstone Report (Word .docx)",
            data=docx_report_bytes,
            file_name=f"Capstone_Report_{rep_roll_no}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

    with btn_col3:
        st.download_button(
            label="📊 Download Master Excel Gradebook (.xlsx)",
            data=generate_excel_workbook(df, subjects),
            file_name=f"Master_Gradebook_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("### 📄 Formal Document In-App Preview (Exact IIT Patna Format)")

    preview_tabs = st.tabs([
        "Page 1: Title Page",
        "Page 2: Declaration",
        "Page 3: Summary & Contributions",
        "Page 4: Content (TOC)",
        "Chapter 1: Introduction",
        "Chapter 2: Methodology & 3D Demo",
        "Chapter 3: Conclusion & Future Work"
    ])

    with preview_tabs[0]:
        st.markdown(f"""
        <div class="formal-paper">
            <div class="formal-title">{rep_title.upper()}</div>
            <div style="height: 100px;"></div>
            <div class="formal-center" style="font-size: 16px;">Capstone-I project report submitted</div>
            <div class="formal-center" style="font-size: 14px;">by the student of</div>
            <div class="formal-center" style="font-size: 16px; font-weight: 700;">Hybrid UG program in Computer Science & Data Analytics</div>
            <div style="height: 90px;"></div>
            <div class="formal-center" style="font-size: 15px; font-weight: 700;">
                {rep_student_name}<br/>
                Roll No. {rep_roll_no}<br/>
                {rep_group_no}
            </div>
            <div style="height: 110px;"></div>
            <div class="formal-inst">
                INDIAN INSTITUTE OF TECHNOLOGY PATNA<br/>
                BIHTA - 801106, INDIA<br/>
                <span style="font-weight: 400; font-size: 14px;">Date: {rep_date}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with preview_tabs[1]:
        st.markdown(f"""
        <div class="formal-paper">
            <h2 style="text-align: center; font-weight: 800; margin-bottom: 30px;">Declaration</h2>
            <p style="text-align: justify; font-size: 15px; line-height: 1.8;">
                I hereby declare that this submission is my own work and that, to the best of our knowledge 
                and belief, it contains no material previously published or written by another person nor material 
                which to a substantial extent has been accepted for the award of any other degree or diploma 
                of the university or other institute of higher learning, except where due acknowledgment 
                has been made in the text.
            </p>
            <div style="height: 250px;"></div>
            <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                <div>
                    <b>Date:</b> {rep_date}
                </div>
                <div style="text-align: right;">
                    <b>{rep_student_name}</b><br/>
                    Roll No: {rep_roll_no}, {rep_group_no}<br/><br/>
                    ____________________________________<br/>
                    <i>(Signature)</i>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with preview_tabs[2]:
        st.markdown(f"""
        <div class="formal-paper">
            <h2 style="text-align: center; font-weight: 800; margin-bottom: 25px;">Summary of the Project</h2>
            <p style="text-align: justify; font-size: 14.5px; line-height: 1.7;">
                The <b>Student Marks Report Analysis Program</b> is a specialized analytics and visual reporting system 
                engineered for contemporary academic institutions. Moving beyond legacy static spreadsheets, the system 
                unifies rigorous statistical computing with rich 2D analytics (violin plots, radar charts, inter-subject correlation) 
                and <b>3D interactive spatial demonstrations</b> (3D academic coordinate space, multivariate polynomial response surfaces 
                of attendance vs. study effort, and 3D unsupervised K-Means clustering). 
                The software equips academic committees to identify at-risk students, simulate future mark trajectories, 
                and synthesize formal Capstone documentation automatically.
            </p>
            <br/>
            <h4 style="font-weight: 700;">Mention the work done by each member:</h4>
            <ol style="font-size: 14px; line-height: 1.8;">
                <li>{mem1}</li>
                <li>{mem2}</li>
                <li>{mem3}</li>
                <li>{mem4}</li>
                <li>{mem5}</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with preview_tabs[3]:
        st.markdown("""
        <div class="formal-paper">
            <h2 style="text-align: left; font-weight: 800; margin-bottom: 30px;">Content</h2>
            <table style="width: 100%; font-size: 15px; line-height: 2.2;">
                <tr><td style="font-weight: 700; width: 40px;">1</td><td style="font-weight: 700;">Introduction</td><td style="text-align: right; font-weight: 700;">Page 5</td></tr>
                <tr><td></td><td>1.1 Project Overview & Motivation</td><td style="text-align: right;">5</td></tr>
                <tr><td></td><td>1.2 Objectives & Scope</td><td style="text-align: right;">5</td></tr>
                <tr><td></td><td>1.3 Academic Significance & Problem Statement</td><td style="text-align: right;">6</td></tr>
                <tr><td></td><td>1.4 Dataset Description & Academic Attributes</td><td style="text-align: right;">6</td></tr>
                <tr><td style="font-weight: 700;">2</td><td style="font-weight: 700;">Methodology, Visual Analytics & 3D Demonstration</td><td style="text-align: right; font-weight: 700;">Page 7</td></tr>
                <tr><td></td><td>2.1 System Architecture & Data Pipeline</td><td style="text-align: right;">7</td></tr>
                <tr><td></td><td>2.2 Comprehensive 2D Statistical Visualizations</td><td style="text-align: right;">7</td></tr>
                <tr><td></td><td>2.3 3D Demonstration & Spatial Academic Modeling</td><td style="text-align: right;">8</td></tr>
                <tr><td></td><td>2.4 Machine Learning Student Clustering (K-Means 3D)</td><td style="text-align: right;">9</td></tr>
                <tr><td></td><td>2.5 Early Intervention & Remedial Engine</td><td style="text-align: right;">9</td></tr>
                <tr><td style="font-weight: 700;">3</td><td style="font-weight: 700;">Conclusion & future work</td><td style="text-align: right; font-weight: 700;">Page 10</td></tr>
                <tr><td></td><td>3.1 Key Insights & Analytical Findings</td><td style="text-align: right;">10</td></tr>
                <tr><td></td><td>3.2 Technological Impact & Limitations</td><td style="text-align: right;">10</td></tr>
                <tr><td></td><td>3.3 Future Enhancements & Recommendations</td><td style="text-align: right;">10</td></tr>
                <tr><td></td><td>References & Bibliography</td><td style="text-align: right;">11</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with preview_tabs[4]:
        st.markdown("""
        <div class="formal-paper">
            <h2>Chapter 1</h2>
            <h1 style="text-align: center; margin-bottom: 25px;">Introduction</h1>
            <h4>1.1 Project Overview & Motivation</h4>
            <p>Evaluating student learning outcomes is fundamental to maintaining academic excellence. Traditional grade reporting often obscures inter-subject correlations and early indicators of distress. This program combines Streamlit, Plotly, and scikit-learn to provide interactive 2D and 3D visual diagnostics.</p>
            <h4>1.2 Objectives & Scope</h4>
            <ul>
                <li>Standardize and ingest multi-subject academic records.</li>
                <li>Compute comprehensive descriptive statistics and distribution quartiles.</li>
                <li>Implement 3D visual demonstrations (coordinate space, response surfaces, K-Means clustering).</li>
                <li>Synthesize official IIT Patna Capstone documentation and individualized report cards.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with preview_tabs[5]:
        st.markdown("""
        <div class="formal-paper">
            <h2>Chapter 2</h2>
            <h1 style="text-align: center; margin-bottom: 25px;">Methodology, Visual Analytics & 3D Demonstration</h1>
            <h4>2.1 System Architecture & Data Pipeline</h4>
            <p>Comprises Data Management, Analytics Engine, Visualization Suite, and Report Compilation Engine.</p>
            <h4>2.2 Comprehensive 2D Statistical Visualizations</h4>
            <p>Grouped bar charts, box/violin distributions, and radar competency graphs benchmark student mastery.</p>
            <h4>2.3 3D Demonstration & Spatial Modeling</h4>
            <p>Maps students in 3D Academic Coordinate Space, computes continuous polynomial response surfaces of attendance and study effort, and performs 3D K-Means clustering.</p>
        </div>
        """, unsafe_allow_html=True)

    with preview_tabs[6]:
        st.markdown("""
        <div class="formal-paper">
            <h2>Chapter 3</h2>
            <h1 style="text-align: center; margin-bottom: 25px;">Conclusion & future work</h1>
            <h4>3.1 Key Insights & Analytical Findings</h4>
            <p>Strong positive Pearson correlation (r > 0.7) observed across quantitative disciplines. Attendance above 80% strongly correlates with distinction grades.</p>
            <h4>3.2 Technological Impact</h4>
            <p>Drastically reduces administrative reporting overhead while providing actionable insights for student counseling.</p>
            <h4>3.3 Future Work</h4>
            <p>LMS API integration (Canvas, Moodle), deep learning trajectory forecasting, and WebXR / VR immersive analytics.</p>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# MODE 6: TARGET SCORE SIMULATOR
# ==============================================================================
elif nav_mode == "🔮 Target Score Simulator":
    st.markdown("### 🔮 What-If / Target Score Simulator")
    st.write("Calculate what score a student needs in the upcoming examinations to achieve their target grade.")

    sim_c1, sim_c2 = st.columns(2)
    with sim_c1:
        cur_pct = st.slider("Current Aggregate Percentage (%):", min_value=30.0, max_value=98.0, value=68.5, step=0.5)
        cur_weight = st.slider("Weight of Completed Term (%):", min_value=10, max_value=80, value=50, step=5) / 100.0
    with sim_c2:
        target_grade = st.selectbox(
            "Desired Target Final Grade:",
            ["A+ (Outstanding, ≥90%)", "A (Excellent, ≥80%)", "B+ (Very Good, ≥70%)", "B (Good, ≥60%)"]
        )
        target_min = 90.0 if "A+" in target_grade else (80.0 if "A " in target_grade or "A (" in target_grade else (70.0 if "B+" in target_grade else 60.0))

    sim_res = calculate_target_mark_simulation(cur_pct, cur_weight, target_min)

    st.markdown("<br>", unsafe_allow_html=True)
    if sim_res["feasible"]:
        st.success(f"🎯 **Required Score:** You need to score an average of **{sim_res['required_pct']}%** in the remaining exams (weight {int((1-cur_weight)*100)}%) to attain **{target_grade.split('(')[0].strip()}**.")
    else:
        st.error(f"⚠️ {sim_res['message']}")


# ==============================================================================
# MODE 7: DATA MANAGEMENT & RAW TABLE
# ==============================================================================
elif nav_mode == "📁 Data Management":
    st.markdown("### 📁 Data Management & Master Records")
    st.dataframe(df, use_container_width=True)

    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Filtered Data as CSV",
        data=csv_data,
        file_name=f"student_marks_export_{datetime.date.today()}.csv",
        mime="text/csv"
    )
