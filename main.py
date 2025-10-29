import streamlit as st
import pandas as pd
import plotly.express as px
import base64

st.set_page_config(page_title="Carbon Sense", layout="wide", page_icon="🌱", initial_sidebar_state="expanded")

def get_logo_base64(path="logo.png"):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

logo_base64 = get_logo_base64()
if logo_base64:
    # If the logo is a dark image, consider replacing with a light/transparent variant for dark mode
    st.markdown(
        f"<img src='data:image/png;base64,{logo_base64}' width='140' style='display:block;margin:auto;filter:brightness(1.1);'>",
        unsafe_allow_html=True
    )

# Dark mode CSS
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

        :root {
            --bg: #0b1220;
            --card: #0f1724;
            --muted: #94a3b8;
            --text: #e6eef8;
            --accent: #2dd4bf;
            --accent-2: #60a5fa;
            --table-border: #1f2a37;
        }

        html, body, [class*="css"] {
            background: var(--bg) !important;
            color: var(--text) !important;
            font-family: 'Montserrat', 'Segoe UI', sans-serif !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)) !important;
            color: var(--text) !important;
        }
        section[data-testid="stSidebar"] .css-1d391kg { color: var(--text) !important; }

        /* Main content cards */
        .stApp, .main {
            background: var(--bg) !important;
            color: var(--text) !important;
        }

        /* Titles and headings */
        h1, h2, h3, h4, h5, h6, .stCaption, .stMarkdown {
            color: var(--text) !important;
            font-family: 'Montserrat', 'Segoe UI', sans-serif !important;
        }

        /* Dataframe styling */
        div[data-testid="stDataFrame"] table {
            border: 1px solid var(--table-border) !important;
            border-radius: 8px;
            background-color: transparent !important;
            color: var(--text) !important;
        }
        div[data-testid="stDataFrame"] th {
            background: rgba(255,255,255,0.03) !important;
            color: var(--text) !important;
        }
        div[data-testid="stDataFrame"] td {
            background: rgba(255,255,255,0.01) !important;
            color: var(--text) !important;
        }

        /* Input controls */
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSlider>div {
            background: rgba(255,255,255,0.03) !important;
            color: var(--text) !important;
        }
        .stButton>button {
            background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
            color: #042027 !important;
            border: none !important;
        }

        /* Executive summary card */
        .exec-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
            border: 1px solid rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 22px;
            color: var(--text);
        }

        /* Tips list */
        .tips li { color: var(--muted); }

        /* Footer */
        .footer { color: var(--muted); font-size:13px; text-align:center; margin-top:18px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌿 Carbon Sense")
st.caption("Estimate and visualize CO₂ emissions for logistics and operations")

def executive_summary(total, optimized, reduction):
    if reduction > 40:
        msg = "Outstanding! Your optimizations yield significant reductions in carbon footprint."
    elif reduction > 20:
        msg = "Good progress. Consider further electrification and efficiency upgrades."
    else:
        msg = "There's room for improvement. Explore emission reduction strategies."
    return f"""
    <div class='exec-card' style='font-family:Montserrat,sans-serif;'>
        <h3 style='color:var(--text);font-weight:700;margin-bottom:0;font-family:Montserrat,sans-serif;'>Executive Summary</h3>
        <p style='font-size:18px;margin:8px 0;font-family:Montserrat,sans-serif;'>Total Baseline Emissions: <strong>{total:.1f} tons CO₂e</strong></p>
        <p style='font-size:18px;margin:8px 0;font-family:Montserrat,sans-serif;'>Optimized Emissions: <strong>{optimized:.1f} tons CO₂e</strong></p>
        <p style='font-size:18px;font-family:Montserrat,sans-serif;'>Estimated Emission Reduction: <strong style="color:var(--accent);">{reduction:.1f}%</strong></p>
        <p style='margin-top:12px;font-size:15px;font-family:Montserrat,sans-serif;color:var(--muted);'>{msg}</p>
    </div>
    """

with st.sidebar:
    st.header("INPUTS: ACTIVITY DATA")
    cars_km = st.number_input("Cars - distance (km/year) ℹ️", 0, 1_000_000, 230000, help="Total annual km driven by fleet cars")
    ev_share = st.slider("EV Share (%) ℹ️", 0, 100, 30, help="Percent of cars that are electric vehicles")
    km_reduction = st.slider("KM Reduction (%) ℹ️", 0, 100, 10, help="Percent reduction in driving distance (e.g. by route optimization)")
    trucks_km = st.number_input("Trucks - distance (km/year) ℹ️", 0, 1_000_000, 150000, help="Total annual km driven by trucks")
    buses_km = st.number_input("Buses - distance (km/year) ℹ️", 0, 1_000_000, 80000, help="Total annual km by buses")
    forklift_hr = st.number_input("Forklifts - operating hours/year ℹ️", 0, 5000, 600, help="Total annual operating hours for forklifts")
    planes_hr = st.number_input("Cargo Planes - flight hours/year ℹ️", 0, 2000, 400, help="Total annual flight hours by cargo planes")
    load_factor = st.slider("Load Factor (%) ℹ️", 0, 100, 80, help="Average cargo load factor for planes")
    lighting_kwh = st.number_input("Office Lighting (kWh/year) ℹ️", 0, 50000, 12000, help="Annual kWh for lighting")
    heating_kwhth = st.number_input("Heating (kWh-th/year) ℹ️", 0, 50000, 10000, help="Annual thermal energy for heating")
    cooling_kwh = st.number_input("Cooling A/C (kWh/year) ℹ️", 0, 50000, 15000, help="Annual electricity for cooling")
    computing_kwh = st.number_input("Computing IT (kWh/year) ℹ️", 0, 50000, 18000, help="Annual electricity for IT/computing")

factors = {
    "Cars": 0.18,
    "Trucks": 0.90,
    "Buses": 1.10,
    "Forklifts": 4.0,
    "Cargo Planes": 9000,
    "Office Lighting": 0.42,
    "Heating": 0.20,
    "Cooling": 0.42,
    "Computing IT": 0.42
}

def calculate_emissions():
    cars_em = ((cars_km * factors["Cars"]) * (1 - 0.7 * ev_share / 100) * (1 - km_reduction / 100)) / 1000
    trucks_em = (trucks_km * factors["Trucks"]) / 1000
    buses_em = (buses_km * factors["Buses"]) / 1000
    forklifts_em = (forklift_hr * factors["Forklifts"]) / 1000
    planes_em = (planes_hr * factors["Cargo Planes"] * (load_factor / 100)) / 1000
    lighting_em = (lighting_kwh * factors["Office Lighting"]) / 1000
    heating_em = (heating_kwhth * factors["Heating"]) / 1000
    cooling_em = (cooling_kwh * factors["Cooling"]) / 1000
    computing_em = (computing_kwh * factors["Computing IT"]) / 1000

    total_baseline = sum([
        cars_em, trucks_em, buses_em, forklifts_em, planes_em,
        lighting_em, heating_em, cooling_em, computing_em
    ])

    optimized_values = {
        "Cars": cars_em * 0.75,
        "Trucks": trucks_em * 0.85,
        "Buses": buses_em * 0.9,
        "Forklifts": forklifts_em * 0.9,
        "Cargo Planes": planes_em * 0.8,
        "Office Lighting": lighting_em * 0.7,
        "Heating": heating_em * 0.8,
        "Cooling": cooling_em * 0.75,
        "Computing IT": computing_em * 0.8
    }
    total_optimized = sum(optimized_values.values())
    return {
        "baseline": {
            "Cars": cars_em, "Trucks": trucks_em, "Buses": buses_em, "Forklifts": forklifts_em,
            "Cargo Planes": planes_em, "Office Lighting": lighting_em, "Heating": heating_em,
            "Cooling": cooling_em, "Computing IT": computing_em
        },
        "optimized": optimized_values,
        "total_baseline": total_baseline,
        "total_optimized": total_optimized
    }

results = calculate_emissions()
# avoid division by zero
if results["total_baseline"] == 0:
    reduction = 0.0
else:
    reduction = (1 - results["total_optimized"] / results["total_baseline"]) * 100

st.markdown(executive_summary(results["total_baseline"], results["total_optimized"], reduction), unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

# Use a lighter palette that stands out on dark background
pie_colors = [
    "#60a5fa",  # light blue
    "#34d399",  # teal
    "#f59e0b",  # amber
    "#fb7185",  # pink
    "#a78bfa",  # purple
    "#38bdf8",  # sky
    "#f472b6",  # rose
    "#06b6d4",  # cyan
    "#94a3b8"   # muted
]

with col1:
    df_pie = pd.DataFrame({
        "Category": list(results["optimized"].keys()),
        "Emission": list(results["optimized"].values())
    })

    # Keep the biggest slice visually emphasized
    biggest_idx = df_pie["Emission"].idxmax()
    pie_colors_ordered = pie_colors.copy()
    if biggest_idx != 0:
        pie_colors_ordered[biggest_idx], pie_colors_ordered[0] = pie_colors_ordered[0], pie_colors_ordered[biggest_idx]

    pie_fig = px.pie(
        df_pie,
        values="Emission",
        names="Category",
        title="Emission Share by Category (Post-Optimization)",
        color_discrete_sequence=pie_colors_ordered,
        template="plotly_dark"
    )
    pie_fig.update_traces(
        textinfo="none",
        marker=dict(line=dict(color="rgba(0,0,0,0.4)", width=1.5)),
        pull=[0.08 if v == max(df_pie["Emission"]) else 0 for v in df_pie["Emission"]],
        hovertemplate="<b>%{label}</b><br>CO₂e: %{value:.2f} tons"
    )
    pie_fig.update_layout(
        title_font=dict(size=22, color="#e6eef8", family="Montserrat"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=12, color="#e6eef8", family="Montserrat")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6eef8",
        font_family="Montserrat",
        height=550
    )
    st.plotly_chart(pie_fig, use_container_width=True)

with col2:
    bar_fig = px.bar(
        x=["Baseline", "Optimized"],
        y=[results["total_baseline"], results["total_optimized"]],
        text=[f"{results['total_baseline']:.1f}", f"{results['total_optimized']:.1f}"],
        title="Total Emissions (tons CO₂e) — Baseline vs Optimized",
        color=["Baseline", "Optimized"],
        color_discrete_map={"Baseline": "#94a3b8", "Optimized": "#34d399"},
        template="plotly_dark"
    )
    bar_fig.update_traces(
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.5)",
        marker_line_width=1.2
    )
    bar_fig.update_layout(
        title_font=dict(size=20, color="#e6eef8", family="Montserrat"),
        yaxis_title="Tons of CO₂e",
        height=550,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e6eef8",
        font_family="Montserrat"
    )
    st.plotly_chart(bar_fig, use_container_width=True)

st.markdown("<h3 style='font-family:Montserrat,sans-serif;color:var(--text);'>📋 Emission Summary Table</h3>", unsafe_allow_html=True)
summary_df = pd.DataFrame({
    "Category": list(results["baseline"].keys()),
    "Baseline (tons CO₂e)": list(results["baseline"].values()),
    "Optimized (tons CO₂e)": list(results["optimized"].values())
})

# Use Styler to set dark-friendly colors
styled = summary_df.style.format({
    "Baseline (tons CO₂e)": "{:.2f}",
    "Optimized (tons CO₂e)": "{:.2f}"
}).set_properties(**{
    "background-color": "transparent",
    "color": "#e6eef8",
    "font-family": "Montserrat"
}).set_table_styles([
    {"selector": "thead", "props": [("background-color", "rgba(255,255,255,0.03)"), ("color", "#e6eef8")]},
    {"selector": "tbody tr:nth-child(even)", "props": [("background-color", "rgba(255,255,255,0.01)")]}
])

st.dataframe(styled, use_container_width=True)

st.markdown(f"<h3 style='font-family:Montserrat,sans-serif;color:var(--text);'>Total Baseline Emissions: {results['total_baseline']:.1f} tons CO₂e</h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='font-family:Montserrat,sans-serif;color:var(--text);'>Total Optimized Emissions: {results['total_optimized']:.1f} tons CO₂e</h3>", unsafe_allow_html=True)

# Use custom success-like display for dark background
st.markdown(f"""
<div style='margin:6px 0;padding:10px;border-radius:8px;background:linear-gradient(90deg,#022f2a, rgba(255,255,255,0.02)); color: #bff3e8; font-weight:600; display:inline-block;'>
💡 Estimated Emission Reduction: {reduction:.1f}%
</div>
""", unsafe_allow_html=True)

tips = [
    "Increase EV share in fleet for dramatic CO₂ savings.",
    "Optimize truck/bus routes to reduce travel distance.",
    "Switch to LED lighting and smart controls.",
    "Invest in building insulation for heating/cooling efficiency.",
    "Utilize cloud-based IT for better energy management."
]
st.markdown("<hr style='border-color:rgba(255,255,255,0.04)'>", unsafe_allow_html=True)
st.markdown("<h3 style='font-family:Montserrat,sans-serif;color:var(--text);'>🌟 Sustainability Recommendations</h3>", unsafe_allow_html=True)
for tip in tips:
    st.markdown(f"- <span style='color:var(--muted);'>{tip}</span>", unsafe_allow_html=True)

st.caption("<span style='color:var(--muted)'>Developed by Team DPWPZ | Powered by Sustainable Tech 💚</span>", unsafe_allow_html=True)

st.markdown("""
    <div class='footer'>
        © 2025 Carbon Sense
    </div>
""", unsafe_allow_html=True)