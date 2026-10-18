"""StockSense - Smart Stock Management (Streamlit)."""
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import core

st.set_page_config(page_title="StockSense | Smart Stock Management", page_icon="📦",
                   layout="wide", initial_sidebar_state="expanded")

BLUE, PURPLE, GREEN, ORANGE, CYAN, RED, AMBER = "#2F6BFF", "#8B5CF6", "#12B886", "#FF8A3D", "#38BDF8", "#F0475B", "#F5B301"
PALETTE = [BLUE, PURPLE, GREEN, ORANGE, CYAN, "#EC4899", "#14B8A6"]
STATUS_COLORS = core.COLORS
INR = lambda v: f"₹{v:,.0f}"

# ------------------------------------------------------------------ styling
CSS = """
<style>
#MainMenu, footer, [data-testid="stToolbar"] {visibility: hidden;}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stAppViewContainer"] {background: #0A1128;}
.block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px;}
[data-testid="stSidebar"] {background: #0B1330; border-right: 1px solid #16224A;}
[data-testid="stSidebar"] > div:first-child {padding-top: 1rem;}
h1, h2, h3, h4 {color: #F2F5FF; letter-spacing: -0.01em;}

/* bordered containers = cards */
[data-testid="stVerticalBlockBorderWrapper"] {background: #0F1A3C; border: 1px solid #1E2B55 !important; border-radius: 14px;}

/* sidebar navigation */
[data-testid="stSidebar"] div[role="radiogroup"] {gap: 6px;}
[data-testid="stSidebar"] div[role="radiogroup"] > label {background: transparent; padding: 11px 14px; border-radius: 10px; width: 100%; cursor: pointer; transition: background .15s;}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {background: #15214A;}
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {display: none;}
[data-testid="stSidebar"] div[role="radiogroup"] > label p {font-size: 15px; font-weight: 500; color: #B8C4EA;}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {background: #2F6BFF;}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {color: #fff; font-weight: 600;}

.brand {display:flex; align-items:center; gap:12px; padding: 4px 6px 18px 6px;}
.brand .logo {width:42px; height:42px; border-radius:11px; background: linear-gradient(135deg,#2F6BFF,#38BDF8); display:flex; align-items:center; justify-content:center; font-size:22px;}
.brand .t1 {font-size:22px; font-weight:700; color:#fff; line-height:1.1;} .brand .t1 span {color:#2F6BFF;}
.brand .t2 {font-size:12px; color:#8FA0D0;}
.help {background:#0F1A3C; border:1px solid #1E2B55; border-radius:12px; padding:14px; color:#8FA0D0; font-size:13px; margin-top:18px;}
.help b {color:#E8EEFF;}

/* header */
.hello {font-size:30px; font-weight:700; color:#fff; margin:0;} .sub {color:#9AA8D4; margin-top:2px; font-size:15px;}
.datepill {float:right; background:#0F1A3C; border:1px solid #1E2B55; border-radius:10px; padding:9px 16px; color:#DCE4FF; font-size:14px;}

/* KPI cards */
.kpi {background:#0F1A3C; border:1px solid #1E2B55; border-radius:14px; padding:18px 20px; height:100%;}
.kpi .ic {width:46px; height:46px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:21px; margin-bottom:12px;}
.kpi .lab {color:#DCE4FF; font-size:15px; font-weight:500;}
.kpi .val {color:#fff; font-size:32px; font-weight:700; margin:4px 0 2px 0;}
.kpi .cap {font-size:13px; color:#8FA0D0;}

.card-title {font-size:17px; font-weight:600; color:#F2F5FF; margin: 2px 0 10px 0;}

/* html tables */
table.t {width:100%; border-collapse:collapse; font-size:14px;}
table.t th {text-align:left; color:#8FA0D0; font-weight:500; padding:8px 10px; border-bottom:1px solid #1E2B55; font-size:13px;}
table.t td {padding:10px; border-bottom:1px solid #16224A; color:#E8EEFF;}
table.t td.n {text-align:right;} table.t th.n {text-align:right;}
.stk {color:#fff; text-decoration: underline; text-decoration-color:#2F6BFF;} .rl {color:#F0475B; text-decoration: underline;}

/* pills & alert rows */
.pill {display:inline-block; padding:3px 10px; border-radius:6px; font-size:12px; font-weight:700;}
.p-REORDER {background:rgba(240,71,91,.18); color:#FF6B7D;} .p-LOW {background:rgba(245,179,1,.18); color:#F5B301;} .p-IN {background:rgba(18,184,134,.18); color:#2DD4A0;}
.p-CRITICAL {background:#F0475B; color:#fff;} .p-HIGH {background:rgba(240,71,91,.18); color:#FF6B7D;} .p-MEDIUM {background:rgba(245,179,1,.18); color:#F5B301;}
.al {display:flex; gap:12px; align-items:center; padding:10px 0; border-bottom:1px solid #16224A;}
.al:last-child {border-bottom:none;}
.al .ico {width:36px; height:36px; border-radius:9px; display:flex; align-items:center; justify-content:center; font-size:17px; flex-shrink:0;}
.al .nm {color:#fff; font-weight:600; font-size:14px;} .al .ds {color:#8FA0D0; font-size:12.5px;}
.al .tm {margin-left:auto; color:#8FA0D0; font-size:12px; white-space:nowrap;}
.legend-row {display:flex; align-items:center; justify-content:space-between; padding:9px 0; color:#E8EEFF; font-size:15px;}
.dot {display:inline-block; width:11px; height:11px; border-radius:50%; margin-right:10px;}

.stButton > button, .stDownloadButton > button {border-radius:10px; font-weight:600; border:1px solid #2F6BFF;}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {background:#2F6BFF; color:#fff;}
[data-testid="stDataFrame"] {border-radius:10px;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def html(s: str) -> None:
    st.markdown(" ".join(line.strip() for line in s.strip().splitlines()), unsafe_allow_html=True)


def style_fig(fig, h=300, legend=True):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#C9D4F5", size=12), height=h, margin=dict(l=10, r=10, t=10, b=10),
                      showlegend=legend, legend=dict(bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(gridcolor="#1B2750", zeroline=False)
    fig.update_yaxes(gridcolor="#1B2750", zeroline=False)
    return fig


def pill(status: str) -> str:
    key = {"REORDER NOW": "REORDER", "LOW STOCK": "LOW", "IN STOCK": "IN"}.get(status, status)
    return f'<span class="pill p-{key}">{status}</span>'


# --------------------------------------------------------------------- data
settings = core.load_settings()
sup = core.load_suppliers()
inv = core.load_inventory()
data = core.enrich(inv, sup, settings)

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    html("""<div class="brand"><div class="logo">📦</div><div><div class="t1">Stock<span>Sense</span></div>
    <div class="t2">Smart Stock Management</div></div></div>""")
    n_alerts = int((data["Status"] != "IN STOCK").sum())
    pages = ["🏠  Dashboard", "📦  Inventory", f"🔔  Alerts ({n_alerts})", "🚚  Suppliers",
             "📊  Analytics", "📑  Reports", "⚙️  Settings"]
    choice = st.radio("Navigate", pages, label_visibility="collapsed")
    page = choice.split("  ")[1].split(" (")[0]

    st.markdown("---")
    st.markdown("**Filters** (apply to every page)")
    f_store = st.multiselect("Store", sorted(data["Store ID"].unique()))
    f_cat = st.multiselect("Category", sorted(data["Category"].unique()))
    f_reg = st.multiselect("Region", sorted(data["Region"].unique()))
    f_status = st.multiselect("Stock status", core.STATUS_ORDER)
    f_search = st.text_input("Search", placeholder="Product ID, store, supplier...")
    html("""<div class="help"><b>Need help?</b><br>For any support, contact the system administrator.</div>""")

view = data.copy()
if f_store: view = view[view["Store ID"].isin(f_store)]
if f_cat: view = view[view["Category"].isin(f_cat)]
if f_reg: view = view[view["Region"].isin(f_reg)]
if f_status: view = view[view["Status"].isin(f_status)]
if f_search:
    q = f_search.lower()
    mask = view[["SKU", "Category", "Region", "Supplier", "Status"]].astype(str).apply(
        lambda c: c.str.lower().str.contains(q, regex=False)).any(axis=1)
    view = view[mask]
active_filters = bool(f_store or f_cat or f_reg or f_status or f_search)

K = core.kpis(view)


def greeting() -> str:
    h = datetime.now().hour
    return "Good Morning" if h < 12 else "Good Afternoon" if h < 17 else "Good Evening"


def header(title=None, subtitle=None):
    if title is None:
        title = f"{greeting()}, {settings['user_name']}!"
        subtitle = "Here's what's happening with your inventory today."
    html(f"""<div class="datepill">📅 {datetime.now():%B %d, %Y}</div>
    <div class="hello">{title}</div><div class="sub">{subtitle}</div>""")
    if active_filters:
        st.caption(f"Filters active - showing {len(view)} of {len(data)} items.")
    st.write("")


def kpi_card(col, icon, bg, label, value, caption):
    with col:
        html(f"""<div class="kpi"><div class="ic" style="background:{bg}33;">{icon}</div>
        <div class="lab">{label}</div><div class="val">{value}</div><div class="cap">{caption}</div></div>""")


def pct(a, b): return f"{(a / b * 100):.0f}% of products" if b else "-"


def no_data():
    st.info("No items match the current filters. Clear the filters in the sidebar.")


# ---------------------------------------------------------------- DASHBOARD
def page_dashboard():
    header()
    c = st.columns(5)
    kpi_card(c[0], "📦", BLUE, "Total Products", f"{K['products']:,}", f"{view['Category'].nunique()} categories, {view['Store ID'].nunique()} stores")
    kpi_card(c[1], "🗂️", GREEN, "Total Stock Units", f"{K['units']:,}", "units on hand")
    kpi_card(c[2], "🚨", RED, "Reorder Required", K["reorder"], f"{K['critical']} critical - " + pct(K["reorder"], K["products"]))
    kpi_card(c[3], "⚠️", AMBER, "Low Stock", K["low"], pct(K["low"], K["products"]))
    kpi_card(c[4], "₹", PURPLE, "Total Inventory Value", INR(K["value"]), f"reorder cost {INR(K['reorder_cost'])}")
    st.write("")
    if view.empty:
        return no_data()

    r1 = st.columns([1.15, 1.25, 1.1])
    with r1[0].container(border=True):
        st.markdown('<div class="card-title">Stock Status Overview</div>', unsafe_allow_html=True)
        cnt = view["Status"].value_counts().reindex(core.STATUS_ORDER).fillna(0).astype(int)
        a, b = st.columns([1.2, 1])
        fig = go.Figure(go.Pie(labels=cnt.index, values=cnt.values, hole=0.62, sort=False,
                               marker=dict(colors=[STATUS_COLORS[s] for s in cnt.index], line=dict(color="#0F1A3C", width=2)),
                               textinfo="percent", textfont=dict(size=12)))
        fig.add_annotation(text=f"<b>{len(view)}</b><br>Products", showarrow=False, font=dict(size=20, color="#fff"))
        a.plotly_chart(style_fig(fig, 260, False), use_container_width=True, config={"displayModeBar": False})
        rows = "".join(f'<div class="legend-row"><span><span class="dot" style="background:{STATUS_COLORS[s]}"></span>{s.title()}</span><b>{cnt[s]}</b></div>'
                       for s in ["IN STOCK", "LOW STOCK", "REORDER NOW"])
        with b:
            html(f'<div style="padding-top:34px">{rows}</div>')

    with r1[1].container(border=True):
        st.markdown('<div class="card-title">Top 5 Low Stock Products</div>', unsafe_allow_html=True)
        top = core.alerts_only(view).head(5)
        if top.empty:
            st.success("No low stock items.")
        else:
            body = "".join(f'<tr><td>{r["SKU"]} <span style="color:#8FA0D0;font-size:12px">({r["Category"]})</span></td><td class="n"><span class="stk">{r["Current Stock"]}</span></td><td class="n"><span class="rl">{r["Reorder Level"]}</span></td></tr>'
                           for _, r in top.iterrows())
            html(f'<table class="t"><tr><th>Product</th><th class="n">Current Stock</th><th class="n">Reorder Level</th></tr>{body}</table>')

    with r1[2].container(border=True):
        st.markdown('<div class="card-title">Recent Alerts</div>', unsafe_allow_html=True)
        top = core.alerts_only(view).head(5)
        if top.empty:
            st.success("All good - no alerts.")
        else:
            items = ""
            for r in top.itertuples():
                crit = r.Priority in ("CRITICAL", "HIGH")
                bg, ic = ("rgba(240,71,91,.2)", "🔺") if crit else ("rgba(245,179,1,.2)", "⚠️")
                desc = "Stock below reorder level" if r.Status == "REORDER NOW" else "Low stock warning"
                items += f'<div class="al"><div class="ico" style="background:{bg}">{ic}</div><div><div class="nm">{r.SKU} - {r.Category}</div><div class="ds">{desc}</div></div><div class="tm">{pill(r.Priority)}</div></div>'
            html(items)

    r2 = st.columns([1, 1, 1.2])
    with r2[0].container(border=True):
        st.markdown('<div class="card-title">Inventory Value by Category</div>', unsafe_allow_html=True)
        g = view.groupby("Category", as_index=False)["Stock Value"].sum().sort_values("Stock Value", ascending=False)
        fig = px.bar(g, x="Category", y="Stock Value", color="Category", color_discrete_sequence=PALETTE)
        fig.update_traces(hovertemplate="%{x}: ₹%{y:,.0f}<extra></extra>")
        st.plotly_chart(style_fig(fig, 290, False), use_container_width=True, config={"displayModeBar": False})
    with r2[1].container(border=True):
        st.markdown('<div class="card-title">Stock Distribution by Store</div>', unsafe_allow_html=True)
        g = view.groupby("Store ID", as_index=False)["Current Stock"].sum()
        fig = px.pie(g, names="Store ID", values="Current Stock", color_discrete_sequence=PALETTE)
        fig.update_traces(textinfo="percent", marker=dict(line=dict(color="#0F1A3C", width=2)))
        fig.update_layout(legend=dict(orientation="v", x=1.0, y=0.5))
        st.plotly_chart(style_fig(fig, 290, True), use_container_width=True, config={"displayModeBar": False})
    with r2[2].container(border=True):
        st.markdown('<div class="card-title">Reorder Cost vs Inventory Value</div>', unsafe_allow_html=True)
        g = view.groupby("Category", as_index=False)[["Stock Value", "Reorder Cost"]].sum()
        fig = go.Figure()
        fig.add_bar(x=g["Category"], y=g["Stock Value"], name="Inventory Value", marker_color=BLUE)
        fig.add_bar(x=g["Category"], y=g["Reorder Cost"], name="Reorder Cost", marker_color=ORANGE)
        fig.update_layout(barmode="group", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(style_fig(fig, 290, True), use_container_width=True, config={"displayModeBar": False})

    with st.container(border=True):
        st.markdown('<div class="card-title">Inventory Details</div>', unsafe_allow_html=True)
        inventory_table(view, height=330)


def inventory_table(df, height=420):
    cols = ["SKU", "Category", "Store ID", "Region", "Current Stock", "Reorder Level", "Status",
            "Priority", "Days of Cover", "Supplier", "Unit Price", "Stock Value"]
    show = df.sort_values(["Status", "SKU"], key=lambda s: s.map({k: i for i, k in enumerate(core.STATUS_ORDER)}) if s.name == "Status" else s)[cols]
    def sc(v):
        return {"REORDER NOW": "background-color:rgba(240,71,91,.25);color:#FF8A98;font-weight:700",
                "LOW STOCK": "background-color:rgba(245,179,1,.22);color:#F5B301;font-weight:700",
                "IN STOCK": "background-color:rgba(18,184,134,.22);color:#2DD4A0;font-weight:700",
                "CRITICAL": "background-color:#F0475B;color:#fff;font-weight:700",
                "HIGH": "color:#FF8A98;font-weight:700", "MEDIUM": "color:#F5B301;font-weight:700"}.get(v, "")
    sty = show.style.map(sc, subset=["Status", "Priority"]).format(
        {"Unit Price": "₹{:,.2f}", "Stock Value": "₹{:,.0f}", "Days of Cover": "{:.1f}"}, na_rep="-")
    st.dataframe(sty, use_container_width=True, hide_index=True, height=height)
    st.caption(f"Showing {len(show)} of {len(data)} products")


# ---------------------------------------------------------------- INVENTORY
def page_inventory():
    header("Inventory", "Add products, update stock and edit records. Changes are saved instantly and alerts recalculate.")
    t1, t2, t3, t4, t5 = st.tabs(["📋 All items", "➕ Add product", "🔄 Update stock", "✏️ Edit / delete", "⬆️ Import"])
    with t1:
        if view.empty: no_data()
        else: inventory_table(view, 520)
    with t2:
        with st.form("add", clear_on_submit=True):
            a, b, c = st.columns(3)
            store = a.text_input("Store ID", placeholder="S006")
            pid = b.text_input("Product ID", placeholder="P0021")
            cat = c.selectbox("Category", sorted(set(data["Category"]) | set(sup["Category"])))
            d_, e, f_ = st.columns(3)
            reg = d_.selectbox("Region", sorted(data["Region"].unique()))
            stock = e.number_input("Current stock", 0, 10**7, 100)
            rl = f_.number_input("Reorder level", 0, 10**7, 50)
            g, h = st.columns(2)
            price = g.number_input("Unit price (₹)", 0.0, 1e7, 100.0, step=1.0)
            ads = h.number_input("Avg daily sales (units)", 0.0, 1e6, 5.0, step=0.5)
            if st.form_submit_button("Add product", type="primary"):
                sku = f"{store.strip().upper()}-{pid.strip().upper()}"
                if not store.strip() or not pid.strip():
                    st.error("Store ID and Product ID are required.")
                elif sku in set(data["SKU"]):
                    st.error(f"{sku} already exists. Use Update stock or Edit instead.")
                else:
                    new = pd.DataFrame([{"Store ID": store.strip().upper(), "Product ID": pid.strip().upper(), "Category": cat,
                                         "Region": reg, "Current Stock": stock, "Reorder Level": rl, "Unit Price": price,
                                         "Avg Daily Sales": ads, "Last Updated": datetime.now().strftime("%Y-%m-%d")}])
                    core.save_inventory(pd.concat([inv, new], ignore_index=True))
                    core.log_change(sku, "Added", 0, stock, "New product")
                    st.success(f"Added {sku}."); st.rerun()
    with t3:
        sku = st.selectbox("Select item", data["SKU"].tolist(), key="upd_sku")
        row = data[data["SKU"] == sku].iloc[0]
        a, b = st.columns([1, 2])
        with a:
            html(f'<div class="kpi"><div class="lab">{sku} - {row.Category}</div><div class="val">{row["Current Stock"]}</div><div class="cap">reorder level {row["Reorder Level"]}</div><div style="margin-top:8px">{pill(row.Status)}</div></div>')
        with b:
            mode = st.radio("Action", ["Stock received (+)", "Stock sold / issued (-)", "Set exact count"], horizontal=True)
            qty = st.number_input("Quantity", 0, 10**7, 0)
            note = st.text_input("Note (optional)")
            if st.button("Update stock", type="primary"):
                old = int(row["Current Stock"])
                new = old + qty if mode.startswith("Stock received") else max(0, old - qty) if mode.startswith("Stock sold") else qty
                m = (inv["Store ID"] + "-" + inv["Product ID"]) == sku
                inv.loc[m, "Current Stock"] = new
                inv.loc[m, "Last Updated"] = datetime.now().strftime("%Y-%m-%d")
                core.save_inventory(inv); core.log_change(sku, mode, old, new, note)
                st.success(f"{sku}: {old} -> {new}"); st.rerun()
    with t4:
        sku = st.selectbox("Select item", data["SKU"].tolist(), key="edit_sku")
        m = (inv["Store ID"] + "-" + inv["Product ID"]) == sku
        r = inv[m].iloc[0]
        with st.form("edit"):
            a, b, c = st.columns(3)
            cats = sorted(set(data["Category"]) | set(sup["Category"])); regs = sorted(data["Region"].unique())
            cat = a.selectbox("Category", cats, index=cats.index(r["Category"]))
            reg = b.selectbox("Region", regs, index=regs.index(r["Region"]))
            price = c.number_input("Unit price (₹)", 0.0, 1e7, float(r["Unit Price"]))
            d_, e, f_ = st.columns(3)
            stock = d_.number_input("Current stock", 0, 10**7, int(r["Current Stock"]))
            rl = e.number_input("Reorder level", 0, 10**7, int(r["Reorder Level"]))
            ads = f_.number_input("Avg daily sales", 0.0, 1e6, float(r["Avg Daily Sales"]), step=0.5)
            if st.form_submit_button("Save changes", type="primary"):
                old = int(r["Current Stock"])
                inv.loc[m, ["Category", "Region", "Unit Price", "Current Stock", "Reorder Level", "Avg Daily Sales", "Last Updated"]] = \
                    [cat, reg, price, stock, rl, ads, datetime.now().strftime("%Y-%m-%d")]
                core.save_inventory(inv)
                if stock != old: core.log_change(sku, "Edited", old, stock, "Edit form")
                st.success("Saved."); st.rerun()
        with st.expander("Delete this item"):
            ok = st.checkbox(f"Yes, permanently delete {sku}")
            if st.button("Delete item", disabled=not ok):
                core.save_inventory(inv[~m]); core.log_change(sku, "Deleted", int(r["Current Stock"]), 0, "")
                st.success("Deleted."); st.rerun()
    with t5:
        st.write("Upload a CSV or Excel file with columns: " + ", ".join(core.INV_COLS[:-1]) + ". Existing Store+Product rows are updated, new ones are added.")
        up = st.file_uploader("Choose file", type=["csv", "xlsx"])
        if up is not None:
            df = pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
            need = core.INV_COLS[:-1]
            if not set(need) <= set(df.columns):
                st.error("Missing columns: " + ", ".join(sorted(set(need) - set(df.columns))))
            else:
                st.dataframe(df.head(10), use_container_width=True, hide_index=True)
                if st.button("Merge into inventory", type="primary"):
                    df = df[need].copy(); df["Last Updated"] = datetime.now().strftime("%Y-%m-%d")
                    key = lambda x: x["Store ID"].astype(str) + "-" + x["Product ID"].astype(str)
                    merged = pd.concat([inv[~key(inv).isin(key(df))], df], ignore_index=True)
                    core.save_inventory(merged); st.success(f"Imported {len(df)} rows."); st.rerun()
    with st.expander("🕑 Stock activity log"):
        log = core.load_log()
        if len(log):
            st.dataframe(log.iloc[::-1], use_container_width=True, hide_index=True)
        else:
            st.caption("No changes yet.")


# ------------------------------------------------------------------- ALERTS
def page_alerts():
    header("Smart Alerts", "Automatic warnings when stock falls near or below the reorder level.")
    a = core.alerts_only(view)
    c = st.columns(4)
    kpi_card(c[0], "🛑", RED, "Critical", int((a["Priority"] == "CRITICAL").sum()), "will run out before delivery")
    kpi_card(c[1], "🚨", RED, "Reorder Now", int((a["Status"] == "REORDER NOW").sum()), "at or below reorder level")
    kpi_card(c[2], "⚠️", AMBER, "Low Stock", int((a["Status"] == "LOW STOCK").sum()), "inside buffer zone")
    kpi_card(c[3], "₹", PURPLE, "Est. Order Cost", INR(a["Reorder Cost"].sum()), f"{int(a['Suggested Qty'].sum()):,} units")
    st.write("")
    if a.empty:
        st.success("🎉 No active alerts for the current filters.")
        return
    pr = st.multiselect("Priority", ["CRITICAL", "HIGH", "MEDIUM"], default=["CRITICAL", "HIGH", "MEDIUM"])
    a = a[a["Priority"].isin(pr)]
    with st.container(border=True):
        st.markdown('<div class="card-title">Action list (most urgent first)</div>', unsafe_allow_html=True)
        body = "".join(f'<tr><td>{int(r["Alert Rank"])}</td><td><b>{r.SKU}</b><br><span style="color:#8FA0D0;font-size:12px">{r.Category} - {r.Region}</span></td>'
                       f'<td class="n">{r["Current Stock"]} / {r["Reorder Level"]}</td><td>{pill(r.Status)}</td><td>{pill(r.Priority)}</td>'
                       f'<td class="n">{r["Days of Cover"]:.1f} / {r["Lead Time"]}</td><td>{r.Supplier}</td><td class="n">{r["Suggested Qty"]:,}</td>'
                       f'<td class="n">{INR(r["Reorder Cost"])}</td><td>{r["Expected Delivery"]}</td><td>{r.Action}</td></tr>' for _, r in a.iterrows())
        html(f'<table class="t"><tr><th>#</th><th>Item</th><th class="n">Stock / Reorder</th><th>Status</th><th>Priority</th><th class="n">Cover / Lead (days)</th><th>Supplier</th><th class="n">Order Qty</th><th class="n">Cost</th><th>ETA</th><th>Action</th></tr>{body}</table>')
    with st.container(border=True):
        st.markdown('<div class="card-title">Draft purchase orders by supplier</div>', unsafe_allow_html=True)
        po = core.purchase_orders(view)
        st.dataframe(po.style.format({"Cost": "₹{:,.0f}"}), use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download purchase orders (CSV)", po.to_csv(index=False), "purchase_orders.csv", "text/csv")


# ---------------------------------------------------------------- SUPPLIERS
def page_suppliers():
    header("Suppliers", "Lead times drive days-of-cover alerts and expected delivery dates. Edit and save below.")
    with st.container(border=True):
        st.markdown('<div class="card-title">Supplier master (editable)</div>', unsafe_allow_html=True)
        ed = st.data_editor(sup, num_rows="dynamic", use_container_width=True, hide_index=True, key="sup_ed",
                            column_config={"Lead Time (Days)": st.column_config.NumberColumn(min_value=0, max_value=120, step=1),
                                           "Reliability (%)": st.column_config.NumberColumn(min_value=0, max_value=100)})
        if st.button("💾 Save suppliers", type="primary"):
            core.save_suppliers(ed.dropna(subset=["Supplier Name", "Category"])); st.success("Saved."); st.rerun()
    s = data.groupby("Supplier").agg(Items=("SKU", "count"), Alerts=("Status", lambda x: (x != "IN STOCK").sum()),
                                     Stock_Value=("Stock Value", "sum"), Reorder_Cost=("Reorder Cost", "sum")).reset_index()
    s.columns = ["Supplier", "Items supplied", "Active alerts", "Stock value", "Reorder cost"]
    with st.container(border=True):
        st.markdown('<div class="card-title">Supplier workload</div>', unsafe_allow_html=True)
        st.dataframe(s.style.format({"Stock value": "₹{:,.0f}", "Reorder cost": "₹{:,.0f}"}), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------- ANALYTICS
def page_analytics():
    header("Analytics", "Category-wise charts, reorder cost analysis and stock projections.")
    if view.empty: return no_data()
    t1, t2, t3, t4 = st.tabs(["Category", "Stores & Regions", "Reorder cost", "Stock trend & projection"])
    with t1:
        c = st.columns(2)
        with c[0].container(border=True):
            st.markdown('<div class="card-title">Status by category</div>', unsafe_allow_html=True)
            g = view.groupby(["Category", "Status"]).size().reset_index(name="Items")
            fig = px.bar(g, x="Category", y="Items", color="Status", color_discrete_map=STATUS_COLORS, category_orders={"Status": core.STATUS_ORDER})
            st.plotly_chart(style_fig(fig, 340), use_container_width=True, config={"displayModeBar": False})
        with c[1].container(border=True):
            st.markdown('<div class="card-title">Inventory value treemap</div>', unsafe_allow_html=True)
            fig = px.treemap(view, path=["Category", "Store ID"], values="Stock Value", color_discrete_sequence=PALETTE)
            st.plotly_chart(style_fig(fig, 340, False), use_container_width=True, config={"displayModeBar": False})
        with st.container(border=True):
            st.markdown('<div class="card-title">Current stock vs reorder level (each dot = one item)</div>', unsafe_allow_html=True)
            fig = px.scatter(view, x="Reorder Level", y="Current Stock", color="Status", color_discrete_map=STATUS_COLORS,
                             hover_data=["SKU", "Category"], category_orders={"Status": core.STATUS_ORDER})
            mx = max(view["Reorder Level"].max(), view["Current Stock"].max())
            fig.add_shape(type="line", x0=0, y0=0, x1=mx, y1=mx, line=dict(color="#8FA0D0", dash="dash"))
            st.plotly_chart(style_fig(fig, 360), use_container_width=True, config={"displayModeBar": False})
            st.caption("Dots on or below the dashed line are at or under their reorder level.")
    with t2:
        c = st.columns(2)
        with c[0].container(border=True):
            st.markdown('<div class="card-title">Alerts heatmap: store x category</div>', unsafe_allow_html=True)
            h = view[view["Status"] != "IN STOCK"].pivot_table(index="Store ID", columns="Category", values="SKU", aggfunc="count", fill_value=0)
            if h.empty:
                st.success("No alerts to plot.")
            else:
                fig = px.imshow(h, text_auto=True, color_continuous_scale=["#0F1A3C", "#F5B301", "#F0475B"], aspect="auto")
                st.plotly_chart(style_fig(fig, 340, False), use_container_width=True, config={"displayModeBar": False})
        with c[1].container(border=True):
            st.markdown('<div class="card-title">Stock units by region</div>', unsafe_allow_html=True)
            g = view.groupby("Region", as_index=False)["Current Stock"].sum()
            fig = px.bar(g, x="Region", y="Current Stock", color="Region", color_discrete_sequence=PALETTE)
            st.plotly_chart(style_fig(fig, 340, False), use_container_width=True, config={"displayModeBar": False})
    with t3:
        c = st.columns(2)
        with c[0].container(border=True):
            st.markdown('<div class="card-title">Reorder cost by supplier</div>', unsafe_allow_html=True)
            g = view.groupby("Supplier", as_index=False)["Reorder Cost"].sum().sort_values("Reorder Cost")
            fig = px.bar(g, x="Reorder Cost", y="Supplier", orientation="h", color_discrete_sequence=[ORANGE])
            st.plotly_chart(style_fig(fig, 340, False), use_container_width=True, config={"displayModeBar": False})
        with c[1].container(border=True):
            st.markdown('<div class="card-title">Reorder cost by priority</div>', unsafe_allow_html=True)
            g = view[view["Priority"] != "-"].groupby("Priority", as_index=False)["Reorder Cost"].sum()
            if g.empty:
                st.success("No reorder cost - nothing to order.")
            else:
                fig = px.pie(g, names="Priority", values="Reorder Cost", hole=0.55, color="Priority",
                             color_discrete_map={"CRITICAL": RED, "HIGH": "#FF8A3D", "MEDIUM": AMBER})
                st.plotly_chart(style_fig(fig, 340), use_container_width=True, config={"displayModeBar": False})
        with st.container(border=True):
            st.markdown('<div class="card-title">Days of cover distribution</div>', unsafe_allow_html=True)
            fig = px.histogram(view.dropna(subset=["Days of Cover"]), x="Days of Cover", nbins=25, color="Status",
                               color_discrete_map=STATUS_COLORS, category_orders={"Status": core.STATUS_ORDER})
            st.plotly_chart(style_fig(fig, 300), use_container_width=True, config={"displayModeBar": False})
    with t4:
        sku = st.selectbox("Item", view.sort_values("Alert Rank", na_position="last")["SKU"].tolist(), key="proj_sku")
        r = view[view["SKU"] == sku].iloc[0]
        days = st.slider("Projection horizon (days)", 14, 90, 45)
        p = core.projection(r, days)
        with st.container(border=True):
            st.markdown(f'<div class="card-title">{sku}: projected stock at {r["Avg Daily Sales"]:.1f} units/day</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_scatter(x=p["Day"], y=p["Projected Stock"], mode="lines", name="Projected stock", line=dict(color=BLUE, width=3), fill="tozeroy", fillcolor="rgba(47,107,255,.15)")
            fig.add_hline(y=r["Reorder Level"], line=dict(color=RED, dash="dash"), annotation_text="Reorder level")
            fig.add_vline(x=r["Lead Time"], line=dict(color=AMBER, dash="dot"), annotation_text=f"Supplier lead time ({r['Lead Time']}d)")
            fig.update_xaxes(title="Days from today"); fig.update_yaxes(title="Units")
            st.plotly_chart(style_fig(fig, 360, False), use_container_width=True, config={"displayModeBar": False})
            cross = p[p["Projected Stock"] <= r["Reorder Level"]]
            st.caption(f"Projected to hit the reorder level on day {int(cross['Day'].iloc[0])}." if len(cross) else "Stays above the reorder level in this window.")
        log = core.load_log(); log = log[log["SKU"] == sku]
        if len(log):
            with st.container(border=True):
                st.markdown('<div class="card-title">Recorded stock history (from the activity log)</div>', unsafe_allow_html=True)
                fig = px.line(log, x="Timestamp", y="New Stock", markers=True, color_discrete_sequence=[GREEN])
                st.plotly_chart(style_fig(fig, 260, False), use_container_width=True, config={"displayModeBar": False})


# ------------------------------------------------------------------ REPORTS
def page_reports():
    header("Reports & Export", "Export exactly what you see, with the sidebar filters applied.")
    if view.empty: return no_data()
    k = core.kpis(view)
    c = st.columns(4)
    kpi_card(c[0], "📦", BLUE, "Records", k["products"], "in this export")
    kpi_card(c[1], "🚨", RED, "Alerts", k["reorder"] + k["low"], f"{k['critical']} critical")
    kpi_card(c[2], "₹", PURPLE, "Inventory value", INR(k["value"]), "")
    kpi_card(c[3], "🛒", AMBER, "Reorder cost", INR(k["reorder_cost"]), "")
    st.write("")
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    with st.container(border=True):
        st.markdown('<div class="card-title">Download</div>', unsafe_allow_html=True)
        a, b, c3 = st.columns(3)
        a.download_button("⬇️ Full report (Excel)", core.to_excel_bytes(view), f"inventory_report_{stamp}.xlsx",
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
        cols = [c_ for c_ in view.columns if c_ not in ("Score",)]
        b.download_button("⬇️ Inventory (CSV)", view[cols].to_csv(index=False), f"inventory_{stamp}.csv", "text/csv", use_container_width=True)
        c3.download_button("⬇️ Alerts only (CSV)", core.alerts_only(view)[cols].to_csv(index=False), f"alerts_{stamp}.csv", "text/csv", use_container_width=True)
        st.caption("The Excel report contains Summary, Inventory, Alerts and Purchase_Orders sheets with colour-coded status.")
    with st.container(border=True):
        st.markdown('<div class="card-title">Preview</div>', unsafe_allow_html=True)
        inventory_table(view, 400)


# ----------------------------------------------------------------- SETTINGS
def page_settings():
    header("Settings", "Tune alert sensitivity. Everything recalculates immediately.")
    with st.container(border=True):
        with st.form("settings"):
            name = st.text_input("Display name", settings["user_name"])
            buf = st.slider("Low stock buffer (%)", 5, 100, int(settings["low_stock_buffer"] * 100), 5,
                            help="Items above the reorder level but within this % of it are LOW STOCK.")
            mult = st.slider("Order-up-to multiple (x reorder level)", 1.0, 6.0, float(settings["order_up_to_multiple"]), 0.5,
                             help="Suggested order quantity = reorder level x multiple - current stock.")
            if st.form_submit_button("Save settings", type="primary"):
                core.save_settings({"low_stock_buffer": buf / 100, "order_up_to_multiple": mult, "user_name": name})
                st.success("Settings saved."); st.rerun()
    with st.container(border=True):
        st.markdown('<div class="card-title">Alert rules</div>', unsafe_allow_html=True)
        st.markdown(f"- **REORDER NOW**: stock <= reorder level\n- **LOW STOCK**: up to **{settings['low_stock_buffer']:.0%}** above reorder level\n"
                    "- **IN STOCK**: otherwise\n- **CRITICAL**: days of cover < supplier lead time")
    with st.expander("⚠️ Reset all data to the original Excel dataset"):
        ok = st.checkbox("I understand this erases my changes and activity log")
        if st.button("Reset data", disabled=not ok):
            core.reset_to_seed(); st.success("Data reset."); st.rerun()


{"Dashboard": page_dashboard, "Inventory": page_inventory, "Alerts": page_alerts, "Suppliers": page_suppliers,
 "Analytics": page_analytics, "Reports": page_reports, "Settings": page_settings}[page]()
