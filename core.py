"""Business logic for InventoryPro - no Streamlit imports so it can be tested on its own."""
from __future__ import annotations

import io
import json
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
INV_FILE = DATA_DIR / "inventory.csv"
SUP_FILE = DATA_DIR / "suppliers.csv"
LOG_FILE = DATA_DIR / "stock_log.csv"
SET_FILE = DATA_DIR / "settings.json"

INV_COLS = ["Store ID", "Product ID", "Category", "Region", "Current Stock",
            "Reorder Level", "Unit Price", "Avg Daily Sales", "Last Updated"]
SUP_COLS = ["Supplier ID", "Supplier Name", "Category", "Lead Time (Days)",
            "Reliability (%)", "City", "Contact"]
DEFAULT_SETTINGS = {"low_stock_buffer": 0.25, "order_up_to_multiple": 3.0,
                    "user_name": "Sanjai R"}

STATUS_ORDER = ["REORDER NOW", "LOW STOCK", "IN STOCK"]
PRIORITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "-"]
COLORS = {"REORDER NOW": "#F0475B", "LOW STOCK": "#F5B301", "IN STOCK": "#12B886"}


# ----------------------------------------------------------------- settings
def load_settings() -> dict:
    s = dict(DEFAULT_SETTINGS)
    if SET_FILE.exists():
        try:
            s.update(json.loads(SET_FILE.read_text()))
        except Exception:
            pass
    return s


def save_settings(s: dict) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    SET_FILE.write_text(json.dumps(s, indent=2))


