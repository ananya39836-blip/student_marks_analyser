"""
visualizations.py - High-fidelity 2D and 3D data visualization suite using Plotly
for Student Marks Report Analysis Program.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Optional

# Color palettes
GRADE_COLORS = {
    "A+": "#10B981",  # Emerald
    "A": "#34D399",   # Mint
    "B+": "#3B82F6",  # Blue
    "B": "#60A5FA",   # Light Blue
    "C": "#F59E0B",   # Amber
    "D": "#F97316",   # Orange
    "F": "#EF4444"    # Red
}

THEME_LAYOUT = dict(
    font=dict(family="Inter, system-ui, sans-serif"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=40, t=50, b=40),
)


# ==============================================================================
# 2D VISUALIZATIONS
# ==============================================================================

def plot_subject_distribution_box(df: pd.DataFrame, subjects: List[str]) -> go.Figure:
    """Create interactive box and violin plots showing subject score distributions."""
    valid_subjects = [s for s in subjects if s in df.columns]
    melted = df.melt(id_vars=["Student_Name", "Roll_No"], value_vars=valid_subjects,
                     var_name="Subject", value_name="Score")
    
    fig = px.box(
        melted,
        x="Subject",
        y="Score",
        color="Subject",
        points="all",
        hover_data=["Student_Name", "Roll_No"],
        title="<b>Subject Score Distributions & Dispersion</b> (Quartiles, Median, Outliers)"
    )
    
    fig.add_hline(y=40, line_dash="dash", line_color="#EF4444", annotation_text="Passing Threshold (40)")
    fig.add_hline(y=75, line_dash="dot", line_color="#10B981", annotation_text="Distinction (75)")
    fig.update_layout(
        **THEME_LAYOUT,
        showlegend=False,
        yaxis=dict(range=[0, 105], title="Score (out of 100)", gridcolor="#E2E8F0"),
        xaxis=dict(title="", gridcolor="#E2E8F0")
    )
    return fig


def plot_subject_averages_bar(df: pd.DataFrame, subjects: List[str]) -> go.Figure:
    """Create grouped bar chart comparing subject mean and median scores."""
    valid_subjects = [s for s in subjects if s in df.columns]
    means = [round(df[s].mean(), 1) for s in valid_subjects]
    medians = [round(df[s].median(), 1) for s in valid_subjects]
    stds = [round(df[s].std(), 1) for s in valid_subjects]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=valid_subjects,
        y=means,
        name="Mean Score",
        marker_color="#4F46E5",
        text=means,
        textposition="outside",
        error_y=dict(type="data", array=stds, visible=True)
    ))
    fig.add_trace(go.Bar(
        x=valid_subjects,
        y=medians,
        name="Median Score",
        marker_color="#06B6D4",
        text=medians,
        textposition="outside"
    ))

    fig.add_hline(y=40, line_dash="dash", line_color="#EF4444", annotation_text="Pass Benchmark (40)")
    fig.update_layout(
        **THEME_LAYOUT,
        barmode="group",
        title="<b>Subject Performance Benchmarks: Mean vs. Median</b>",
        yaxis=dict(range=[0, 110], title="Score", gridcolor="#E2E8F0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_grade_donut(df: pd.DataFrame) -> go.Figure:
    """Create sleek donut chart of student grade distributions."""
    order = ["A+", "A", "B+", "B", "C", "D", "F"]
    counts = df["Grade"].value_counts().reindex(order, fill_value=0)
    
    colors = [GRADE_COLORS.get(g, "#64748B") for g in counts.index]
    
    fig = go.Figure(data=[go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="label+percent",
        hoverinfo="label+value+percent",
        sort=False
    )])
    
    fig.update_layout(
        **THEME_LAYOUT,
        title="<b>Overall Grade Distribution</b>",
        annotations=[dict(text=f"Total<br><b>{len(df)}</b>", x=0.5, y=0.5, font_size=18, showarrow=False)],
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    return fig


def plot_overall_score_histogram(df: pd.DataFrame) -> go.Figure:
    """Histogram of overall percentage with normal distribution indicator."""
    fig = px.histogram(
        df,
        x="Percentage",
        nbins=20,
        color="Status",
        color_discrete_map={"PASSED": "#4F46E5", "FAILED": "#EF4444"},
        marginal="rug",
        hover_data=["Student_Name", "Roll_No", "Grade"],
        title="<b>Cohort Percentage Distribution with Pass/Fail Breakdown</b>"
    )
    
    mean_val = df["Percentage"].mean()
    median_val = df["Percentage"].median()
    fig.add_vline(x=mean_val, line_dash="dash", line_color="#10B981", annotation_text=f"Mean ({mean_val:.1f}%)")
    fig.add_vline(x=median_val, line_dash="dot", line_color="#F59E0B", annotation_text=f"Median ({median_val:.1f}%)")
    
    fig.update_layout(
        **THEME_LAYOUT,
        xaxis=dict(range=[0, 100], title="Percentage (%)", gridcolor="#E2E8F0"),
        yaxis=dict(title="Student Frequency", gridcolor="#E2E8F0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_correlation_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    """Correlation heatmap showing interdependence of academic subjects and engagement."""
    fig = px.imshow(
        corr_matrix,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="Purples",
        title="<b>Academic Inter-Subject Correlation Matrix</b> (Pearson's r)"
    )
    fig.update_layout(
        **THEME_LAYOUT,
        xaxis=dict(tickangle=-45),
        coloraxis_colorbar=dict(title="Correlation")
    )
    return fig


def plot_attendance_vs_marks_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter plot exploring relationship between Attendance % and Final Percentage."""
    fig = px.scatter(
        df,
        x="Attendance_Pct",
        y="Percentage",
        color="Grade",
        size="Study_Hours_Week",
        hover_name="Student_Name",
        hover_data=["Roll_No", "Class", "Section", "Status"],
        trendline="ols",
        color_discrete_map=GRADE_COLORS,
        title="<b>Attendance vs. Academic Percentage</b> (Bubble Size = Study Hours/Week)"
    )
    
    fig.add_hline(y=40, line_dash="dash", line_color="#EF4444", annotation_text="Pass Cutoff (40%)")
    fig.add_vline(x=75, line_dash="dash", line_color="#F59E0B", annotation_text="Min Required Attendance (75%)")
    
    fig.update_layout(
        **THEME_LAYOUT,
        xaxis=dict(title="Attendance (%)", gridcolor="#E2E8F0"),
        yaxis=dict(title="Academic Percentage (%)", gridcolor="#E2E8F0")
    )
    return fig


