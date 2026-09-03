import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st

# Set Streamlit Page Config
st.set_page_config(
    page_title="Materials Thermodynamics | Cp(T) Explorer",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Thermal Colors
COLD = "#4CC9F0"
MID = "#7209B7"
WARM = "#F72585"
HOT = "#FF70A6"
AMBER = "#FFB703"

# Load Dataset with Fallback & Cleaning
@st.cache_data
def load_thermo_data():
    filepaths = ["cp_values.csv", "data.csv"]
    df = None
    for path in filepaths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                break
            except Exception:
                continue
    if df is None:
        st.error("Error: Could not find dataset file ('cp_values.csv' or 'data.csv') in project directory.")
        st.stop()
    
    # Clean string columns from trailing whitespace
    for col in ["Category", "Material_Name", "Formula", "Unit", "Source"]:
        if col in df.columns and df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
    
    # Ensure numeric columns
    for col in ["A", "B", "C", "T_min", "T_max"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
    return df

df = load_thermo_data()

# Inject Custom CSS Styling
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    --bg-dark: #0B132B;
    --panel-bg: #1C2541;
    --card-bg: #16213E;
    --card-hover: #1F2D5A;
    --accent-blue: {COLD};
    --accent-purple: {MID};
    --accent-pink: {WARM};
    --accent-amber: {AMBER};
    --border-color: #2D3A5E;
    --text-main: #F4F7F6;
    --text-muted: #94A3B8;
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: var(--text-main);
}}

/* App Background */
.stApp {{
    background: radial-gradient(circle at 10% 0%, #152238 0%, var(--bg-dark) 55%) fixed;
}}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {{
    background-color: var(--panel-bg) !important;
    border-right: 1px solid var(--border-color);
}}
section[data-testid="stSidebar"] * {{
    color: var(--text-main) !important;
}}

/* Header Banner */
.hero-header {{
    background: linear-gradient(135deg, rgba(28,37,65,0.8) 0%, rgba(22,33,62,0.9) 100%);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}}

.eyebrow-badge {{
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent-blue);
    background: rgba(76, 201, 240, 0.12);
    border: 1px solid rgba(76, 201, 240, 0.3);
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    margin-bottom: 0.6rem;
}}

.hero-title {{
    font-family: 'Outfit', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0.2rem 0;
    background: linear-gradient(90deg, #4CC9F0 0%, #7209B7 50%, #F72585 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.hero-subtitle {{
    font-size: 0.95rem;
    color: var(--text-muted);
    margin-bottom: 0.2rem;
}}

/* Card Widget */
.thermo-card {{
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease-in-out;
}}
.thermo-card:hover {{
    border-color: var(--accent-blue);
    background: var(--card-hover);
}}

/* Metric Cards Grid */
.metric-box {{
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    text-align: center;
}}
.metric-label {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 0.2rem;
}}
.metric-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--accent-blue);
}}

/* Formula Pill Chips */
.chip {{
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--text-main);
    margin-right: 0.4rem;
}}

/* Section Titles */
.section-title {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-main);
    margin: 1.2rem 0 0.8rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

/* Footer Badge */
.student-footer {{
    text-align: center;
    font-size: 0.8rem;
    color: var(--text-muted);
    padding: 1rem;
    border-top: 1px solid var(--border-color);
    margin-top: 2rem;
}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Kelley Equation function: Cp = a + b*T + c/T^2
def cp_kelley(a: float, b: float, c: float, T: np.ndarray) -> np.ndarray:
    return float(a) + float(b) * T + float(c) / (T ** 2)

# Helper function to style Matplotlib plot to match dark theme
def create_styled_plot():
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=100)
    fig.patch.set_facecolor('#16213E')
    ax.set_facecolor('#0F172A')
    
    ax.spines['bottom'].set_color('#334155')
    ax.spines['top'].set_color('#334155')
    ax.spines['right'].set_color('#334155')
    ax.spines['left'].set_color('#334155')
    
    ax.xaxis.label.set_color('#E2E8F0')
    ax.yaxis.label.set_color('#E2E8F0')
    ax.title.set_color('#F8FAFC')
    
    ax.tick_params(colors='#94A3B8', which='both', labelsize=9)
    ax.grid(True, color='#334155', linestyle='--', linewidth=0.7, alpha=0.5)
    return fig, ax

