import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

# 1. Configurare Pagină
st.set_page_config(page_title="Water License Portal", page_icon="💧", layout="wide")

# 2. Design Personalizat (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    #MainMenu, footer, header {visibility: hidden;}
    .detail-card { 
        background-color: white; padding: 25px; border-radius: 12px; 
        border: 2px solid #1E3A8A; box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
    }
    .stInfo { border-radius: 8px; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)


# 3. Încărcare Date
@st.cache_data
def load_data():
    file_name = "water-licence-attributes.csv"
    for enc in ['utf-8', 'cp1252', 'latin1', 'iso-8859-1']:
        try:
            df = pd.read_csv(file_name, sep=None, engine='python', encoding=enc, on_bad_lines='skip')
            return df.fillna('N/A').astype(str)
        except:
            continue
    return pd.DataFrame()


df = load_data()

# --- INTERFAȚA ---
st.title("💧 Water License Search Portal")

# 4. CĂUTARE TRIPLA (Configurată pentru WaterName/Type)
c1, c2, c3 = st.columns(3)

with c1:
    search_name = st.text_input("👤 Legal Name:", placeholder="Search name...")
with c2:
    search_auth = st.text_input("🔢 Authorization No:", placeholder="Search ID...")
with c3:
    search_water = st.text_input("🌊 Water Name/Type:", placeholder="Search water source...")

# LOGICA DE FILTRARE
data_to_show = df.copy()


# Funcție pentru a găsi coloana corectă chiar dacă are caractere speciale
def get_exact_col(target):
    for col in df.columns:
        if target.lower().replace(" ", "") in col.lower().replace(" ", ""):
            return col
    return None


if search_name:
    col = get_exact_col('legalname') or df.columns[1]
    data_to_show = data_to_show[data_to_show[col].str.contains(search_name, case=False, na=False)]

if search_auth:
    col = get_exact_col('authorizationnumber') or df.columns[0]
    data_to_show = data_to_show[data_to_show[col].str.contains(search_auth, case=False, na=False)]

if search_water:
    # Căutăm exact coloana indicată de tine: WaterName/Type
    target_col = "WaterName/Type" if "WaterName/Type" in df.columns else get_exact_col('watername')

    if target_col:
        data_to_show = data_to_show[data_to_show[target_col].str.contains(search_water, case=False, na=False)]
    else:
        # Fallback dacă coloana nu e găsită exact
        mask = data_to_show.apply(lambda row: row.str.contains(search_water, case=False, na=False).any(), axis=1)
        data_to_show = data_to_show[mask]

# Previzualizare limitată
if not (search_name or search_auth or search_water):
    data_to_show = df.head(100)

# 5. AG-GRID (Tabelul)
gb = GridOptionsBuilder.from_dataframe(data_to_show)
gb.configure_default_column(resizable=True, filterable=True, sortable=True, minWidth=200)
gb.configure_selection('single', use_checkbox=True)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
grid_options = gb.build()

grid_response = AgGrid(
    data_to_show,
    gridOptions=grid_options,
    fit_columns_on_grid_load=False,
    theme='alpine',
    height=450,
    update_mode=GridUpdateMode.SELECTION_CHANGED
)

# 6. AFIȘARE DETALII
selected_rows = grid_response.get('selected_rows', [])
row_dict = None

if isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
    row_dict = selected_rows.iloc[0].to_dict()
elif isinstance(selected_rows, list) and len(selected_rows) > 0:
    row_dict = selected_rows[0]

if row_dict:
    st.markdown("---")
    st.markdown('<div class="detail-card">', unsafe_allow_html=True)
    st.subheader("📋 Complete Record Details")
    cols = st.columns(3)
    clean_items = {k: v for k, v in row_dict.items() if not str(k).startswith('_')}
    for i, (k, v) in enumerate(clean_items.items()):
        cols[i % 3].markdown(f"**{k}**")
        cols[i % 3].info(str(v))
    st.markdown('</div>', unsafe_allow_html=True)
