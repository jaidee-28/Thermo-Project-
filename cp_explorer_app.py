

import numpy as np
import pandas as pd

import plotly.graph_objects as go
import streamlit as st



st.set_page_config(page_title="Cp vs T Materials Explorer", layout="wide")

COLD = "#4CC9F0"
MID = "#7C83FD"
HOT = "#FF6B35"
HOTTER = "#FF3D3D"
THERMAL_RAMP = [COLD, MID, HOT, HOTTER]




CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    --bg: #0B1220;
    --bg-panel: #101828;
    --bg-card: #16213A;
    --border: #263352;
    --text: #EAF2F8;
    --text-muted: #8A9BAE;
    --cold: {COLD};
    --hot: {HOT};
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: var(--text);
}}

.stApp {{
    background: radial-gradient(circle at 15% 0%, #101c33 0%, var(--bg) 45%) fixed;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: var(--bg-panel);
    border-right: 1px solid var(--border);
}}
section[data-testid="stSidebar"] * {{
    color: var(--text) !important;
}}
section[data-testid="stSidebar"] .stRadio label {{
    font-family: 'Inter', sans-serif;
}}


/* Eyebrow label */
.eyebrow {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--cold);
    margin-bottom: 0.3rem;
}}

/* Hero */
.hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.6rem;
    line-height: 1.05;
    margin: 0 0 0.4rem 0;
    background: linear-gradient(90deg, {COLD} 0%, {MID} 35%, {HOT} 75%, {HOTTER} 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.hero-sub {{
    color: var(--text-muted);
    font-size: 1.02rem;
    max-width: 640px;

    margin-bottom: 0.6rem;
}}


/* Card */
.card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.9rem;
}}
.card h4 {{
    margin-top: 0;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    color: var(--text);
}}
.meta-line {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--text-muted);
}}
.meta-line b {{
    color: var(--text);
}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown("<div class='eyebrow'>KELLEY EQUATION · Cp = a + bT + c/T²</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-title'>Heat Capacity Explorer</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='hero-sub'>Trace how specific heat shifts from cryogenic to furnace "
    "temperatures, one material at a time or several side by side.</div>",
    unsafe_allow_html=True,
)
st.markdown("<div class='thermal-rule'></div>", unsafe_allow_html=True)

 
 
def cp_curve(a: float, b: float, c: float, t_arr: np.ndarray) -> np.ndarray:
    """Kelley equation: Cp = a + b*T + c/T^2"""
    a = float(a)
    b = float(b)
    c = float(c)
    return a + b * t_arr + c/(t_arr ** 2)

def thermal_color(i: int, n: int) -> str:
    """Map an index across n items onto the cold→hot ramp."""
    if n <= 1:
        return HOT
    t = i / (n - 1)
    stops = [(0.0, COLD), (0.35, MID), (0.75, HOT), (1.0, HOTTER)]
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t0 <= t <= t1:
            f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            return _lerp_hex(c0, c1, f)
    return HOT
def _lerp_hex(c0: str, c1: str, f: float) -> str:
    c0 = c0.lstrip("#")
    c1 = c1.lstrip("#")
    r0, g0, b0 = int(c0[0:2], 16), int(c0[2:4], 16), int(c0[4:6], 16)
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r = round(r0 + (r1 - r0) * f)
    g = round(g0 + (g1 - g0) * f)
    b = round(b0 + (b1 - b0) * f)
    return f"#{r:02x}{g:02x}{b:02x}"

def style_plotly(fig: go.Figure, title: str, y_label: str) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(family="Space Grotesk, sans-serif", size=18, color="#EAF2F8")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="Inter, sans-serif", color="#8A9BAE"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#EAF2F8")),
        xaxis=dict(title="Temperature, T (K)", gridcolor="#22304a", zeroline=False),
        yaxis=dict(title=y_label, gridcolor="#22304a", zeroline=False),
        margin=dict(l=10, r=10, t=55, b=10),
        hovermode="x unified",
        height=480,
    )
    return fig



st.sidebar.title("Select Type Of Analysis")
 
df = pd.read_csv("data.csv")

st.markdown("<div class='hero-title'>Cp vs T Curve Ploting</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-sub'>Heat capacity curves from the Kelley equation:  Cp = a + b·T + c/T²  (J/mol·K)</div>", unsafe_allow_html=True)

selected_tab = st.sidebar.radio(
    "Select View",
    ["Single Material", "Compare Materials"]
)

if selected_tab == "Single Material":
    st.markdown("<div class='hero-title'>Single Material Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Explore a single material</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
            st.markdown("<div class='eyebrow'>1. Select category</div>", unsafe_allow_html=True)
            category = st.selectbox(

                "",

                sorted(df["Category"].unique()),

                key="single_category",

            ) 


    filtered_df = df[df["Category"] == category]
     
    with col2:
            st.markdown("<div class='eyebrow'>2. Select material</div>", unsafe_allow_html=True)
            Material_Name = st.selectbox(
                "",
                sorted(filtered_df["Material_Name"].unique()),
                key="single_material",
            )
     
    row = filtered_df[filtered_df["Material_Name"] == Material_Name].iloc[0]
     
    t_min, t_max = float(row["T_min"]), float(row["T_max"])
     
    st.markdown(
            f"<div class='card'><span class='meta-line'>"
            f"<b>Formula</b> {row['Formula']} &nbsp;·&nbsp; "
            f"<b>Valid range</b> {t_min:.0f}–{t_max:.0f} K &nbsp;·&nbsp; "
            f"<b>Source</b> {row.get('Source', '—')}"
            f"</span></div>",
            unsafe_allow_html=True,
        )
    
    st.markdown("<div class='eyebrow'>3. Select temperature range</div>", unsafe_allow_html=True)
    t_range = st.slider(
         
            "",
            min_value=t_min,
            max_value=t_max,
            value=(t_min, t_max),
            step=max((t_max - t_min) / 200, 1.0),
            key="single_t_range",
        )
     
    t_start, t_end = t_range
    T = np.linspace(t_start, t_end, 300)

    Cp = cp_curve(row["A"], row["B"], row["C"], T)
    
    unit_label = row.get("Unit", "J/mol·K")
    st.markdown("<div class='hero-title'>4. Cp vs T curve</div>", unsafe_allow_html=True)
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=T, y=Cp, mode="lines", name=Material_Name,
            line=dict(color=HOT, width=3),
            fill="none", fillcolor="rgba(255,107,53,0.08)",
            hovertemplate="T = %{x:.0f} K<br>Cp = %{y:.2f}<extra></extra>",
        )
    )
    fig = style_plotly(fig, f"Cp vs T — {Material_Name} ({row['Formula']})", f"Specific heat, Cp ({unit_label})")
    st.plotly_chart(fig, use_container_width=True)

    
