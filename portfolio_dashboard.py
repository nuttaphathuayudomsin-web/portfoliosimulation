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
from datetime import datetime, timedelta, date
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Portfolio Dashboard", layout="wide", page_icon="📊")

# ── Ticker mapping (Bloomberg → Yahoo Finance) ──────────────────────────────
TICKER_MAP = {
    # US — Developed Markets
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
    # APAC — Japan (.T) & Korea (.KS)
    "6146 JP Equity":   "6146.T",
    "6857 JP Equity":   "6857.T",
    "4062 JP Equity":   "4062.T",
    "6383 JP Equity":   "6383.T",
    "000660 KS":        "000660.KS",
    "005930 KS":        "005930.KS",
    "9104 JP":          "9104.T",
    "7011 JP":          "7011.T",
    "7012 JP":          "7012.T",
    # Emerging Markets — China & HK
    "688041 CH Equity": "688041.SS",
    "603986 CH Equity": "603986.SS",
    "300476 CH Equity": "300476.SZ",
    "1772 HK Equity":   "1772.HK",
    "002353 CH":        "002353.SZ",
    # Commodities & Inflation hedge (ETFs)
    "GOLD":             "GLD",
    "SILVER":           "SLV",
    "OIL":              "USO",
}

# ── Portfolio structure (synced from Portfolio_Simulation.xlsx) ──────────────
# Format: (bb_ticker, display_name, weight, region, theme, sector)
PORTFOLIO = [
    # ── Developed Markets / US / Upstream AI ─────────────────────────────────
    ("LAM US Equity",   "Lam Research",             0.004615, "Developed Markets", "Upstream AI",      "Machine"),
    ("SNDK US Equity",  "Sandisk",                  0.004615, "Developed Markets", "Upstream AI",      "Memory"),
    ("MU US Equity",    "Micron Technology",        0.004615, "Developed Markets", "Upstream AI",      "Memory"),
    ("BDC US Equity",   "Belden Inc",               0.004615, "Developed Markets", "Upstream AI",      "Infrastructure - network"),
    ("APLD US Equity",  "Applied Digital Corp",     0.004615, "Developed Markets", "Upstream AI",      "Infrastructure - system"),
    ("MPWR US Equity",  "Monolithic Power Systems", 0.004615, "Developed Markets", "Upstream AI",      "Photooptic"),
    ("COHR US Equity",  "Coherent",                 0.004615, "Developed Markets", "Upstream AI",      "Photooptic"),
    ("TER US Equity",   "Teradyne Inc",             0.004615, "Developed Markets", "Upstream AI",      "Machine"),
    ("PWR US Equity",   "Quanta Services",          0.004615, "Developed Markets", "Upstream AI",      "Infrastructure - service"),
    ("CAT US Equity",   "Caterpillar Inc",          0.004615, "Developed Markets", "Upstream AI",      "Energy - AI"),
    ("ON US Equity",    "ON Semiconductor",         0.004615, "Developed Markets", "Upstream AI",      "Packaging"),
    ("ADI US Equity",   "Analog Devices",           0.004615, "Developed Markets", "Upstream AI",      "Packaging"),
    # ── Developed Markets / US / Defense ─────────────────────────────────────
    ("MOG/A US Equity", "Moog Inc",                 0.003333, "Developed Markets", "Defense",          "Sensors"),
    ("VSEC US Equity",  "VSE Corp",                 0.003333, "Developed Markets", "Defense",          "Components"),
    ("HII US Equity",   "Huntington Ingalls",       0.003333, "Developed Markets", "Defense",          "Ship building"),
    ("HXL US Equity",   "Hexcel Corp",              0.003333, "Developed Markets", "Defense",          "Components"),
    ("WWD US Equity",   "Woodward Inc",             0.003333, "Developed Markets", "Defense",          "Components"),
    ("HWM US Equity",   "Howmet Aerospace",         0.003333, "Developed Markets", "Defense",          "Components"),
    ("RTX US Equity",   "RTX Corporation",          0.003333, "Developed Markets", "Defense",          "Drone"),
    ("LMT US Equity",   "Lockheed Martin",          0.003333, "Developed Markets", "Defense",          "Aircraft"),
    ("NOC US Equity",   "Northrop Grumman",         0.003333, "Developed Markets", "Defense",          "Aircraft"),
    # ── Developed Markets / US / Energy ──────────────────────────────────────
    ("OXY",             "Occidental Petroleum",     0.006,    "Developed Markets", "Energy",           "Oil field"),
    ("CVX",             "Chevron",                  0.006,    "Developed Markets", "Energy",           "Integrated"),
    ("XOM",             "Exxon Mobil",              0.006,    "Developed Markets", "Energy",           "Integrated"),
    ("SLB",             "Schlumberger",             0.006,    "Developed Markets", "Energy",           "Oil field"),
    ("BE US Equity",    "Bloom Energy",             0.006,    "Developed Markets", "Energy",           "Hydrogen"),
    # ── Developed Markets / US / Inflation-linked ─────────────────────────────
    ("WMT",             "Walmart Inc",              0.003,    "Developed Markets", "Inflation-linked", "Discount store"),
    ("COST",            "Costco",                   0.003,    "Developed Markets", "Inflation-linked", "Big box"),
    ("DG",              "Dollar General",           0.003,    "Developed Markets", "Inflation-linked", "Discount store"),
    ("PG",              "P&G",                      0.003,    "Developed Markets", "Inflation-linked", "Household"),
    ("CL",              "Colgate",                  0.003,    "Developed Markets", "Inflation-linked", "Household"),
    # ── APAC / Upstream AI (JP + KR) ─────────────────────────────────────────
    ("6146 JP Equity",  "Disco Corp",               0.000833, "APAC",             "Upstream AI",      "Machine"),
    ("6857 JP Equity",  "Advantest Corp",           0.000833, "APAC",             "Upstream AI",      "Machine"),
    ("4062 JP Equity",  "Ibiden Co Ltd",            0.000833, "APAC",             "Upstream AI",      "Machine"),
    ("6383 JP Equity",  "Daifuku Co Ltd",           0.000833, "APAC",             "Upstream AI",      "Automation"),
    ("000660 KS",       "SK Hynix",                 0.000833, "APAC",             "Upstream AI",      "Foundry"),
    ("005930 KS",       "Samsung Electronics",      0.000833, "APAC",             "Upstream AI",      "Foundry"),
    # ── APAC / Energy ────────────────────────────────────────────────────────
    ("9104 JP",         "Mitsui OSK Lines",         0.005,    "APAC",             "Energy",           "Tanker"),
    # ── APAC / Defense ───────────────────────────────────────────────────────
    ("7011 JP",         "Mitsubishi Heavy",         0.0025,   "APAC",             "Defense",          "Aircraft, Turbine"),
    ("7012 JP",         "Kawasaki Heavy",           0.0025,   "APAC",             "Defense",          "Aircraft, Turbine"),
    # ── Emerging Markets / Upstream AI ───────────────────────────────────────
    ("688041 CH Equity","Hygon Information Tech",   0.025,    "Emerging Markets", "Upstream AI",      "Chips"),
    ("603986 CH Equity","GigaDevice",               0.025,    "Emerging Markets", "Upstream AI",      "Chips"),
    ("300476 CH Equity","Victory Giant",            0.025,    "Emerging Markets", "Upstream AI",      "PCB"),
    # ── Emerging Markets / Precious Metal ────────────────────────────────────
    ("1772 HK Equity",  "Ganfeng Lithium",          0.0375,   "Emerging Markets", "Precious Metal",   "Mining"),
    # ── Emerging Markets / Energy ─────────────────────────────────────────────
    ("002353 CH",       "Yangtai Jereh Oilfield",   0.0375,   "Emerging Markets", "Energy",           "Energy"),
    # ── Inflation-hedged ─────────────────────────────────────────────────────
    ("GOLD",            "Gold (GLD ETF)",           0.025,    "Inflation-hedged", "Precious Metal",   "Gold"),
    ("SILVER",          "Silver (SLV ETF)",         0.025,    "Inflation-hedged", "Precious Metal",   "Silver"),
    # ── Commodity ────────────────────────────────────────────────────────────
    ("OIL",             "Oil (USO ETF)",            0.05,     "Commodity",        "Commodity",        "Oil"),
]

