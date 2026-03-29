import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode, DataReturnMode

# 1. Configurare Pagină
st.set_page_config(page_title="Water License Portal", page_icon="💧", layout="wide")

# 2. Design-ul tău preferat (Reinstaurat)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    #MainMenu, footer, header {visibility: hidden;}
    .detail-card { 
        background-color: white; padding: 25px; border-radius: 12px; 
        border: 2px solid #1E3A8A; box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)


# 3. Încărcare Date
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("water-licence-attributes.csv", sep=None, engine='python', encoding='cp1252',
                         on_bad_lines='skip')
        return df.fillna('N/A').astype(str)
    except:
        return pd.DataFrame()


df = load_data()

# --- INTERFAȚA ---
st.title("💧 Water License Search Portal")

# 4. Cele 3 Căutări (Inclusiv WaterName/Type)
c1, c2, c3 = st.columns(3)
with c1: s_name = st.text_input("👤 Legal Name:", placeholder="Search...")
with c2: s_auth = st.text_input("🔢 Authorization No:", placeholder="Search...")
with c3: s_water = st.text_input("🌊 Water Name/Type:", placeholder="Search...")

# Logica de filtrare
d_show = df.copy()

if s_name:
    col = next((c for c in df.columns if 'legal' in c.lower()), df.columns[1])
    d_show = d_show[d_show[col].str.contains(s_name, case=False, na=False)]
if s_auth:
    col = next((c for c in df.columns if 'auth' in c.lower() or 'number' in c.lower()), df.columns[0])
    d_show = d_show[d_show[col].str.contains(s_auth, case=False, na=False)]
if s_water:
    target_col = "WaterName/Type" if "WaterName/Type" in df.columns else next(
        (c for c in df.columns if 'water' in c.lower()), None)
    if target_col:
        d_show = d_show[d_show[target_col].str.contains(s_water, case=False, na=False)]
    else:
        d_show = d_show[d_show.apply(lambda r: r.str.contains(s_water, case=False).any(), axis=1)]

# Limitare preview
if not (s_name or s_auth or s_water):
    d_show = d_show.head(100)

# --- 5. TABELUL (Metoda Stabilă) ---
if d_show.empty:
    st.warning("⚠️ No results found.")
else:
    manual_options = {
        "columnDefs": [{"field": i, "headerName": i} for i in d_show.columns],
        "defaultColDef": {"resizable": True, "sortable": True, "filter": True, "minWidth": 200},
        "rowSelection": "single",
        "pagination": True,
        "paginationPageSize": 10
    }

    response = AgGrid(
        d_show,
        gridOptions=manual_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        theme='alpine',
        height=450,
        fit_columns_on_grid_load=False
    )

    # --- 6. PARTEA DE JOS (Pop-up/Detail Card + Export) ---
    sel = response.get('selected_rows')
    row = None
    if isinstance(sel, pd.DataFrame) and not sel.empty:
        row = sel.iloc[0].to_dict()
    elif isinstance(sel, list) and len(sel) > 0:
        row = sel[0]

    if row:
        st.markdown("---")
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        st.subheader("📋 Complete Record Details")

        cols = st.columns(3)
        clean_items = {k: v for k, v in row.items() if not str(k).startswith('_')}

        for i, (k, v) in enumerate(clean_items.items()):
            cols[i % 3].markdown(f"**{k}**")
            cols[i % 3].info(str(v))
        st.markdown('</div>', unsafe_allow_html=True)

        # Export rând selectat
        csv_single = pd.DataFrame([clean_items]).to_csv(index=False).encode('utf-8')