# Helper function to render Material Card HTML
def render_material_card(row, accent_color=COLD):
    t_min, t_max = float(row["T_min"]), float(row["T_max"])
    source_val = row.get("Source", "N/A")
    return f"""
    <div class='thermo-card' style='border-left: 4px solid {accent_color};'>
        <div style='display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;'>
            <div>
                <h3 style='margin:0 0 0.4rem 0; font-family: Outfit, sans-serif; font-size: 1.3rem; color: #F4F7F6;'>{row['Material_Name']}</h3>
                <div>
                    <span class='chip' style='background: rgba(76,201,240,0.12); color: #4CC9F0; border-color: rgba(76,201,240,0.3);'>Formula: <b>{row['Formula']}</b></span>
                    <span class='chip'>Category: <b>{row['Category']}</b></span>
                </div>
            </div>
            <div style='text-align: right;'>
                <span class='chip' style='background: rgba(247,37,133,0.15); color: #F72585; border-color: rgba(247,37,133,0.4);'>
                    Valid Range: <b>{t_min:.0f} K – {t_max:.0f} K</b>
                </span>
                <div style='font-size:0.78rem; color:#94A3B8; margin-top:0.35rem;'>Source: <i>{source_val}</i></div>
            </div>
        </div>
    </div>
    """