PORTFOLIO_DF = pd.DataFrame(PORTFOLIO, columns=["bb_ticker","name","weight","region","theme","sector"])

TODAY = date(2026, 3, 3)
TFS   = ["Since Entry", "YTD", "1M", "3M", "6M", "1Y", "3Y"]

# ── Data fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_all_prices() -> dict:
    result = {}
    fetch_start = datetime(2022, 1, 1)
    for bb, yf_ticker in TICKER_MAP.items():
        try:
            data = yf.download(yf_ticker, start=fetch_start, progress=False, auto_adjust=True)
            if not data.empty:
                result[bb] = data["Close"].squeeze()
        except Exception:
            pass
    return result

def get_price_on(series: pd.Series, target: date) -> float | None:
    try:
        dt = pd.Timestamp(target)
        s = series[series.index <= dt].dropna()
        return float(s.iloc[-1]) if not s.empty else None
    except Exception:
        return None

def calc_tf_return(series: pd.Series, tf: str, entry_date: date, today: date) -> float | None:
    """
    Each timeframe is measured backwards from today.
    If entry_date falls AFTER the tf window start, we use entry_date instead
    (you can't have returns before you entered).
    """
    tf_start_map = {
        "Since Entry": entry_date,
        "YTD":         date(today.year, 1, 1),
        "1M":          today - timedelta(days=30),
        "3M":          today - timedelta(days=91),
        "6M":          today - timedelta(days=182),
        "1Y":          today - timedelta(days=365),
        "3Y":          today - timedelta(days=1095),
    }
    window_start    = tf_start_map[tf]
    effective_start = max(window_start, entry_date)
    p_start = get_price_on(series, effective_start)
    p_end   = get_price_on(series, today)
    if p_start is None or p_end is None or p_start == 0:
        return None
    return (p_end / p_start - 1) * 100

