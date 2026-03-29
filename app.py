import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

# 1. Page Config
st.set_page_config(page_title="Water License Portal", page_icon="💧", layout="wide")

# 2. Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    #MainMenu, footer, header {visibility: hidden;}
    .detail-card { 
        background-color: white; 
        padding: 25px; 
        border-radius: 12px; 
        border: 2px solid #1E3A8A; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        margin-top: 20px;
    }
    .stInfo { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)


# 3. Data Loading (Handles the 17.2 MB file and 0x97 encoding error)
@st.cache_data
def load_data():
    file_name = "water-licence-attributes.csv"
    for enc in ['utf-8', 'cp1252', 'latin1', 'iso-8859-1']:
        try:
            df = pd.read_csv(file_name, sep=None, engine='python', encoding=enc, on_bad_lines='skip')
            # Clean empty values
            return df.fillna('N/A').astype(str)
        except:
            continue
    return pd.DataFrame()


df = load_data()

# --- THE INTERFACE ---
st.title("💧 Water License Search Portal")
st.write("Search by specific fields below. **Click a row or checkbox** to see full technical details.")

# 4. TARGETED SEARCH (Faster and more accurate)
# We create two side-by-side search boxes
col1, col2 = st.columns(2)

with col1:
    search_name = st.text_input("👤 Search by Legal Name:", placeholder="Enter client/company name...")

with col2:
    search_auth = st.text_input("🔢 Search by Authorization Number:", placeholder="Enter license/auth number...")

# Filtering Logic
filtered_df = df.copy()

if search_name:
    # We look for the closest column name in case of typos in the CSV header
    name_col = 'Legal Name' if 'Legal Name' in df.columns else df.columns[1]
    filtered_df = filtered_df[filtered_df[name_col].str.contains(search_name, case=False, na=False)]

if search_auth:
    # We look for the authorization column
    auth_col = 'Authorization Number' if 'Authorization Number' in df.columns else df.columns[0]
    filtered_df = filtered_df[filtered_df[auth_col].str.contains(search_auth, case=False, na=False)]

# If no search is performed, show only first 100 rows for performance
if not search_name and not search_auth:
    data_to_show = df.head(100)
else:
    data_to_show = filtered_df

# 5. AG-GRID CONFIGURATION (Fixes the "squashed" table look)
gb = GridOptionsBuilder.from_dataframe(data_to_show)
gb.configure_default_column(
    resizable=True,
    filterable=True,
    sortable=True,
    minWidth=200  # Forces columns to be wider
)
gb.configure_selection('single', use_checkbox=True)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
grid_options = gb.build()

# Display interactive table with horizontal scroll enabled
grid_response = AgGrid(
    data_to_show,
    gridOptions=grid_options,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=False,  # Essential for the horizontal scroll
    theme='alpine',
    height=450,
    allow_unsafe_jscode=True
)

# 6. SHOW DETAILS ON CLICK (Fixes the Ambiguity Error)
selected_data = grid_response['selected_rows']

if selected_data is not None and len(selected_data) > 0:
    # Handle different AgGrid return formats
    if isinstance(selected_data, pd.DataFrame):
        row_dict = selected_data.iloc[0].to_dict()
    else:
        row_dict = selected_data[0]

    st.markdown("---")
    st.markdown('<div class="detail-card">', unsafe_allow_html=True)
    st.subheader(f"📋 Complete Technical Record")

    cols = st.columns(3)
    # Clean internal AgGrid columns
    clean_display = {k: v for k, v in row_dict.items() if not str(k).startswith('_')}

    for i, (col_name, val) in enumerate(clean_display.items()):
        current_col = cols[i % 3]
        current_col.markdown(f"**{col_name}**")
        current_col.info(str(val))
    st.markdown('</div>', unsafe_allow_html=True)

    # Individual CSV Export
    csv_single = pd.DataFrame([clean_display]).to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Selected Record", csv_single, "record_details.csv", "text/csv")

elif not search_name and not search_auth:
    st.info("💡 **Instructions:** Use the search boxes above. Click on a row to reveal full details.")

# 7. Global Export
if not data_to_show.empty:
    st.markdown("---")
    full_csv = data_to_show.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download All Results (CSV)", full_csv, "search_results.csv", "text/csv")