# Sidebar Header & Controls
with st.sidebar:
    st.markdown("<div class='eyebrow-badge'>Thermodynamics Lab</div>", unsafe_allow_html=True)
    st.markdown("### 🌡️ Specific Heat ($C_p$) Explorer")
    st.markdown("---")
    
    selected_mode = st.radio(
        "Select Mode",
        ["Single Material Analysis", "Compare Materials"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("#### 📊 Database Quick Stats")
    st.markdown(f"• **Total Materials:** `{len(df)}`")
    st.markdown(f"• **Categories:** `{df['Category'].nunique()}` ({', '.join(sorted(df['Category'].unique()))})")
    
    with st.expander("🔍 View Materials Database"):
        search_q = st.text_input("Filter material", "")
        db_show = df[["Material_Name", "Formula", "Category"]]
        if search_q:
            db_show = db_show[db_show["Material_Name"].str.contains(search_q, case=False) | db_show["Formula"].str.contains(search_q, case=False)]
        st.dataframe(db_show, use_container_width=True, height=220)
        
    st.markdown("---")
    

# Header Banner on Main Page
st.markdown(
    """
    <div class='hero-header'>
        <div class='eyebrow-badge'>KELLEY EQUATION · MATERIALS THERMODYNAMICS</div>
        <div class='hero-title'>Heat Capacity (Cp vs T) Explorer</div>
        <div class='hero-subtitle'>
            Analyze and compare specific heat capacity temperature dependence derived from empirical constants.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# SINGLE MATERIAL MODE
if selected_mode == "Single Material Analysis":
    st.markdown("<div class='section-title'>📌 Single Material Inspection</div>", unsafe_allow_html=True)
    
    categories = sorted(df["Category"].unique())
    col1, col2 = st.columns(2)
    
    with col1:
        selected_cat = st.selectbox(
            "1. Select Category",
            options=categories,
            key="single_cat"
        )
    
    filtered_df = df[df["Category"] == selected_cat]
    mats = sorted(filtered_df["Material_Name"].unique())
    
    with col2:
        selected_mat = st.selectbox(
            "2. Select Material",
            options=mats,
            key="single_mat"
        )
        
    row = filtered_df[filtered_df["Material_Name"] == selected_mat].iloc[0]
    t_min, t_max = float(row["T_min"]), float(row["T_max"])
    unit_label = row.get("Unit", "J/mol·K")
    
    # Material Overview Card
    st.markdown(render_material_card(row, accent_color=COLD), unsafe_allow_html=True)
    
    # Temperature Slider
    t_range = st.slider(
        "3. Temperature Range Selection (K)",
        min_value=t_min,
        max_value=t_max,
        value=(t_min, t_max),
        step=max((t_max - t_min) / 200, 1.0),
        key="single_t_slider"
    )
    
    t_start, t_end = t_range
    T_arr = np.linspace(t_start, t_end, 300)
    Cp_arr = cp_kelley(row["A"], row["B"], row["C"], T_arr)
    
    # Thermodynamics Key Metrics Cards
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    
    # Calculate Cp at 298.15 K if in range
    cp_298 = cp_kelley(row["A"], row["B"], row["C"], np.array([298.15]))[0] if (t_min <= 298.15 <= t_max) else None
    
    with mcol1:
        st.markdown(
            f"""
            <div class='metric-box'>
                <div class='metric-label'>Cp at 298.15 K (STP)</div>
                <div class='metric-value'>{"{:.2f}".format(cp_298) if cp_298 else 'Out of Range'}</div>
                <div style='font-size:0.7rem; color:#94A3B8;'>{unit_label if cp_298 else ''}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with mcol2:
        st.markdown(
            f"""
            <div class='metric-box'>
                <div class='metric-label'>Min Cp in Range</div>
                <div class='metric-value'>{Cp_arr.min():.2f}</div>
                <div style='font-size:0.7rem; color:#94A3B8;'>at T = {T_arr[Cp_arr.argmin()]:.0f} K</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with mcol3:
        st.markdown(
            f"""
            <div class='metric-box'>
                <div class='metric-label'>Max Cp in Range</div>
                <div class='metric-value'>{Cp_arr.max():.2f}</div>
                <div style='font-size:0.7rem; color:#94A3B8;'>at T = {T_arr[Cp_arr.argmax()]:.0f} K</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with mcol4:
        st.markdown(
            f"""
            <div class='metric-box'>
                <div class='metric-label'>Mean Cp</div>
                <div class='metric-value'>{Cp_arr.mean():.2f}</div>
                <div style='font-size:0.7rem; color:#94A3B8;'>{unit_label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    
    # Styled Matplotlib Chart
    fig, ax = create_styled_plot()
    ax.plot(T_arr, Cp_arr, color=WARM, linewidth=2.5, label=f"{row['Material_Name']} ({row['Formula']})")
    
    # Annotate Room Temperature 298.15 K if in current view window
    if t_start <= 298.15 <= t_end and cp_298 is not None:
        ax.axvline(298.15, color=COLD, linestyle=':', alpha=0.7, label='Room Temp (298.15 K)')
        ax.scatter([298.15], [cp_298], color=COLD, s=40, zorder=5)
        
    ax.set_xlabel("Temperature, T (K)", fontsize=10, fontweight='medium')
    ax.set_ylabel(f"Specific Heat, Cp ({unit_label})", fontsize=10, fontweight='medium')
    ax.set_title(f"Heat Capacity Curve: {row['Material_Name']} ({row['Formula']})", fontsize=12, fontweight='bold', pad=12)
    
    legend = ax.legend(facecolor='#1C2541', edgecolor='#3A506B', labelcolor='#F4F7F6', loc='best')
    
    st.pyplot(fig, use_container_width=True)
    
    # Interactive Formula & Coefficient Expander
    with st.expander("📐 View Kelley Equation & Empirical Coefficients", expanded=False):
        st.latex(r"C_p(T) = a + b \cdot T + \frac{c}{T^2} \quad \left[\text{J/mol}\cdot\text{K}\right]")
        ecol1, ecol2, ecol3 = st.columns(3)
        with ecol1:
            st.markdown(f"<div class='metric-box'><div class='metric-label'>Constant 'a'</div><div class='metric-value' style='color:#4CC9F0;'>{row['A']:.5g}</div></div>", unsafe_allow_html=True)
        with ecol2:
            st.markdown(f"<div class='metric-box'><div class='metric-label'>Constant 'b'</div><div class='metric-value' style='color:#FFB703;'>{row['B']:.5g}</div></div>", unsafe_allow_html=True)
        with ecol3:
            st.markdown(f"<div class='metric-box'><div class='metric-label'>Constant 'c'</div><div class='metric-value' style='color:#F72585;'>{row['C']:.5g}</div></div>", unsafe_allow_html=True)

# COMPARE MATERIALS MODE
elif selected_mode == "Compare Materials":
    st.markdown("<div class='section-title'>⚖️ Comparative Material Thermodynamics</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Compare temperature dependence of heat capacity between two materials.</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)
    
    categories = sorted(df["Category"].unique())
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔹 Material 1 Selection")
        cat1 = st.selectbox("Category 1", options=["All Categories"] + list(categories), key="cmp_cat_1")
        pool1 = df if cat1 == "All Categories" else df[df["Category"] == cat1]
        mats1 = sorted(pool1["Material_Name"].unique())
        mat1 = st.selectbox("Material 1", options=mats1, index=0 if mats1 else 0, key="cmp_mat_1")
        
    with col2:
        st.markdown("#### 🔸 Material 2 Selection")
        cat2 = st.selectbox("Category 2", options=["All Categories"] + list(categories), key="cmp_cat_2")
        pool2 = df if cat2 == "All Categories" else df[df["Category"] == cat2]
        mats2 = sorted(pool2["Material_Name"].unique())
        default_idx2 = 1 if (mats1 == mats2 and len(mats2) > 1) else 0
        mat2 = st.selectbox("Material 2", options=mats2, index=default_idx2 if mats2 else 0, key="cmp_mat_2")

    if not mat1 or not mat2:
        st.warning("Please select valid materials in both columns.")
    else:
        r1 = df[df["Material_Name"] == mat1].iloc[0]
        r2 = df[df["Material_Name"] == mat2].iloc[0]
        
        # Render Material Cards side-by-side for comparison
        card_col1, card_col2 = st.columns(2)
        with card_col1:
            st.markdown(render_material_card(r1, accent_color=COLD), unsafe_allow_html=True)
        with card_col2:
            st.markdown(render_material_card(r2, accent_color=WARM), unsafe_allow_html=True)
        
        global_min_t = min(float(r1["T_min"]), float(r2["T_min"]))
        global_max_t = max(float(r1["T_max"]), float(r2["T_max"]))
        
        st.markdown("<div style='margin-top:0.4rem;'></div>", unsafe_allow_html=True)
        t_cmp_range = st.slider(
            "Select Display Temperature Range (K)",
            min_value=global_min_t,
            max_value=global_max_t,
            value=(global_min_t, global_max_t),
            step=max((global_max_t - global_min_t) / 200, 1.0),
            key="cmp_t_slider"
        )
        
        t_start, t_end = t_cmp_range
        T_arr = np.linspace(t_start, t_end, 300)
        
        # Styled Comparison Chart
        fig, ax = create_styled_plot()
        
        colors = [COLD, WARM]
        styles = ['-', '--']
        
        summary_list = []
        
        for idx, r in enumerate([r1, r2]):
            t_min_m, t_max_m = float(r["T_min"]), float(r["T_max"])
            valid_mask = (T_arr >= t_min_m) & (T_arr <= t_max_m)
            
            Cp_full = np.full_like(T_arr, np.nan, dtype=float)
            if np.any(valid_mask):
                Cp_full[valid_mask] = cp_kelley(r["A"], r["B"], r["C"], T_arr[valid_mask])
                
            ax.plot(
                T_arr, Cp_full, linewidth=2.5, color=colors[idx], linestyle=styles[idx],
                label=f"{r['Material_Name']} ({r['Formula']}) [{t_min_m:.0f}–{t_max_m:.0f} K]"
            )
            
            valid_vals = Cp_full[~np.isnan(Cp_full)]
            start_cp = f"{valid_vals[0]:.2f}" if len(valid_vals) > 0 else "Out of Range"
            end_cp = f"{valid_vals[-1]:.2f}" if len(valid_vals) > 0 else "Out of Range"
            
            summary_list.append({
                "Material": r["Material_Name"],
                "Formula": r["Formula"],
                "Category": r["Category"],
                "Valid Range (K)": f"{t_min_m:.0f} – {t_max_m:.0f}",
                "Start Cp (in view)": start_cp,
                "End Cp (in view)": end_cp,
                "Source": r["Source"]
            })
            
        ax.set_xlabel("Temperature, T (K)", fontsize=10, fontweight='medium')
        ax.set_ylabel("Specific Heat, Cp (J/mol·K)", fontsize=10, fontweight='medium')
        ax.set_title(f"Comparative Cp vs T Curves: {r1['Material_Name']} vs {r2['Material_Name']}", fontsize=12, fontweight='bold', pad=12)
        ax.legend(facecolor='#1C2541', edgecolor='#3A506B', labelcolor='#F4F7F6', loc='best')
        
        st.pyplot(fig, use_container_width=True)
        
        # Summary Comparison Table
        st.markdown("<div class='section-title'>📋 Comparison Summary Table</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(summary_list), use_container_width=True)