# --------------------------------------------------------------- data files
def load_inventory() -> pd.DataFrame:
    df = pd.read_csv(INV_FILE)
    for c in INV_COLS:
        if c not in df.columns:
            df[c] = np.nan
    df = df[INV_COLS].copy()
    for c in ["Current Stock", "Reorder Level"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    for c in ["Unit Price", "Avg Daily Sales"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    return df


def save_inventory(df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    df[INV_COLS].to_csv(INV_FILE, index=False)


def load_suppliers() -> pd.DataFrame:
    return pd.read_csv(SUP_FILE)[SUP_COLS]


def save_suppliers(df: pd.DataFrame) -> None:
    df[SUP_COLS].to_csv(SUP_FILE, index=False)


def reset_to_seed() -> None:
    pd.read_csv(DATA_DIR / "seed_inventory.csv").to_csv(INV_FILE, index=False)
    pd.read_csv(DATA_DIR / "seed_suppliers.csv").to_csv(SUP_FILE, index=False)
    if LOG_FILE.exists():
        LOG_FILE.unlink()


def log_change(sku: str, action: str, old, new, note: str = "") -> None:
    row = pd.DataFrame([{"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         "SKU": sku, "Action": action, "Old Stock": old,
                         "New Stock": new, "Note": note}])
    row.to_csv(LOG_FILE, mode="a", header=not LOG_FILE.exists(), index=False)


def load_log() -> pd.DataFrame:
    if LOG_FILE.exists():
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame(columns=["Timestamp", "SKU", "Action", "Old Stock", "New Stock", "Note"])


# ------------------------------------------------------------- calculations
def enrich(inv: pd.DataFrame, sup: pd.DataFrame, settings: dict) -> pd.DataFrame:
    """Python version of every Excel formula in the workbook."""
    d = inv.copy().reset_index(drop=True)
    buf = float(settings["low_stock_buffer"])
    mult = float(settings["order_up_to_multiple"])
    d["SKU"] = d["Store ID"].astype(str) + "-" + d["Product ID"].astype(str)
    stock, rl = d["Current Stock"], d["Reorder Level"]

    d["Status"] = np.select([stock <= rl, stock <= rl * (1 + buf)],
                            ["REORDER NOW", "LOW STOCK"], "IN STOCK")

    sup_idx = sup.drop_duplicates("Category").set_index("Category")
    d["Supplier"] = d["Category"].map(sup_idx["Supplier Name"]).fillna("Unassigned")
    d["Lead Time"] = d["Category"].map(sup_idx["Lead Time (Days)"]).fillna(0).astype(int)

    ads = d["Avg Daily Sales"]
    d["Days of Cover"] = np.where(ads > 0, (stock / ads.replace(0, np.nan)).round(1), np.nan)
    alert = d["Status"] != "IN STOCK"
    critical = alert & d["Days of Cover"].lt(d["Lead Time"])
    d["Priority"] = np.select([~alert, critical, d["Status"] == "REORDER NOW"],
                              ["-", "CRITICAL", "HIGH"], "MEDIUM")

    d["Suggested Qty"] = np.where(alert, np.maximum(0, np.ceil(rl * mult) - stock), 0).astype(int)
    d["Stock Value"] = stock * d["Unit Price"]
    d["Reorder Cost"] = d["Suggested Qty"] * d["Unit Price"]
    today = pd.Timestamp(date.today())
    d["Expected Delivery"] = np.where(alert, (today + pd.to_timedelta(d["Lead Time"], unit="D")).dt.strftime("%d-%b-%Y"), "")
    d["Action"] = d["Priority"].map({"CRITICAL": "Order immediately - stock-out before delivery",
                                     "HIGH": "Raise purchase order today",
                                     "MEDIUM": "Plan reorder this week",
                                     "-": "No action required"})
    tier = d["Priority"].map({"CRITICAL": 30, "HIGH": 20, "MEDIUM": 10, "-": 0})
    short = np.where(rl > 0, (rl - stock) / rl.replace(0, np.nan), 0)
    d["Score"] = np.where(alert, tier + np.nan_to_num(short) + d.index / 1e7, 0.0)
    d["Alert Rank"] = np.where(alert, d["Score"].rank(ascending=False, method="first"), np.nan)
    return d


def kpis(d: pd.DataFrame) -> dict:
    n = len(d)
    rn = int((d["Status"] == "REORDER NOW").sum())
    ls = int((d["Status"] == "LOW STOCK").sum())
    ins = int((d["Status"] == "IN STOCK").sum())
    return {"products": n, "units": int(d["Current Stock"].sum()), "reorder": rn,
            "low": ls, "in_stock": ins, "value": float(d["Stock Value"].sum()),
            "reorder_cost": float(d["Reorder Cost"].sum()),
            "critical": int((d["Priority"] == "CRITICAL").sum()),
            "health": (ins / n) if n else 0.0}


def alerts_only(d: pd.DataFrame) -> pd.DataFrame:
    return d[d["Status"] != "IN STOCK"].sort_values("Alert Rank")


def purchase_orders(d: pd.DataFrame) -> pd.DataFrame:
    a = alerts_only(d)
    if a.empty:
        return pd.DataFrame(columns=["Supplier", "Items", "Units", "Cost", "Lead Time"])
    g = a.groupby("Supplier").agg(Items=("SKU", "count"), Units=("Suggested Qty", "sum"),
                                  Cost=("Reorder Cost", "sum"), Lead_Time=("Lead Time", "max")).reset_index()
    g = g.rename(columns={"Lead_Time": "Lead Time"})
    return g.sort_values("Cost", ascending=False)


def projection(row: pd.Series, days: int = 45) -> pd.DataFrame:
    x = np.arange(0, days + 1)
    stock = np.maximum(0, row["Current Stock"] - row["Avg Daily Sales"] * x)
    return pd.DataFrame({"Day": x, "Projected Stock": stock})


# ------------------------------------------------------------------ exports
def to_excel_bytes(d: pd.DataFrame) -> bytes:
    cols = ["SKU", "Store ID", "Product ID", "Category", "Region", "Current Stock",
            "Reorder Level", "Unit Price", "Status", "Priority", "Days of Cover",
            "Supplier", "Lead Time", "Suggested Qty", "Stock Value", "Reorder Cost",
            "Expected Delivery", "Action"]
    out = io.BytesIO()
    k = kpis(d)
    with pd.ExcelWriter(out, engine="xlsxwriter") as xw:
        wb = xw.book
        hdr = wb.add_format({"bold": True, "font_color": "white", "bg_color": "#17365D",
                             "align": "center", "valign": "vcenter", "border": 1})
        money = wb.add_format({"num_format": "₹#,##0"})
        price = wb.add_format({"num_format": "₹#,##0.00"})
        red = wb.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006", "bold": True})
        amb = wb.add_format({"bg_color": "#FFEB9C", "font_color": "#9C5700", "bold": True})
        grn = wb.add_format({"bg_color": "#C6EFCE", "font_color": "#006100", "bold": True})
        title = wb.add_format({"bold": True, "font_size": 16, "font_color": "#17365D"})
        lab = wb.add_format({"bold": True, "border": 1, "bg_color": "#DCE6F1"})
        val = wb.add_format({"border": 1})
        valm = wb.add_format({"border": 1, "num_format": "₹#,##0"})

        def sheet(df, name):
            df = df[cols] if set(cols) <= set(df.columns) else df
            df.to_excel(xw, sheet_name=name, index=False, startrow=0)
            ws = xw.sheets[name]
            for i, c in enumerate(df.columns):
                ws.write(0, i, c, hdr)
                w = max(12, min(44, int(df[c].astype(str).str.len().max() if len(df) else 10) + 3))
                fmt = money if c in ("Stock Value", "Reorder Cost") else price if c == "Unit Price" else None
                ws.set_column(i, i, w, fmt)
            ws.freeze_panes(1, 1)
            ws.set_row(0, 24)
            ws.autofilter(0, 0, max(len(df), 1), len(df.columns) - 1)
            n = max(len(df), 1)
            for c in ("Status",):
                if c in df.columns:
                    j = list(df.columns).index(c)
                    for txt, f in (("REORDER NOW", red), ("LOW STOCK", amb), ("IN STOCK", grn)):
                        ws.conditional_format(1, j, n, j, {"type": "cell", "criteria": "==",
                                                          "value": f'"{txt}"', "format": f})

        s = xw.book.add_worksheet("Summary")
        xw.sheets["Summary"] = s
        s.write("A1", "Inventory Stock Alert - Summary", title)
        s.write("A2", f"Generated {datetime.now():%d-%b-%Y %H:%M}   |   Records in this export: {len(d)}")
        rows = [("Total products", k["products"], val), ("Total stock units", k["units"], val),
                ("REORDER NOW", k["reorder"], val), ("LOW STOCK", k["low"], val),
                ("IN STOCK", k["in_stock"], val), ("Critical alerts", k["critical"], val),
                ("Inventory value", k["value"], valm), ("Estimated reorder cost", k["reorder_cost"], valm)]
        for i, (a, b, f) in enumerate(rows):
            s.write(3 + i, 0, a, lab); s.write(3 + i, 1, b, f)
        s.set_column(0, 0, 28); s.set_column(1, 1, 18)
        sheet(d, "Inventory")
        sheet(alerts_only(d), "Alerts")
        po = purchase_orders(d)
        po.to_excel(xw, sheet_name="Purchase_Orders", index=False)
        ws = xw.sheets["Purchase_Orders"]
        for i, c in enumerate(po.columns):
            ws.write(0, i, c, hdr); ws.set_column(i, i, 22, money if c == "Cost" else None)
    return out.getvalue()