def build_returns_table(price_data: dict, entry_date: date) -> pd.DataFrame:
    rows = []
    for _, row in PORTFOLIO_DF.iterrows():
        bb = row["bb_ticker"]
        rec = {k: row[k] for k in ["bb_ticker","name","weight","region","theme","sector"]}
        if bb in price_data:
            s = price_data[bb]
            rec["entry_price"]   = get_price_on(s, entry_date)
            rec["current_price"] = get_price_on(s, TODAY)
            for tf in TFS:
                rec[tf] = calc_tf_return(s, tf, entry_date, TODAY)
        else:
            rec["entry_price"]   = None
            rec["current_price"] = None
            for tf in TFS:
                rec[tf] = None
        rows.append(rec)
    return pd.DataFrame(rows)

def weighted_return(df: pd.DataFrame, tf: str) -> float | None:
    valid = df[df[tf].notna()].copy()
    if valid.empty:
        return None
    total_w = valid["weight"].sum()
    return (valid[tf] * valid["weight"] / total_w).sum() if total_w > 0 else None

def fmt_pct(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    return f"{val:+.1f}%"

# ── Main app ──────────────────────────────────────────────────────────────────
def main():
    st.markdown("""
        <h1 style='margin-bottom:0'>📊 Portfolio Simulation Dashboard</h1>
        <p style='color:grey;margin-top:4px'>Live data · Yahoo Finance · ~15 min delay</p>
    """, unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Settings")

        # Business-day date list from 2022 to today
        bdays   = [d.date() for d in pd.date_range(date(2022, 1, 1), TODAY, freq="B")]
        def_idx = len(bdays) - 1  # default = TODAY (Mar 3 2026)

        st.markdown("**📅 Portfolio Entry Date**")
        picker_mode = st.radio("Input mode", ["📅 Calendar", "🎚️ Slider"], horizontal=True)

        if picker_mode == "📅 Calendar":
            entry_date = st.date_input(
                "Pick entry date",
                value=TODAY,
                min_value=date(2022, 1, 1),
                max_value=TODAY,
                format="DD/MM/YYYY",
            )
            # Snap to nearest business day if weekend selected
            ts = pd.Timestamp(entry_date)
            if ts.weekday() >= 5:  # Saturday=5, Sunday=6
                entry_date = (ts - pd.offsets.BDay(1)).date()
                st.caption(f"⚠️ Weekend selected — snapped to {entry_date.strftime('%d %b %Y')}")
        else:
            entry_idx  = st.select_slider(
                "Slide to set entry point",
                options=range(len(bdays)),
                value=def_idx,
                format_func=lambda i: bdays[i].strftime("%d %b %Y"),
            )
            entry_date = bdays[entry_idx]

        days_held  = (TODAY - entry_date).days
        st.success(f"Entry: **{entry_date.strftime('%d %b %Y')}**  \nToday: **{TODAY.strftime('%d %b %Y')}**  \nHeld: **{days_held} days**")

        st.divider()
        sel_regions = st.multiselect("Region", PORTFOLIO_DF["region"].unique().tolist(),
                                     default=PORTFOLIO_DF["region"].unique().tolist())
        sel_themes  = st.multiselect("Theme",  PORTFOLIO_DF["theme"].unique().tolist(),
                                     default=PORTFOLIO_DF["theme"].unique().tolist())
        st.divider()
        if st.button("🔄 Refresh Prices", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.caption(f"Cached: {datetime.now().strftime('%d %b %Y %H:%M')}")

        st.divider()
        with st.expander("➕ How to add stocks"):
            st.markdown("""
**Step 1 — Add to `TICKER_MAP`** (top of the file)
```python
"NVDA US Equity": "NVDA",
"7203 JP Equity": "7203.T",
"005930 KS":      "005930.KS",
```
Yahoo Finance suffixes by market:
- 🇺🇸 US → no suffix (`AAPL`, `LRCX`)
- 🇯🇵 JP → `.T` (`6857.T`)
- 🇰🇷 KR → `.KS` (`005930.KS`)
- 🇭🇰 HK → `.HK` (`1772.HK`)
- 🇨🇳 CN Shanghai → `.SS`
- 🇨🇳 CN Shenzhen → `.SZ`

**Step 2 — Add to `PORTFOLIO`** (below TICKER_MAP)
```python
("NVDA US Equity", "Nvidia",
  0.01,                # weight (1%)
  "Developed Markets", # region
  "Upstream AI",       # theme
  "Chips"),            # sector
```
⚠️ Keep total weights summed to **1.0** (100%)
            """)

    # ── Load data ─────────────────────────────────────────────────────────────
    with st.spinner("Pulling prices from Yahoo Finance..."):
        price_data = fetch_all_prices()
        df         = build_returns_table(price_data, entry_date)

    mask = df["region"].isin(sel_regions) & df["theme"].isin(sel_themes)
    df_f = df[mask].copy()

    n_loaded = df_f["current_price"].notna().sum()
    st.caption(f"✅ {n_loaded} / {len(df_f)} tickers loaded  ·  Entry date: {entry_date.strftime('%d %b %Y')}")

    # ── Portfolio KPI strip (weighted) ─────────────────────────────────────────
    st.divider()
    kpi_cols = st.columns(len(TFS))
    for col, tf in zip(kpi_cols, TFS):
        val = weighted_return(df_f, tf)
        if val is not None:
            col.metric(f"Portfolio {tf}", f"{val:+.1f}%",
                       delta="weighted", delta_color="normal" if val >= 0 else "inverse")
        else:
            col.metric(f"Portfolio {tf}", "N/A")

    st.caption("All portfolio returns are **weight-adjusted** across tickers with available data.")
    st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Holdings Table", "📈 Stock Returns", "🧩 Allocation & Heatmap", "📉 Price Chart"
    ])

    # Tab 1 ── Holdings table ──────────────────────────────────────────────────
    with tab1:
        st.subheader(f"Holdings  ·  Entry {entry_date.strftime('%d %b %Y')} → {TODAY.strftime('%d %b %Y')}")

        disp = df_f[["name","sector","region","theme","weight","entry_price","current_price"] + TFS].copy()
        disp["weight"] = disp["weight"] * 100
        disp.columns   = ["Name","Sector","Region","Theme","Weight %","Entry Price","Current Price"] + TFS

        def _style(row):
            out = [""] * len(row)
            for i, c in enumerate(row.index):
                if c in TFS:
                    v = row[c]
                    if isinstance(v, (int, float)) and not np.isnan(v):
                        out[i] = "color:#2ecc71;font-weight:bold" if v >= 0 else "color:#e74c3c;font-weight:bold"
            return out

        fmt = {tf: fmt_pct for tf in TFS}
        fmt["Weight %"]      = "{:.3f}%".format
        fmt["Entry Price"]   = lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A"
        fmt["Current Price"] = lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A"

        st.dataframe(disp.style.apply(_style, axis=1).format(fmt),
                     use_container_width=True, height=650)

    # Tab 2 ── Bar chart ───────────────────────────────────────────────────────
    with tab2:
        st.subheader("Individual Stock Returns")
        c1, c2 = st.columns([1, 4])
        with c1:
            sel_tf  = st.selectbox("Timeframe", TFS, index=0)
            clr_by  = st.radio("Color by", ["Theme","Region","Sector"], index=0)
        clr_col  = {"Theme":"theme","Region":"region","Sector":"sector"}[clr_by]
        plot_df  = df_f[["name","region","theme","sector", sel_tf]].dropna(subset=[sel_tf])
        plot_df  = plot_df.sort_values(sel_tf, ascending=True)
        port_ret = weighted_return(df_f, sel_tf)

        with c2:
            fig = px.bar(plot_df, x=sel_tf, y="name", color=clr_col, orientation="h",
                         title=f"{sel_tf} Return (%)  ·  Portfolio (weighted): {fmt_pct(port_ret)}",
                         labels={sel_tf:"Return (%)", "name":""},
                         color_discrete_sequence=px.colors.qualitative.Set2,
                         height=max(500, len(plot_df)*22))
            fig.add_vline(x=0, line_dash="dash", line_color="white", line_width=1)
            if port_ret is not None:
                fig.add_vline(x=port_ret, line_dash="dot", line_color="#f39c12", line_width=2,
                              annotation_text=f"Portfolio {fmt_pct(port_ret)}",
                              annotation_font_color="#f39c12")
            fig.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                              font_color="white", margin=dict(l=10,r=40,t=40,b=10))
            st.plotly_chart(fig, use_container_width=True)

    # Tab 3 ── Allocation & Heatmap ────────────────────────────────────────────
    with tab3:
        pm = PORTFOLIO_DF["region"].isin(sel_regions) & PORTFOLIO_DF["theme"].isin(sel_themes)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("By Region")
            rdf = PORTFOLIO_DF[pm].groupby("region")["weight"].sum().reset_index()
            fig_r = px.pie(rdf, names="region", values="weight",
                           color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_r.update_layout(paper_bgcolor="#0e1117", font_color="white")
            st.plotly_chart(fig_r, use_container_width=True)
        with c2:
            st.subheader("By Theme")
            tdf = PORTFOLIO_DF[pm].groupby("theme")["weight"].sum().reset_index()
            fig_t = px.pie(tdf, names="theme", values="weight",
                           color_discrete_sequence=px.colors.qualitative.Set2)
            fig_t.update_layout(paper_bgcolor="#0e1117", font_color="white")
            st.plotly_chart(fig_t, use_container_width=True)

        st.subheader("Weighted Return Heatmap — Theme × Timeframe")
        heat_rows = []
        for theme, grp in df_f.groupby("theme"):
            row = {"Theme": theme}
            for tf in TFS:
                wr = weighted_return(grp, tf)
                row[tf] = round(wr, 2) if wr is not None else np.nan
            heat_rows.append(row)
        hdf = pd.DataFrame(heat_rows).set_index("Theme")

        fig_h = go.Figure(go.Heatmap(
            z=hdf.values.astype(float),
            x=list(hdf.columns), y=list(hdf.index),
            colorscale=[[0,"#c0392b"],[0.45,"#2c2c2c"],[0.55,"#2c2c2c"],[1,"#27ae60"]],
            zmid=0,
            text=[[fmt_pct(v) for v in r] for r in hdf.values],
            texttemplate="%{text}",
        ))
        fig_h.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                            font_color="white", height=420, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig_h, use_container_width=True)

    # Tab 4 ── Price Chart ─────────────────────────────────────────────────────
    with tab4:
        st.subheader("Historical Price Chart")
        names_map = dict(zip(PORTFOLIO_DF["bb_ticker"], PORTFOLIO_DF["name"]))
        available = df_f[df_f["current_price"].notna()]["bb_ticker"].tolist()

        ca, cb = st.columns([3,1])
        with ca:
            sel_stocks = st.multiselect(
                "Select tickers to plot",
                options=available, default=available[:6],
                format_func=lambda x: f"{names_map.get(x,x)} ({x})"
            )
        with cb:
            normalize     = st.checkbox("Index to 100 at entry", value=True)
            show_port_line = st.checkbox("Show portfolio line", value=True)

        if sel_stocks:
            entry_ts = pd.Timestamp(entry_date)
            today_ts = pd.Timestamp(TODAY)
            fig_l    = go.Figure()

            for bb in sel_stocks:
                if bb in price_data:
                    s = price_data[bb].loc[entry_ts:today_ts].dropna()
                    if len(s) > 1:
                        y = (s / s.iloc[0] * 100) if normalize else s
                        fig_l.add_trace(go.Scatter(x=s.index, y=y, mode="lines",
                                                   name=names_map.get(bb,bb),
                                                   line=dict(width=1.5), opacity=0.75))

            # Weighted portfolio composite
            if show_port_line and normalize:
                pm2 = PORTFOLIO_DF["region"].isin(sel_regions) & PORTFOLIO_DF["theme"].isin(sel_themes)
                weighted_parts = []
                for _, r in PORTFOLIO_DF[pm2].iterrows():
                    if r["bb_ticker"] in price_data:
                        s = price_data[r["bb_ticker"]].loc[entry_ts:today_ts].dropna()
                        if len(s) > 1:
                            weighted_parts.append((s / s.iloc[0]) * r["weight"])
                if weighted_parts:
                    combined = pd.concat(weighted_parts, axis=1).ffill().sum(axis=1)
                    tot_w    = PORTFOLIO_DF[pm2]["weight"].sum()
                    port_idx = combined / tot_w * 100
                    fig_l.add_trace(go.Scatter(x=port_idx.index, y=port_idx,
                                               mode="lines", name="📊 Portfolio (weighted)",
                                               line=dict(width=3, color="#f39c12", dash="dash")))

            if normalize:
                fig_l.add_hline(y=100, line_dash="dash", line_color="grey", line_width=1)
            fig_l.update_layout(
                paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font_color="white",
                hovermode="x unified",
                yaxis_title="Indexed to 100 at entry" if normalize else "Price",
                xaxis_title="Date",
                height=520, margin=dict(l=10,r=10,t=20,b=10),
                legend=dict(bgcolor="#1a1a2e", bordercolor="#444", borderwidth=1)
            )
            st.plotly_chart(fig_l, use_container_width=True)
        else:
            st.info("Select at least one ticker above.")

if __name__ == "__main__":
    main()
