"""
Portfolio Simulation Dashboard
Run: streamlit run portfolio_dashboard.py
Requirements: pip install streamlit yfinance plotly pandas openpyxl
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Portfolio Dashboard", layout="wide", page_icon="📊")

# ── Ticker mapping (Bloomberg → Yahoo Finance) ──────────────────────────────
TICKER_MAP = {
    "LAM US Equity":    "LRCX",
    "SNDK US Equity":   "SNDK",
    "MU US Equity":     "MU",
    "BDC US Equity":    "BDC",
    "APLD US Equity":   "APLD",
    "MPWR US Equity":   "MPWR",
    "COHR US Equity":   "COHR",
    "TER US Equity":    "TER",
    "PWR US Equity":    "PWR",
    "CAT US Equity":    "CAT",
    "ON US Equity":     "ON",
    "ADI US Equity":    "ADI",
    "MOG/A US Equity":  "MOG-A",
    "VSEC US Equity":   "VSEC",
    "HII US Equity":    "HII",
    "HXL US Equity":    "HXL",
    "WWD US Equity":    "WWD",
    "HWM US Equity":    "HWM",
    "RTX US Equity":    "RTX",
    "LMT US Equity":    "LMT",
    "NOC US Equity":    "NOC",
    "OXY":              "OXY",
    "CVX":              "CVX",
    "XOM":              "XOM",
    "SLB":              "SLB",
    "BE US Equity":     "BE",
    "WMT":              "WMT",
    "COST":             "COST",
    "DG":               "DG",
    "PG":               "PG",
    "CL":               "CL",
    "6146 JP Equity":   "6146.T",
    "6857 JP Equity":   "6857.T",
    "4062 JP Equity":   "4062.T",
    "6383 JP Equity":   "6383.T",
    "9104 JP":          "9104.T",
    "7011 JP":          "7011.T",
    "7012 JP":          "7012.T",
    "GOLD":             "GLD",
    "SILVER":           "SLV",
    "OIL":              "USO",
    # Chinese/HK tickers (limited Yahoo coverage)
    "688041 CH Equity": "688041.SS",
    "603986 CH Equity": "603986.SS",
    "1772 HK Equity":   "1772.HK",
    "300476 CH Equity": "300476.SZ",
    "002353 CH":        "002353.SZ",
}

# ── Portfolio structure from Excel ──────────────────────────────────────────
PORTFOLIO = [
    # (bloomberg_ticker, name, weight, region, theme, sector)
    ("LAM US Equity",   "Lam Research",             0.004615, "Developed Markets", "Upstream AI",      "Machine"),
    ("SNDK US Equity",  "Sandisk",                  0.004615, "Developed Markets", "Upstream AI",      "Memory"),
    ("MU US Equity",    "Micron Technology",         0.004615, "Developed Markets", "Upstream AI",      "Memory"),
    ("BDC US Equity",   "Belden Inc",               0.004615, "Developed Markets", "Upstream AI",      "Infrastructure - network"),
    ("APLD US Equity",  "Applied Digital Corp",      0.004615, "Developed Markets", "Upstream AI",      "Infrastructure - system"),
    ("MPWR US Equity",  "Monolithic Power Systems",  0.004615, "Developed Markets", "Upstream AI",      "Photooptic"),
    ("COHR US Equity",  "Coherent",                 0.004615, "Developed Markets", "Upstream AI",      "Photooptic"),
    ("TER US Equity",   "Teradyne Inc",             0.004615, "Developed Markets", "Upstream AI",      "Machine"),
    ("PWR US Equity",   "Quanta Services",          0.004615, "Developed Markets", "Upstream AI",      "Infrastructure - service"),
    ("CAT US Equity",   "Caterpillar Inc",          0.004615, "Developed Markets", "Upstream AI",      "Energy - AI"),
    ("ON US Equity",    "ON Semiconductor",         0.004615, "Developed Markets", "Upstream AI",      "Packaging"),
    ("ADI US Equity",   "Analog Devices",           0.004615, "Developed Markets", "Upstream AI",      "Packaging"),
    ("MOG/A US Equity", "Moog Inc",                 0.003333, "Developed Markets", "Defense",          "Sensors"),
    ("VSEC US Equity",  "VSE Corp",                 0.003333, "Developed Markets", "Defense",          "Components"),
    ("HII US Equity",   "Huntington Ingalls",       0.003333, "Developed Markets", "Defense",          "Ship building"),
    ("HXL US Equity",   "Hexcel Corp",              0.003333, "Developed Markets", "Defense",          "Components"),
    ("WWD US Equity",   "Woodward Inc",             0.003333, "Developed Markets", "Defense",          "Components"),
    ("HWM US Equity",   "Howmet Aerospace",         0.003333, "Developed Markets", "Defense",          "Components"),
    ("RTX US Equity",   "RTX Corporation",          0.003333, "Developed Markets", "Defense",          "Drone"),
    ("LMT US Equity",   "Lockheed Martin",          0.003333, "Developed Markets", "Defense",          "Aircraft"),
    ("NOC US Equity",   "Northrop Grumman",         0.003333, "Developed Markets", "Defense",          "Aircraft"),
    ("OXY",             "Occidental Petroleum",     0.006,    "Developed Markets", "Energy",           "Oil field"),
    ("CVX",             "Chevron",                  0.006,    "Developed Markets", "Energy",           "Integrated"),
    ("XOM",             "Exxon Mobil",              0.006,    "Developed Markets", "Energy",           "Integrated"),
    ("SLB",             "Schlumberger",             0.006,    "Developed Markets", "Energy",           "Oil field"),
    ("BE US Equity",    "Bloom Energy",             0.006,    "Developed Markets", "Energy",           "Hydrogen"),
    ("WMT",             "Walmart Inc",              0.003,    "Developed Markets", "Inflation-linked", "Discount store"),
    ("COST",            "Costco",                   0.003,    "Developed Markets", "Inflation-linked", "Big box"),
    ("DG",              "Dollar General",           0.003,    "Developed Markets", "Inflation-linked", "Discount store"),
    ("PG",              "P&G",                      0.003,    "Developed Markets", "Inflation-linked", "Household"),
    ("CL",              "Colgate",                  0.003,    "Developed Markets", "Inflation-linked", "Household"),
    ("6146 JP Equity",  "Disco Corp",               0.025,    "APAC",              "Upstream AI",      "Semiconductor"),
    ("6857 JP Equity",  "Advantest Corp",           0.025,    "APAC",              "Upstream AI",      "Semiconductor"),
    ("4062 JP Equity",  "Ibiden Co Ltd",            0.025,    "APAC",              "Upstream AI",      "Semiconductor"),
    ("6383 JP Equity",  "Daifuku Co Ltd",           0.025,    "APAC",              "Upstream AI",      "Semiconductor"),
    ("9104 JP",         "Mitsui OSK Lines",         0.1,      "APAC",              "Energy",           "Shipping"),
    ("7011 JP",         "Mitsubishi Heavy",         0.05,     "APAC",              "Defense",          "Heavy industry"),
    ("7012 JP",         "Kawasaki Heavy",           0.05,     "APAC",              "Defense",          "Heavy industry"),
    ("688041 CH Equity","Hygon Information Tech",   0.05,     "Emerging Markets",  "Upstream AI",      "Chips"),
    ("603986 CH Equity","GigaDevice",               0.05,     "Emerging Markets",  "Upstream AI",      "Chips"),
    ("1772 HK Equity",  "Ganfeng Lithium",          0.05,     "Emerging Markets",  "Upstream AI",      "Mining"),
    ("300476 CH Equity","Victory Giant",            0.05,     "Emerging Markets",  "Upstream AI",      "PCB"),
    ("002353 CH",       "Yangtai Jereh Oilfield",   0.1,      "Emerging Markets",  "Energy",           "Energy"),
    ("GOLD",            "Gold (GLD ETF)",           0.05,     "Inflation-hedged",  "Precious Metal",   "Gold"),
    ("SILVER",          "Silver (SLV ETF)",         0.05,     "Inflation-hedged",  "Precious Metal",   "Silver"),
    ("OIL",             "Oil (USO ETF)",            0.1,      "Commodity",         "Commodity",        "Oil"),
]

PORTFOLIO_DF = pd.DataFrame(PORTFOLIO, columns=["bb_ticker","name","weight","region","theme","sector"])

TIMEFRAMES = {
    "YTD":  (datetime(datetime.today().year, 1, 1), datetime.today()),
    "1M":   (datetime.today() - timedelta(days=30), datetime.today()),
    "6M":   (datetime.today() - timedelta(days=182), datetime.today()),
    "1Y":   (datetime.today() - timedelta(days=365), datetime.today()),
    "3Y":   (datetime.today() - timedelta(days=1095), datetime.today()),
}

# ── Data fetching ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_prices(tickers: list[str]) -> dict:
    """Download 3Y of daily closes for all tickers."""
    result = {}
    start = datetime.today() - timedelta(days=1100)
    for bb, yf_ticker in tickers:
        try:
            data = yf.download(yf_ticker, start=start, progress=False, auto_adjust=True)
            if not data.empty:
                result[bb] = data["Close"].squeeze()
        except Exception:
            pass
    return result

def calc_return(series: pd.Series, start: datetime, end: datetime) -> float | None:
    try:
        s = series.loc[start:end].dropna()
        if len(s) < 2:
            return None
        return (s.iloc[-1] / s.iloc[0] - 1) * 100
    except Exception:
        return None

def build_returns_table(price_data: dict) -> pd.DataFrame:
    rows = []
    for _, row in PORTFOLIO_DF.iterrows():
        bb = row["bb_ticker"]
        entry = {"bb_ticker": bb, "name": row["name"], "weight": row["weight"],
                 "region": row["region"], "theme": row["theme"], "sector": row["sector"]}
        if bb in price_data:
            s = price_data[bb]
            entry["current_price"] = round(float(s.iloc[-1]), 2)
            for tf, (t_start, t_end) in TIMEFRAMES.items():
                entry[tf] = calc_return(s, t_start, t_end)
        else:
            entry["current_price"] = None
            for tf in TIMEFRAMES:
                entry[tf] = None
        rows.append(entry)
    return pd.DataFrame(rows)

# ── Helpers ──────────────────────────────────────────────────────────────────
def color_return(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "color: grey"
    return "color: #2ecc71" if val >= 0 else "color: #e74c3c"

def fmt_pct(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    return f"{val:+.1f}%"

# ── App ──────────────────────────────────────────────────────────────────────
def main():
    # Header
    st.markdown("""
        <h1 style='margin-bottom:0'>📊 Portfolio Simulation Dashboard</h1>
        <p style='color:grey;margin-top:4px'>Auto-refreshed from Yahoo Finance · Delayed data</p>
    """, unsafe_allow_html=True)

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Settings")
        selected_tf = st.selectbox("Default Timeframe", list(TIMEFRAMES.keys()), index=0)
        selected_regions = st.multiselect("Filter Region", PORTFOLIO_DF["region"].unique().tolist(),
                                           default=PORTFOLIO_DF["region"].unique().tolist())
        selected_themes = st.multiselect("Filter Theme", PORTFOLIO_DF["theme"].unique().tolist(),
                                          default=PORTFOLIO_DF["theme"].unique().tolist())
        refresh = st.button("🔄 Refresh Data", use_container_width=True)
        if refresh:
            st.cache_data.clear()
        st.caption(f"Last loaded: {datetime.now().strftime('%d %b %Y %H:%M')}")

    # Fetch data
    with st.spinner("Fetching prices from Yahoo Finance..."):
        ticker_pairs = [(bb, TICKER_MAP[bb]) for bb in PORTFOLIO_DF["bb_ticker"] if bb in TICKER_MAP]
        price_data = fetch_prices(ticker_pairs)
        df = build_returns_table(price_data)

    # Apply filters
    mask = df["region"].isin(selected_regions) & df["theme"].isin(selected_themes)
    df_filtered = df[mask].copy()

    loaded = df_filtered["current_price"].notna().sum()
    st.caption(f"✅ {loaded}/{len(df_filtered)} tickers loaded successfully")

    # ── KPI row ──────────────────────────────────────────────────────────────
    st.divider()
    col1, col2, col3, col4, col5 = st.columns(5)
    for col, tf in zip([col1, col2, col3, col4, col5], TIMEFRAMES.keys()):
        vals = df_filtered[tf].dropna()
        weights = df_filtered.loc[df_filtered[tf].notna(), "weight"]
        if len(vals) > 0 and weights.sum() > 0:
            wt_return = (vals.values * (weights.values / weights.sum())).sum()
            delta_color = "normal" if wt_return >= 0 else "inverse"
            col.metric(f"Portfolio {tf}", f"{wt_return:+.1f}%",
                       delta=f"Weighted avg", delta_color=delta_color)
        else:
            col.metric(f"Portfolio {tf}", "N/A")

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Holdings Table", "📈 Price Performance", "🧩 Allocation", "📉 Price Chart"])

    # ── Tab 1: Holdings Table ─────────────────────────────────────────────────
    with tab1:
        st.subheader("Holdings — Return by Timeframe")

        display = df_filtered[["name","sector","region","theme","weight","current_price","YTD","1M","6M","1Y","3Y"]].copy()
        display["weight"] = (display["weight"] * 100).round(2)
        display.columns = ["Name","Sector","Region","Theme","Weight %","Price",*list(TIMEFRAMES.keys())]

        def style_row(row):
            styles = [""] * len(row)
            for i, col in enumerate(row.index):
                if col in TIMEFRAMES:
                    val = row[col]
                    if isinstance(val, (int, float)) and not np.isnan(val):
                        styles[i] = "color: #2ecc71" if val >= 0 else "color: #e74c3c"
            return styles

        fmt_dict = {tf: lambda x: fmt_pct(x) for tf in TIMEFRAMES}
        fmt_dict["Weight %"] = "{:.3f}%".format
        fmt_dict["Price"] = lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A"

        styled = display.style.apply(style_row, axis=1).format(fmt_dict)
        st.dataframe(styled, use_container_width=True, height=600)

    # ── Tab 2: Bar chart — returns by ticker ──────────────────────────────────
    with tab2:
        st.subheader(f"Individual Stock Returns — {selected_tf}")
        grp_by = st.radio("Group by", ["None","Theme","Region","Sector"], horizontal=True)

        plot_df = df_filtered[["name","bb_ticker","region","theme","sector", selected_tf]].dropna(subset=[selected_tf])
        plot_df = plot_df.sort_values(selected_tf, ascending=True)

        color_col = {"None": "region","Theme":"theme","Region":"region","Sector":"sector"}[grp_by]

        fig = px.bar(
            plot_df, x=selected_tf, y="name",
            color=color_col,
            orientation="h",
            title=f"{selected_tf} Price Return (%)",
            labels={selected_tf: "Return (%)", "name": ""},
            color_discrete_sequence=px.colors.qualitative.Set2,
            height=max(500, len(plot_df) * 22),
        )
        fig.add_vline(x=0, line_dash="dash", line_color="white", line_width=1)
        fig.update_layout(
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font_color="white", legend_title_text=grp_by,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Tab 3: Allocation breakdown ───────────────────────────────────────────
    with tab3:
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("By Region")
            reg_df = PORTFOLIO_DF[mask].groupby("region")["weight"].sum().reset_index()
            fig_reg = px.pie(reg_df, names="region", values="weight",
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_reg.update_layout(paper_bgcolor="#0e1117", font_color="white")
            st.plotly_chart(fig_reg, use_container_width=True)

        with c2:
            st.subheader("By Theme")
            theme_df = PORTFOLIO_DF[mask].groupby("theme")["weight"].sum().reset_index()
            fig_theme = px.pie(theme_df, names="theme", values="weight",
                               color_discrete_sequence=px.colors.qualitative.Set2)
            fig_theme.update_layout(paper_bgcolor="#0e1117", font_color="white")
            st.plotly_chart(fig_theme, use_container_width=True)

        st.subheader("Return Heatmap by Theme × Timeframe")
        heat_rows = []
        for theme, grp in df_filtered.groupby("theme"):
            row = {"Theme": theme}
            for tf in TIMEFRAMES:
                vals = grp[tf].dropna()
                wts = grp.loc[grp[tf].notna(), "weight"]
                if len(vals) > 0 and wts.sum() > 0:
                    row[tf] = round((vals.values * (wts.values / wts.sum())).sum(), 2)
                else:
                    row[tf] = None
            heat_rows.append(row)
        heat_df = pd.DataFrame(heat_rows).set_index("Theme")

        fig_heat = go.Figure(data=go.Heatmap(
            z=heat_df.values,
            x=list(heat_df.columns),
            y=list(heat_df.index),
            colorscale=[
                [0.0, "#c0392b"], [0.4, "#2c2c2c"], [0.5, "#2c2c2c"], [1.0, "#27ae60"]
            ],
            zmid=0,
            text=[[fmt_pct(v) for v in row] for row in heat_df.values],
            texttemplate="%{text}",
        ))
        fig_heat.update_layout(
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font_color="white", height=400, margin=dict(l=10,r=10,t=20,b=10)
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # ── Tab 4: Historical Price Chart ─────────────────────────────────────────
    with tab4:
        st.subheader("Historical Price Performance")

        available = df_filtered[df_filtered["current_price"].notna()]["bb_ticker"].tolist()
        names_map = dict(zip(PORTFOLIO_DF["bb_ticker"], PORTFOLIO_DF["name"]))
        selected_stocks = st.multiselect(
            "Select tickers to compare",
            options=available,
            default=available[:5],
            format_func=lambda x: f"{names_map.get(x, x)} ({x})"
        )
        chart_tf = st.select_slider("Period", options=list(TIMEFRAMES.keys()), value="1Y")
        normalize = st.checkbox("Normalize to 100 (indexed)", value=True)

        if selected_stocks:
            t_start, t_end = TIMEFRAMES[chart_tf]
            fig_line = go.Figure()
            for bb in selected_stocks:
                if bb in price_data:
                    s = price_data[bb].loc[t_start:t_end].dropna()
                    if len(s) > 1:
                        y = (s / s.iloc[0] * 100) if normalize else s
                        fig_line.add_trace(go.Scatter(
                            x=s.index, y=y,
                            mode="lines", name=names_map.get(bb, bb),
                            line=dict(width=2)
                        ))
            fig_line.update_layout(
                paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                font_color="white", hovermode="x unified",
                yaxis_title="Indexed (100 = start)" if normalize else "Price",
                margin=dict(l=10, r=10, t=20, b=10), height=500,
                legend=dict(bgcolor="#1a1a2e")
            )
            if normalize:
                fig_line.add_hline(y=100, line_dash="dash", line_color="grey", line_width=1)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Select at least one ticker above.")

if __name__ == "__main__":
    main()