elif selected_tab == "Compare Materials":
    st.markdown("<div class='hero-title'>Compare Materials</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Compare Cp–T curves of multiple materials (same conditions)</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    categories = sorted(df["Category"].unique())

    with col1:
        st.markdown("<div class='eyebrow'>1. Select category and material</div>", unsafe_allow_html=True)
        cat1 = st.selectbox(
            "Category 1",
            options=["All Categories"] + list(categories),
            key="cat_1",
            label_visibility="collapsed"
        )
        
        pool1 = df if cat1 == "All Categories" else df[df["Category"] == cat1]
        mats1 = sorted(pool1["Material_Name"].unique())
        st.markdown(f"<div class='eyebrow'>2. Select material ({cat1})</div>", unsafe_allow_html=True)
        mat1 = st.selectbox(
            "Material 1",
            options=mats1,
            index=0 if mats1 else None,
            key="select_mat_1",
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("<div class='eyebrow'>1. Select category and material</div>", unsafe_allow_html=True)
        cat2 = st.selectbox(
            "Category 2",
            options=["All Categories"] + list(categories),
            key="cat_2",
            label_visibility="collapsed"
        )

        pool2 = df if cat2 == "All Categories" else df[df["Category"] == cat2]
        mats2 = sorted(pool2["Material_Name"].unique())
        default_idx2 = 1 if (mats1 == mats2 and len(mats2) > 1) else 0
        st.markdown(f"<div class='eyebrow'>2. Select material ({cat2})</div>", unsafe_allow_html=True)    
        mat2 = st.selectbox(
            "Material 2",
            options=mats2,
            index=default_idx2 if mats2 else None,
            key="select_mat_2",
            label_visibility="collapsed"
        )

    # Validation Checks
    if not mat1 or not mat2:
        st.info("Please select a material in both columns.")
    elif mat1 == mat2:
        st.warning("Please select two different materials for comparison.")
    else:
        # All plotting logic MUST be indented inside this 'else' block
        compare_materials = [mat1, mat2]
        selected_rows = df[df["Material_Name"].isin(compare_materials)]

        global_t_min = float(selected_rows["T_min"].min())
        global_t_max = float(selected_rows["T_max"].max())

        common_t_min = float(selected_rows["T_min"].max())
        common_t_max = float(selected_rows["T_max"].min())
        st.markdown("<div class='eyebrow'>3. Select temperature range for comparison</div>", unsafe_allow_html=True)
        t_range_cmp = st.slider(
            "",
            min_value=global_t_min,
            max_value=global_t_max,
            value=(global_t_min, global_t_max),
            step=max((global_t_max - global_t_min) / 200, 1.0),
            key="compare_t_range",
        )

        t_start, t_end = t_range_cmp
        fig, ax = plt.subplots(figsize=(9, 5.5))
        cmap = plt.get_cmap("tab10")

        
        T = np.linspace(t_start, t_end, 300)
        fig = go.Figure()
        summary_rows = []
        n = len(selected_rows)
        for i, (_, r) in enumerate(selected_rows.iterrows()):
                        Cp = cp_curve(r["A"], r["B"], r["C"], T)
                        color = thermal_color(i, n)
                        fig.add_trace(
                            go.Scatter(
                                x=T, y=Cp, mode="lines", name=f"{r['Material_Name']} ({r['Formula']})",
                                line=dict(color=color, width=2.6),
                                hovertemplate="T = %{x:.0f} K<br>Cp = %{y:.2f}<extra>%{fullData.name}</extra>",
                            )
                        )
                        summary_rows.append(
                            {
                                "Material": r["Material_Name"],
                                "Formula": r["Formula"],
                                "Category": r["Category"],
                                f"Cp at {t_start:.0f} K": round(float(Cp[0]), 2),
                                f"Cp at {t_end:.0f} K": round(float(Cp[-1]), 2),
                                "Source": r.get("Source", "—"),
                            }
                        )
        
        fig = style_plotly(fig, "Cp vs T — Material Comparison", "Specific heat, Cp (J/mol·K)")
        st.plotly_chart(fig, use_container_width=True)


        if summary_rows:
            st.markdown("<div class='hero-title'>4. Summary of Visible Curves</div>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)
        else:
            st.info("Adjust the slider to intersect with at least one material's valid temperature range.")
with st.sidebar:
    st.header("Database")
    st.write(f"{len(df)} materials loaded, {df['Category'].nunique()} categories.")
    if st.checkbox("Show full materials table"):
        st.dataframe(df, use_container_width=True)
