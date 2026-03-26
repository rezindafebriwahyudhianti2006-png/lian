import streamlit as st
import pandas as pd
import random

# --- CONFIG ---
st.set_page_config(page_title="WorkMatch Big Data", page_icon="📊", layout="wide")

# --- GENERATE DATA BANYAK (Otomatis) ---
@st.cache_data # Supaya data tidak berubah-ubah setiap kali klik tombol
def generate_fake_db(n=50):
    nama_depan = ["Andi", "Budi", "Siti", "Dewi", "Eko", "Rina", "Rizky", "Santi", "Fauzan", "Amelia"]
    nama_belakang = ["Pratama", "Santoso", "Aminah", "Sartika", "Saputra", "Amelia", "Fauzi", "Wijaya", "Hidayat", "Putri"]
    skills_pool = [
        "Python, SQL, Tableau", "React, Javascript, CSS", "Guru Matematika, Statistik", 
        "UI/UX, Figma, Adobe", "Digital Marketing, SEO", "Project Manager, Agile",
        "Python, Machine Learning, AI", "Sales, Komunikasi, Nego", "Guru Fisika, Robotik"
    ]
    lokasi_pool = ["Jakarta", "Surabaya", "Bandung", "Jogja", "Medan", "Semarang"]
    status_pool = ["Online", "Offline"]
    last_seen_pool = ["5 mins ago", "1 hour ago", "3 hours ago", "Yesterday", "2 days ago"]

    db = []
    for i in range(n):
        status = random.choice(status_pool)
        db.append({
            "id": i + 1,
            "nama": f"{random.choice(nama_depan)} {random.choice(nama_belakang)}",
            "skill": random.choice(skills_pool),
            "lokasi": random.choice(lokasi_pool),
            "gaji": random.randint(5, 25) * 1000000,
            "status": status,
            "last_seen": "Now" if status == "Online" else random.choice(last_seen_pool),
            "wa": f"628{random.randint(100000000, 999999999)}"
        })
    return db

# Load Data
if 'db_talent' not in st.session_state:
    st.session_state.db_talent = generate_fake_db(50)

df_all = pd.DataFrame(st.session_state.db_talent)

# --- UI HEADER ---
st.title("📊 WorkMatch: Big Data Talent Pool")
st.write(f"Menampilkan **{len(df_all)}** kandidat terdaftar di sistem.")

# --- DASHBOARD RINGKASAN ---
c1, c2, c3 = st.columns(3)
c1.metric("Total Talent", len(df_all))
c2.metric("🟢 Sedang Online", len(df_all[df_all['status'] == "Online"]))
c3.metric("⚪ Sedang Offline", len(df_all[df_all['status'] == "Offline"]))

st.divider()

# --- SIDEBAR FILTER ---
with st.sidebar:
    st.header("🔍 Pencarian Canggih")
    search_query = st.text_input("Cari Skill/Nama:", "")
    filter_lokasi = st.multiselect("Lokasi:", df_all['lokasi'].unique(), default=df_all['lokasi'].unique())
    only_online = st.checkbox("Hanya yang sedang Online")
    st.divider()
    if st.button("🔄 Refresh/Acak Data Baru"):
        st.session_state.db_talent = generate_fake_db(50)
        st.rerun()

# --- LOGIKA MATCHING & FILTERING ---
df_filtered = df_all.copy()

# Filter Skill
if search_query:
    df_filtered = df_filtered[
        df_filtered['skill'].str.contains(search_query, case=False) | 
        df_filtered['nama'].str.contains(search_query, case=False)
    ]

# Filter Lokasi & Online
df_filtered = df_filtered[df_filtered['lokasi'].isin(filter_lokasi)]
if only_online:
    df_filtered = df_filtered[df_filtered['status'] == "Online"]

# Sorting: Online selalu di atas
df_filtered['sort_idx'] = df_filtered['status'].apply(lambda x: 0 if x == "Online" else 1)
df_filtered = df_filtered.sort_values(by=['sort_idx', 'nama']).drop(columns=['sort_idx'])

# --- DISPLAY KANDIDAT ---
if not df_filtered.empty:
    st.subheader(f"Ditemukan {len(df_filtered)} Kandidat yang Cocok")
    
    # Tampilan Grid (2 Kolom)
    grid_cols = st.columns(2)
    for i, (idx, row) in enumerate(df_filtered.iterrows()):
        with grid_cols[i % 2]:
            with st.container(border=True):
                c_status, c_info, c_action = st.columns([1, 4, 2])
                
                with c_status:
                    st.markdown(f"### {'🟢' if row['status'] == 'Online' else '⚪'}")
                
                with c_info:
                    st.markdown(f"**{row['nama']}**")
                    st.caption(f"📍 {row['lokasi']} | 💰 Rp{row['gaji']:,}")
                    st.write(f"Skills: `{row['skill']}`")
                    if row['status'] == "Offline":
                        st.caption(f"Last seen: {row['last_seen']}")
                
                with c_action:
                    wa_link = f"https://wa.me/{row['wa']}?text=Halo%20{row['nama']}"
                    st.link_button("Chat", wa_link, use_container_width=True, type="primary" if row['status'] == "Online" else "secondary")
else:
    st.warning("Tidak ada kandidat yang cocok dengan kriteria filter Anda.")