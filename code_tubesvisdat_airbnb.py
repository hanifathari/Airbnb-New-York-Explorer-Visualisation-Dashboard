import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Airbnb Hotel US Explorer Dashboard", page_icon="🏙️")

@st.cache_data
def load_data():
    df = pd.read_csv("Airbnb_Open_Data.csv", low_memory=False)
    # Penyesuaian nama kolom agar standar
    df = df.rename(columns={'lat': 'latitude', 'long': 'longitude', 'room type': 'room_type'})
    
    # Cleaning Price
    df['price'] = df['price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    # Hapus data kosong di kolom kritikal
    df = df.dropna(subset=['latitude', 'longitude', 'price', 'neighbourhood group', 'room_type'])
    return df

data = load_data()

st.title("🏙️ Airbnb Hotel and Homestay Explorer (New York - United States)")
st.markdown("The primary objective of this dashboard is to develop an interactive data visualization infographic that enables users to explore the United States Airbnb dataset, " \
"specifically focusing on New York, in an intuitive and efficient manner. " \
"This visualization is designed to assist prospective travelers and property analysts in filtering over 100,000 rows of data through dynamic queries such as price range, " \
"geographical regions, and room types. " \
"By utilizing this dashboard, the decision-making process for selecting accommodations becomes more transparent and data-driven, " \
"allowing users to quickly identify the most strategic locations that align with their specific budgets and needs")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Pilih Filter Data")

# 1. Filter Wilayah (Neighbourhood Group)
wilayah_list = data['neighbourhood group'].unique().tolist()
selected_wilayah = st.sidebar.multiselect("Pilih Wilayah", wilayah_list, default=wilayah_list)

# 2. Filter Tipe Kamar (Room Type)
room_list = data['room_type'].unique().tolist()
selected_room = st.sidebar.multiselect("Pilih Tipe Kamar", room_list, default=room_list)

# 3. Filter Harga (Slider)
max_p = int(data['price'].max())
selected_price = st.sidebar.slider("Rentang Harga ($)", 0, max_p, (0, 500))

# --- PROSES FILTER DATA ---
filtered = data[
    (data['neighbourhood group'].isin(selected_wilayah)) &
    (data['room_type'].isin(selected_room)) &
    (data['price'] >= selected_price[0]) &
    (data['price'] <= selected_price[1])
]

# --- DASHBOARD ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Peta Sebaran")
    if not filtered.empty:
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=filtered['latitude'].mean(), 
                longitude=filtered['longitude'].mean(), 
                zoom=10,
                pitch=45
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=filtered,
                    get_position='[longitude, latitude]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=150,
                    pickable=True, # Details-on-demand 
                ),
            ],
            tooltip={"text": "Nama: {NAME}\nHarga: ${price}\nWilayah: {neighbourhood}"}
        ))
    else:
        st.warning("Data tidak ditemukan untuk kombinasi filter tersebut.")

with col2:
    st.subheader("Statistik Ringkas")
    st.metric("Total Properti", len(filtered))
    st.metric("Rata-rata Harga", f"${int(filtered['price'].mean()) if not filtered.empty else 0}")
    
    # Menambahkan grafik bar untuk kualitas desain 
    if not filtered.empty:
        st.write("Distribusi Tipe Kamar:")
        st.bar_chart(filtered['room_type'].value_counts())

# Tabel data untuk "Details-on-demand" 
with st.expander("Lihat Detail Tabel Data"):
    st.dataframe(filtered[['NAME', 'neighbourhood group', 'room_type', 'price', 'review rate number']].head(100))

# Narrative and conclusion

st.markdown("""
### Key Insights
- Penmilahan Lokasi & Harga 
- Ketersediaan Tipe Kamar
- Transparansi Kualitas (Details-on-demand)
- Tren Harga yang Terfilter
""")

st.markdown("---")
st.markdown("**Final Project – Interactive Visualization (Visualisasi Data Lanjut)**")
st.markdown("Syafreza Hanif Athari - 203012420031")
st.markdown("Nadya Cantika Putri Abdun - 203012410015")