def plot_student_radar_chart(student_row: pd.Series, df_class: pd.DataFrame, subjects: List[str]) -> go.Figure:
    """Radar (Spider) chart comparing individual student with class average and class topper."""
    valid_subjects = [s for s in subjects if s in student_row]
    student_scores = [student_row[s] for s in valid_subjects]
    class_averages = [df_class[s].mean() for s in valid_subjects]
    class_maxima = [df_class[s].max() for s in valid_subjects]

    # Close the radar loop
    radar_subjects = valid_subjects + [valid_subjects[0]]
    student_scores += [student_scores[0]]
    class_averages += [class_averages[0]]
    class_maxima += [class_maxima[0]]

    fig = go.Figure()
    
    # Class Maximum benchmark
    fig.add_trace(go.Scatterpolar(
        r=class_maxima,
        theta=radar_subjects,
        name="Cohort Benchmark (Max)",
        line=dict(color="#94A3B8", dash="dash"),
        fill="none"
    ))
    
    # Class Average benchmark
    fig.add_trace(go.Scatterpolar(
        r=class_averages,
        theta=radar_subjects,
        name="Class Average",
        fill="toself",
        fillcolor="rgba(14, 165, 233, 0.15)",
        line=dict(color="#0EA5E9")
    ))

    # Student's actual marks
    fig.add_trace(go.Scatterpolar(
        r=student_scores,
        theta=radar_subjects,
        name=f"{student_row['Student_Name']} (Actual)",
        fill="toself",
        fillcolor="rgba(79, 70, 229, 0.35)",
        line=dict(color="#4F46E5", width=2.5)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#CBD5E1"),
            angularaxis=dict(gridcolor="#CBD5E1")
        ),
        title=f"<b>Competency Radar: {student_row['Student_Name']} vs. Class Benchmark</b>",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        **THEME_LAYOUT
    )
    return fig


def plot_student_subject_breakdown_bar(student_row: pd.Series, subjects: List[str]) -> go.Figure:
    """Individual horizontal bar chart of subject scores with threshold color coding."""
    valid_subjects = [s for s in subjects if s in student_row]
    scores = [student_row[s] for s in valid_subjects]
    
    colors = []
    for sc in scores:
        if sc >= 75:
            colors.append("#10B981")  # Green
        elif sc >= 60:
            colors.append("#3B82F6")  # Blue
        elif sc >= 40:
            colors.append("#F59E0B")  # Amber
        else:
            colors.append("#EF4444")  # Red

    fig = go.Figure(go.Bar(
        x=scores,
        y=valid_subjects,
        orientation="h",
        marker_color=colors,
        text=[f"{s}/100" for s in scores],
        textposition="inside"
    ))

    fig.add_vline(x=40, line_dash="dash", line_color="#EF4444", annotation_text="Pass Cutoff (40)")
    fig.add_vline(x=75, line_dash="dot", line_color="#10B981", annotation_text="Distinction (75)")
    
    fig.update_layout(
        **THEME_LAYOUT,
        title=f"<b>Subject Marks Breakdown - {student_row['Student_Name']}</b>",
        xaxis=dict(range=[0, 105], title="Marks Obtained", gridcolor="#E2E8F0"),
        yaxis=dict(title="", autorange="reversed")
    )
    return fig


