# InventoryPro - Smart Stock Management

Streamlit web app built on the Inventory Stock Alert System Excel project.
Stack: Python, Streamlit, Pandas, Plotly, Excel/CSV export (xlsxwriter).

## Run locally
```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```
Opens at http://localhost:8501

## Features
- Dashboard: KPI cards, status donut, Top 5 low stock, recent alerts, category/store/cost charts, inventory table
- Smart alerts: REORDER NOW / LOW STOCK / IN STOCK, CRITICAL (days of cover < supplier lead time), draft purchase orders
- Sidebar filters + search (store, category, region, status) applied to every page
- Inventory management: add product, update stock (received / sold / set count), edit, delete, CSV/Excel import, activity log
- Analytics: category charts, heatmap, reorder cost analysis, stock projection vs reorder level and lead time
- Reports: filtered export to Excel (Summary, Inventory, Alerts, Purchase_Orders) and CSV
- Settings: low-stock buffer %, order-up-to multiple, reset to original data

## Files
- `app.py` UI | `core.py` calculations (same logic as the Excel formulas) | `data/` CSV data + original Excel
- `data/inventory.csv` and `data/suppliers.csv` are the live data; `seed_*.csv` is the original copy used by Reset.

## Deploy as a public website
**Streamlit Community Cloud (free, easiest)**
1. Push this folder to a GitHub repo.
2. Go to share.streamlit.io, sign in with GitHub, click New app, pick the repo, main file `app.py`, Deploy.
3. You get a public URL like `https://your-app.streamlit.app`.

**Docker (any cloud: Render, Railway, Azure, AWS)**
```bash
docker build -t inventorypro .
docker run -p 8501:8501 inventorypro
```

**Important:** on free cloud hosting the file system is temporary, so edits made in the app (add/update stock) are lost when the app restarts.
For permanent multi-user data, move storage from CSV to a database (SQLite on a persistent disk, or Postgres/Supabase). Only `load_*`/`save_*` in `core.py` need to change.
Add login (e.g. `streamlit-authenticator`) before sharing a public link, since anyone with the URL can edit stock.