def plot_gauge_chart(percentage: float, title: str = "Overall Score") -> go.Figure:
    """Speedometer / Gauge chart showing student academic standing."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{title}</b>", 'font': {'size': 20}},
        delta={'reference': 75, 'increasing': {'color': "#10B981"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': "#4F46E5", 'thickness': 0.28},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#CBD5E1",
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.25)'},
                {'range': [40, 60], 'color': 'rgba(245, 158, 11, 0.25)'},
                {'range': [60, 75], 'color': 'rgba(59, 130, 246, 0.25)'},
                {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.25)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 3},
                'thickness': 0.75,
                'value': 40
            }
        }
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=35, b=20))
    return fig


# ==============================================================================
# 3D DEMONSTRATION VISUALIZATIONS
# ==============================================================================

def plot_3d_academic_space(df: pd.DataFrame, x_axis: str, y_axis: str, z_axis: str, color_col: str = "Percentage") -> go.Figure:
    """
    Interactive 3D Academic Space:
    Plots students in a 3-dimensional academic coordinate space (e.g. Math vs Physics vs CS or Total).
    Allows full 360-degree rotation, zooming, camera elevation, and hover inspection.
    """
    fig = px.scatter_3d(
        df,
        x=x_axis,
        y=y_axis,
        z=z_axis,
        color=color_col,
        size="Study_Hours_Week" if "Study_Hours_Week" in df.columns else None,
        color_continuous_scale="Viridis",
        hover_name="Student_Name",
        hover_data=["Roll_No", "Class", "Section", "Grade", "Percentage", "Attendance_Pct"],
        title=f"<b>3D Academic Coordinate Space</b> ({x_axis} × {y_axis} × {z_axis})"
    )

    fig.update_traces(
        marker=dict(size=7, opacity=0.88, line=dict(width=0.8, color="#FFFFFF"))
    )

    fig.update_layout(
        scene=dict(
            xaxis=dict(title=f"<b>{x_axis}</b>", backgroundcolor="rgb(245, 247, 250)", gridcolor="#CBD5E1"),
            yaxis=dict(title=f"<b>{y_axis}</b>", backgroundcolor="rgb(240, 244, 248)", gridcolor="#CBD5E1"),
            zaxis=dict(title=f"<b>{z_axis}</b>", backgroundcolor="rgb(235, 240, 245)", gridcolor="#CBD5E1"),
            camera=dict(
                eye=dict(x=1.65, y=1.65, z=1.2)
            )
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=620
    )
    return fig


def plot_3d_attendance_effort_surface(df: pd.DataFrame) -> go.Figure:
    """
    3D Response Surface Demonstration:
    Models the joint impact of Attendance (%) and Study Hours on Academic Percentage.
    Includes both the continuous fitted 3D trend surface mesh and actual student scatter points.
    """
    att = df["Attendance_Pct"].values
    hours = df["Study_Hours_Week"].values
    marks = df["Percentage"].values

    # Fit a 2nd-degree polynomial regression surface for realistic smooth curvature
    # Z = c0 + c1*X + c2*Y + c3*X^2 + c4*Y^2 + c5*X*Y
    A = np.c_[np.ones_like(att), att, hours, att**2, hours**2, att * hours]
    coeffs, _, _, _ = np.linalg.lstsq(A, marks, rcond=None)

    # Create grid mesh
    x_grid = np.linspace(att.min(), att.max(), 35)
    y_grid = np.linspace(hours.min(), hours.max(), 35)
    X_mesh, Y_mesh = np.meshgrid(x_grid, y_grid)

    Z_mesh = (coeffs[0] +
              coeffs[1] * X_mesh +
              coeffs[2] * Y_mesh +
              coeffs[3] * (X_mesh**2) +
              coeffs[4] * (Y_mesh**2) +
              coeffs[5] * (X_mesh * Y_mesh))
    Z_mesh = np.clip(Z_mesh, 0, 100)

    fig = go.Figure()

    # 3D Surface
    fig.add_trace(go.Surface(
        x=X_mesh,
        y=Y_mesh,
        z=Z_mesh,
        colorscale="Spectral_r",
        opacity=0.72,
        colorbar=dict(title="Fitted %", x=1.02),
        name="3D Response Surface"
    ))

    # 3D Student Scatter points on top of surface
    fig.add_trace(go.Scatter3d(
        x=att,
        y=hours,
        z=marks,
        mode="markers",
        marker=dict(
            size=5,
            color=marks,
            colorscale="Plasma",
            opacity=0.95,
            line=dict(color="#FFFFFF", width=0.5)
        ),
        text=[f"<b>{name}</b><br>Attendance: {a}%<br>Study: {h} hrs/wk<br>Mark: {m}%"
              for name, a, h, m in zip(df["Student_Name"], att, hours, marks)],
        hoverinfo="text",
        name="Actual Students"
    ))

    fig.update_layout(
        title="<b>3D Response Surface: Academic Yield vs. Attendance & Weekly Study Effort</b>",
        scene=dict(
            xaxis=dict(title="Attendance (%)", backgroundcolor="rgb(248, 250, 252)", gridcolor="#CBD5E1"),
            yaxis=dict(title="Study Hours / Week", backgroundcolor="rgb(241, 245, 249)", gridcolor="#CBD5E1"),
            zaxis=dict(title="Total Percentage (%)", backgroundcolor="rgb(238, 242, 246)", gridcolor="#CBD5E1", range=[0, 100]),
            camera=dict(eye=dict(x=1.8, y=-1.5, z=1.1))
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=620
    )
    return fig


def plot_3d_kmeans_clustering(clustered_df: pd.DataFrame) -> go.Figure:
    """
    3D Machine Learning Cluster Demonstration:
    Visualizes student learning archetypes identified by K-Means algorithm in 3D PCA Space.
    """
    fig = px.scatter_3d(
        clustered_df,
        x="PC1",
        y="PC2",
        z="PC3",
        color="Archetype",
        hover_name="Student_Name",
        hover_data=["Roll_No", "Class", "Percentage", "Attendance_Pct", "Grade"],
        title="<b>3D Unsupervised Clustering & Student Segmentation (K-Means + PCA)</b>",
        color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#EF4444"]
    )

    # Add Cluster Centroids
    centroids = clustered_df.groupby("Archetype")[["PC1", "PC2", "PC3"]].mean().reset_index()
    fig.add_trace(go.Scatter3d(
        x=centroids["PC1"],
        y=centroids["PC2"],
        z=centroids["PC3"],
        mode="markers+text",
        marker=dict(size=12, symbol="diamond", color="#1E293B", line=dict(color="#FFFFFF", width=2)),
        text=centroids["Archetype"].apply(lambda s: s.split("(")[0].strip()),
        textposition="top center",
        name="Cluster Centroids"
    ))

    fig.update_traces(
        selector=dict(mode="markers"),
        marker=dict(size=7, opacity=0.85)
    )

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Principal Component 1 (Overall Mastery)", backgroundcolor="#F8FAFC", gridcolor="#CBD5E1"),
            yaxis=dict(title="Principal Component 2 (Disciplinary Bias)", backgroundcolor="#F1F5F9", gridcolor="#CBD5E1"),
            zaxis=dict(title="Principal Component 3 (Engagement/Effort)", backgroundcolor="#EEF2F6", gridcolor="#CBD5E1"),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=620,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    return fig


def plot_3d_subject_score_landscape(df: pd.DataFrame, subjects: List[str]) -> go.Figure:
    """
    3D Topographical Score Terrain:
    Creates a 3D elevation map where X represents subjects, Y represents sorted student percentiles,
    and Z represents the score elevation, visualizing academic stratification.
    """
    valid_subjects = [s for s in subjects if s in df.columns]
    sorted_df = df.sort_values(by="Total_Marks", ascending=True).reset_index(drop=True)
    
    # Downsample or interpolate to 25 rank bins for smooth landscape
    num_bins = min(25, len(sorted_df))
    sorted_df["Rank_Bin"] = pd.qcut(sorted_df.index, q=num_bins, labels=False)
    
    terrain_data = sorted_df.groupby("Rank_Bin")[valid_subjects].mean().values

    fig = go.Figure(data=[go.Surface(
        z=terrain_data,
        x=valid_subjects,
        y=[f"P{int((i+1)*(100/num_bins))}" for i in range(num_bins)],
        colorscale="Turbo",
        colorbar=dict(title="Score")
    )])

    fig.update_layout(
        title="<b>3D Cohort Academic Elevation Landscape (Subjects × Student Deciles)</b>",
        scene=dict(
            xaxis=dict(title="Subject Discipline", backgroundcolor="#F8FAFC", gridcolor="#CBD5E1"),
            yaxis=dict(title="Student Percentile Tier", backgroundcolor="#F1F5F9", gridcolor="#CBD5E1"),
            zaxis=dict(title="Average Score", range=[0, 100], backgroundcolor="#EEF2F6", gridcolor="#CBD5E1"),
            camera=dict(eye=dict(x=-1.6, y=-1.6, z=1.2))
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=620
    )
    return fig
